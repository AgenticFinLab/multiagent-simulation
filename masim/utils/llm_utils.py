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


__all__ = [
    "is_retryable_llm_error",
    "parse_llm_response_with_thinking",
    "parse_llm_quantity_response_with_thinking",
]
