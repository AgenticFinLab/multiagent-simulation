"""Decision controls shared by CreditCycle LLM-style agents."""

from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Optional

from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger(__name__)

ACTION_SET = {"buy", "sell", "hold"}
SIZE_KEYS = (
    "order_size",
    "base_size",
    "hedge_size",
    "speculative_size",
    "ponzi_size",
    "counter_cycle_size",
    "value_size",
    "noise_size",
)
PARSE_ERROR_MARKERS = (
    "No decision JSON found",
    "Failed to parse decision JSON",
    "Fields missing or null in LLM response",
)
NON_RETRYABLE_API_MARKERS = (
    "AccountOverdue",
    "Authentication",
    "Unauthorized",
    "PermissionDenied",
    "invalid api key",
    "insufficient quota",
)
RETRYABLE_API_MARKERS = (
    "timeout",
    "timed out",
    "connection",
    "temporarily",
    "rate limit",
    "ratelimit",
    "too many requests",
    "429",
)


def _positive_int(value: Any) -> Optional[int]:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def infer_max_order_size(extras: Mapping[str, Any]) -> int:
    """Infer the role-level maximum order size from CreditCycle config extras."""
    explicit = _positive_int(extras["order_size"]) if "order_size" in extras else None
    if explicit is not None:
        base_size = explicit
    else:
        sizes = [_positive_int(extras[key]) for key in SIZE_KEYS if key in extras]
        base_size = max((size for size in sizes if size is not None), default=0)

    multiplier = 1.0
    if "credit_multiplier" in extras:
        try:
            multiplier = max(float(extras["credit_multiplier"]), 0.0)
        except (TypeError, ValueError):
            multiplier = 1.0
    return int(base_size * multiplier)


def normalize_action(action: Any) -> str:
    """Return a supported trading action, defaulting to hold."""
    normalized = str(action).strip().lower()
    return normalized if normalized in ACTION_SET else "hold"


def safe_int_quantity(value: Any) -> int:
    """Convert an LLM quantity to a non-negative integer."""
    parsed = _positive_int(value)
    return parsed if parsed is not None else 0


def safe_float(value: Any, default: float) -> float:
    """Convert an LLM numeric value to float with a deterministic fallback."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp_order(
    parsed: Mapping[str, Any],
    *,
    cash: float,
    position: int,
    price: float,
    max_order_size: int,
) -> Dict[str, Any]:
    """Normalize and clamp a parsed LLM decision to feasible CreditCycle order."""
    action = normalize_action(parsed.get("action"))
    quantity = safe_int_quantity(parsed.get("quantity"))
    bid_price = safe_float(parsed.get("bid_price"), price)
    reasoning = str(parsed.get("reasoning", "")).strip()

    if action == "hold":
        quantity = 0
    if max_order_size > 0:
        quantity = min(quantity, max_order_size)
    if action == "buy":
        quantity = min(quantity, int(cash / price) if price > 0 else 0)
    elif action == "sell":
        quantity = min(quantity, max(int(position), 0))

    if quantity <= 0:
        action = "hold"
        quantity = 0

    return {
        "action": action,
        "quantity": quantity,
        "bid_price": bid_price,
        "reasoning": reasoning,
        "fallback": False,
        "fallback_type": "",
    }


def is_parse_contract_error(exc: BaseException) -> bool:
    """Return True for deterministic parser-contract failures."""
    if not isinstance(exc, ValueError):
        return False
    message = str(exc)
    return any(marker in message for marker in PARSE_ERROR_MARKERS)


def is_retryable_llm_error(exc: BaseException) -> bool:
    """Return True for transient LLM/API errors worth another call."""
    message = f"{exc.__class__.__name__}: {exc}".lower()
    if any(marker.lower() in message for marker in NON_RETRYABLE_API_MARKERS):
        return False
    return any(marker in message for marker in RETRYABLE_API_MARKERS)


def hold_decision(reason: str, fallback_type: str) -> Dict[str, Any]:
    """Build a deterministic hold decision with fallback metadata."""
    return {
        "action": "hold",
        "quantity": 0,
        "bid_price": 0.0,
        "reasoning": reason,
        "fallback": True,
        "fallback_type": fallback_type,
    }


def record_fallback(custom_state: Dict[str, Any], fallback_type: str) -> None:
    """Accumulate fallback counts in player state for post-run quality checks."""
    counts = custom_state.setdefault("llm_fallback_counts", {})
    counts[fallback_type] = int(counts.get(fallback_type, 0)) + 1


def decide_with_llm_contract(
    *,
    llm_client: Any,
    system_prompt: str,
    user_prompt: str,
    cash: float,
    position: int,
    price: float,
    max_order_size: int,
    identity: str,
    max_attempts: int = 3,
) -> Dict[str, Any]:
    """Call the LLM, parse once per contract response, and clamp the order.

    Parse-contract failures are deterministic for a given response, so they
    immediately fall back to hold instead of spending two more full API calls.
    Transient API failures still retry up to ``max_attempts``.
    """
    last_error: Optional[BaseException] = None
    for attempt in range(max_attempts):
        try:
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            result = llm_client.run([infer_input])
            response = result.outputs[0].response
            parsed = parse_llm_response_with_thinking(response)
            decision = clamp_order(
                parsed,
                cash=cash,
                position=position,
                price=price,
                max_order_size=max_order_size,
            )
            decision["llm_attempts"] = attempt + 1
            return decision
        except Exception as exc:  # pylint: disable=broad-except
            last_error = exc
            if is_parse_contract_error(exc):
                logger.warning(
                    "[%s] LLM parse contract failed on attempt %d: %s. Holding.",
                    identity,
                    attempt + 1,
                    exc,
                )
                decision = hold_decision(str(exc), "parse_contract")
                decision["llm_attempts"] = attempt + 1
                return decision
            if is_retryable_llm_error(exc) and attempt < max_attempts - 1:
                logger.warning(
                    "[%s] Retryable LLM error on attempt %d/%d: %s",
                    identity,
                    attempt + 1,
                    max_attempts,
                    exc,
                )
                continue
            break

    raise RuntimeError(
        f"[{identity}] LLM decision failed after {max_attempts} attempts: {last_error}"
    ) from last_error
