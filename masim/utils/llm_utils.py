"""Shared LLM response parsing helpers for masim simulations.

Provides canonical parsers for the ``<analysis>`` + ``<decision>`` output
format used by LLM-based agent variants, plus transient-error detection for
retry logic.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict


_ANALYSIS_RE = re.compile(r"<analysis>(.*?)</analysis>", re.DOTALL | re.IGNORECASE)
_DECISION_RE = re.compile(r"<decision>(.*?)</decision>", re.DOTALL | re.IGNORECASE)
_THINK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)


def is_retryable_llm_error(exc: BaseException) -> bool:
    """Return whether an LLM/API exception is plausibly transient."""
    text = f"{type(exc).__name__}: {exc}".lower()
    retryable_markers = (
        "timeout",
        "temporarily",
        "temporary",
        "rate limit",
        "ratelimit",
        "429",
        "500",
        "502",
        "503",
        "504",
        "connection",
        "overloaded",
        "try again",
    )
    return any(marker in text for marker in retryable_markers)


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extract a single JSON object from text."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("LLM decision block does not contain a JSON object")
    payload = text[start : end + 1]
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("LLM decision JSON must be an object")
    return data


def parse_llm_response_with_thinking(response_text: str) -> Dict[str, Any]:
    """Parse canonical ``<analysis>`` + ``<decision>`` LLM output.

    Parameters
    ----------
    response_text : str
        Raw LLM output containing ``<analysis>`` and ``<decision>`` XML tags.

    Returns
    -------
    dict
        Parsed decision fields (action, bid_price, quantity, reasoning) plus
        an ``analysis`` key with the reasoning text.

    Raises
    ------
    TypeError
        If *response_text* is not a string.
    ValueError
        If the ``<decision>`` block is missing or contains no JSON object.
    KeyError
        If required decision fields are absent.
    """
    if not isinstance(response_text, str):
        raise TypeError("response_text must be a string")

    decision_match = _DECISION_RE.search(response_text)
    if decision_match is None:
        raise ValueError("LLM response missing <decision>...</decision> block")

    analysis_match = _ANALYSIS_RE.search(response_text)
    analysis = ""
    if analysis_match is not None:
        analysis = analysis_match.group(1).strip()
    else:
        think_match = _THINK_RE.search(response_text)
        if think_match is not None:
            analysis = think_match.group(1).strip()

    decision = _extract_json_object(decision_match.group(1))
    for field in ("action", "bid_price", "quantity", "reasoning"):
        if field not in decision:
            raise KeyError(field)
    decision["analysis"] = analysis
    return decision


def parse_llm_quantity_response_with_thinking(response_text: str) -> Dict[str, Any]:
    """Parse quantity-style LLM output used by legacy examples."""
    parsed = parse_llm_response_with_thinking(response_text)
    if "quantity" not in parsed:
        raise KeyError("quantity")
    return parsed


# ---------------------------------------------------------------------------
# Shared decision validators (raise ValueError → robust_llm_call retries)
# ---------------------------------------------------------------------------


def validate_bid_qty_decision(decision: Dict[str, Any]) -> None:
    """Validate the standard bid+quantity decision contract.

    Contract: ``action`` ∈ {buy, sell, hold}, ``bid_price`` > 0, ``reasoning``
    non-empty.  Called from :func:`robust_llm_call` via ``validate_fn=``.
    Raises :class:`ValueError` on any contract violation so the caller triggers
    a retry (parse errors are treated the same as ``ValueError``).
    """
    if decision["action"] not in ("buy", "sell", "hold"):
        raise ValueError(f"Invalid action: {decision['action']}")
    if float(decision["bid_price"]) <= 0:
        raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
    if not str(decision["reasoning"]).strip():
        raise ValueError("Missing reasoning")


# ---------------------------------------------------------------------------
# Permanent-error detection (errors that will NEVER succeed on retry)
# ---------------------------------------------------------------------------

_PERMANENT_ERROR_MARKERS = (
    "authentication",
    "auth",
    "401",
    "403",
    "invalid api key",
    "invalid_api_key",
    "model not found",
    "model_not_found",
    "permission denied",
    "access denied",
    "billing",
    "quota exceeded",
    "insufficient_quota",
)


def _is_permanent_error(exc: BaseException) -> bool:
    """Return whether an LLM exception indicates a permanent failure."""
    text = f"{type(exc).__name__}: {exc}".lower()
    return any(marker in text for marker in _PERMANENT_ERROR_MARKERS)


# ---------------------------------------------------------------------------
# Fallback hold sentinel
# ---------------------------------------------------------------------------

_FALLBACK_HOLD: Dict[str, Any] = {
    "action": "hold",
    "quantity": 0,
    "bid_price": 0,
    "reasoning": "LLM unavailable after retries",
    "analysis": "",
    "_fallback": True,
}


# ---------------------------------------------------------------------------
# robust_llm_call — the single robust LLM call pipeline
# ---------------------------------------------------------------------------

import logging
import random
import asyncio
from typing import Callable, Optional

_logger = logging.getLogger(__name__)


def robust_llm_call(
    client,
    system_prompt: str,
    user_prompt: str,
    *,
    parse_fn: Callable[[str], Dict[str, Any]] = parse_llm_response_with_thinking,
    validate_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
    max_retries: int = 5,
    fallback: str = "hold",
    identity: str = "",
) -> Dict[str, Any]:
    """Robust LLM call with retry, backoff, error discrimination, and fallback.

    This is the single source of truth for calling an LLM in MASIM simulations.
    It handles transient errors with exponential backoff, aborts on permanent
    errors, and optionally returns a fallback hold when all retries are exhausted.

    Parameters
    ----------
    client : LangChainAPIInference
        LLM client instance with a ``.run([InferInput])`` method.
    system_prompt : str
        System prompt for the LLM.
    user_prompt : str
        User prompt (already formatted with market state variables).
    parse_fn : callable
        Function to parse raw LLM response text into a decision dict.
        Default: ``parse_llm_response_with_thinking``.
    validate_fn : callable, optional
        Additional validation on the parsed dict. Should raise ValueError
        if the decision is invalid (e.g. action not in {buy,sell,hold}).
    max_retries : int
        Maximum number of attempts (default 5).
    fallback : str
        What to do when all retries fail:
        - ``"hold"``: return a synthetic hold decision marked ``_fallback=True``
        - ``"raise"``: raise RuntimeError
    identity : str
        Agent identity for logging.

    Returns
    -------
    dict
        Parsed decision dict (action, quantity, bid_price, reasoning, analysis).
        If fallback triggered, includes ``_fallback=True``.
    """
    from lmbase.inference.base import InferInput  # type: ignore

    last_error: Optional[BaseException] = None

    for attempt in range(max_retries):
        try:
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = client.run([infer_input])
            response_text = infer_output.outputs[0].response

            # Parse
            decision = parse_fn(response_text)

            # Extra validation (e.g. action whitelist)
            if validate_fn is not None:
                validate_fn(decision)

            return decision

        except Exception as exc:  # noqa: BLE001
            last_error = exc

            # --- Permanent errors: abort immediately ---
            if _is_permanent_error(exc):
                _logger.error(
                    "[%s] Permanent LLM error (attempt %d/%d), aborting: %s",
                    identity, attempt + 1, max_retries, exc,
                )
                break

            # --- Log and decide whether to retry ---
            is_api_transient = is_retryable_llm_error(exc)
            is_parse_error = isinstance(exc, (ValueError, KeyError, TypeError))

            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = min(8.0, 0.5 * (2 ** attempt)) + random.uniform(0.0, 0.5)
                _logger.debug(
                    "[%s] LLM attempt %d/%d failed (%s: %s), retrying in %.2fs",
                    identity, attempt + 1, max_retries,
                    "transient" if is_api_transient else "parse" if is_parse_error else "unknown",
                    exc, delay,
                )
                # Use synchronous sleep (this runs inside async but is called
                # from sync context in many scenarios)
                import time
                time.sleep(delay)
            else:
                _logger.warning(
                    "[%s] LLM failed after %d attempts. Last error: %s",
                    identity, max_retries, exc,
                )

    # --- All retries exhausted or permanent error ---
    if fallback == "hold":
        _logger.warning(
            "[%s] Returning fallback hold. Last error: %s", identity, last_error,
        )
        return dict(_FALLBACK_HOLD)  # Return a copy
    else:
        raise RuntimeError(
            f"[{identity}] LLM decision unavailable after {max_retries} retries: "
            f"{last_error}"
        ) from last_error


async def robust_llm_call_async(
    client,
    system_prompt: str,
    user_prompt: str,
    *,
    parse_fn: Callable[[str], Dict[str, Any]] = parse_llm_response_with_thinking,
    validate_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
    max_retries: int = 5,
    fallback: str = "hold",
    identity: str = "",
) -> Dict[str, Any]:
    """Async version of :func:`robust_llm_call` with async sleep for backoff.

    Identical semantics, but uses ``asyncio.sleep`` instead of blocking sleep.
    Use this in async agent code (e.g. ``async def decide()``).
    """
    from lmbase.inference.base import InferInput  # type: ignore

    last_error: Optional[BaseException] = None

    for attempt in range(max_retries):
        try:
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = client.run([infer_input])
            response_text = infer_output.outputs[0].response

            decision = parse_fn(response_text)
            if validate_fn is not None:
                validate_fn(decision)
            return decision

        except Exception as exc:  # noqa: BLE001
            last_error = exc

            if _is_permanent_error(exc):
                _logger.error(
                    "[%s] Permanent LLM error (attempt %d/%d), aborting: %s",
                    identity, attempt + 1, max_retries, exc,
                )
                break

            if attempt < max_retries - 1:
                delay = min(8.0, 0.5 * (2 ** attempt)) + random.uniform(0.0, 0.5)
                _logger.debug(
                    "[%s] LLM attempt %d/%d failed, retrying in %.2fs: %s",
                    identity, attempt + 1, max_retries, delay, exc,
                )
                await asyncio.sleep(delay)
            else:
                _logger.warning(
                    "[%s] LLM failed after %d attempts. Last error: %s",
                    identity, max_retries, exc,
                )

    if fallback == "hold":
        _logger.warning(
            "[%s] Returning fallback hold. Last error: %s", identity, last_error,
        )
        return dict(_FALLBACK_HOLD)
    else:
        raise RuntimeError(
            f"[{identity}] LLM decision unavailable after {max_retries} retries: "
            f"{last_error}"
        ) from last_error


__all__ = [
    "is_retryable_llm_error",
    "parse_llm_response_with_thinking",
    "parse_llm_quantity_response_with_thinking",
    "robust_llm_call",
    "robust_llm_call_async",
]
