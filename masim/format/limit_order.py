"""Order format category — LIMIT ORDER.

Signal structure
----------------
    action     : "buy" | "sell" | "hold"
    bid_price  : positive float (execution reference price)
    quantity   : non-negative float (0 iff action == "hold")
    reasoning  : short string

This is the DEFAULT category used by the majority of MASIM scenarios that
model a standard limit-order market (stock, opinion, credit, FX, bond,
crypto, etc.) — anywhere the market coordinator aggregates orders on a
price × quantity book.

Two public surfaces
-------------------
* ``FORMAT_TAIL`` — a plain-text block that every scenario's ``prompts.py``
  imports and concatenates onto its persona string AT DEFINITION SITE::

      from masim.format.limit_order import FORMAT_TAIL

      _MOMENTUM_PERSONA = \"""You are a MOMENTUM INVESTOR ...\"""

      LLM_MOMENTUM_SYS = _MOMENTUM_PERSONA + "\\n\\n" + FORMAT_TAIL

  Reading the prompts.py file therefore shows the WHOLE final prompt
  composition — no hidden framework-side concatenation.

* ``validate_decision(decision)`` — plugged into
  :func:`masim.utils.llm_utils.robust_llm_call` as ``validate_fn``. Raises
  :class:`ValueError` on any missing / malformed field so ``robust_llm_call``
  retries the LLM until it emits a fully-specified decision.  No silent
  defaulting anywhere in the pipeline.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Set

NAME: str = "limit_order"

REQUIRED_FIELDS: Set[str] = {"action", "bid_price", "quantity", "reasoning"}

ACTION_VALUES: Set[str] = {"buy", "sell", "hold"}

FORMAT_TAIL: str = """\
TRADING CONSTRAINTS:
- Cannot spend more than your available cash
- Cannot sell more shares than you currently hold

Respond with your thinking in <analysis>...</analysis> tags followed by your decision in <decision>...</decision> tags.

The decision JSON must follow this exact format:
{
    "action": "buy" | "sell" | "hold",
    "bid_price": <float>,
    "quantity": <float>,
    "reasoning": <str>
}

Field requirements:
- action: Must be exactly "buy", "sell", or "hold".
- bid_price: Strictly positive numeric value (e.g., 102.5). NOT expressions or formulas. Use the current market price if you are holding.
- quantity: Non-negative numeric value (e.g., 5.0). NOT expressions or formulas. MUST be 0 when action is "hold" and MUST be > 0 when action is "buy" or "sell".
- reasoning: Concise non-empty string summarizing your analysis and rationale.

Every field is REQUIRED. Do not omit any field, do not emit expressions, do not emit null / None."""


def validate_decision(decision: Mapping[str, Any]) -> None:
    """Strict schema check for a limit-order LLM decision.

    Raises :class:`ValueError` if any required field is missing or malformed.
    The exception is caught inside
    :func:`masim.utils.llm_utils.robust_llm_call`, which then retries the LLM
    (up to ``max_retries``). No field is ever silently defaulted.
    """
    if not isinstance(decision, Mapping):
        raise ValueError(
            f"limit_order decision must be a mapping, got "
            f"{type(decision).__name__}"
        )

    missing = [f for f in REQUIRED_FIELDS if f not in decision]
    if missing:
        raise ValueError(
            f"limit_order decision missing required field(s): "
            f"{', '.join(sorted(missing))}"
        )

    action_raw = decision.get("action")
    if not isinstance(action_raw, str):
        raise ValueError(
            f"limit_order 'action' must be a string, got "
            f"{type(action_raw).__name__}"
        )
    action = action_raw.lower().strip()
    if action not in ACTION_VALUES:
        raise ValueError(
            f"limit_order 'action' must be one of "
            f"{sorted(ACTION_VALUES)}, got {action_raw!r}"
        )

    try:
        bid_price = float(decision["bid_price"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"limit_order 'bid_price' must be numeric, got "
            f"{decision['bid_price']!r}"
        ) from exc
    if not math.isfinite(bid_price):
        raise ValueError(
            f"limit_order 'bid_price' must be a finite number, got "
            f"{bid_price}"
        )
    if bid_price <= 0:
        raise ValueError(
            f"limit_order 'bid_price' must be strictly positive, got "
            f"{bid_price}"
        )

    try:
        quantity = float(decision["quantity"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"limit_order 'quantity' must be numeric, got "
            f"{decision['quantity']!r}"
        ) from exc
    if not math.isfinite(quantity):
        raise ValueError(
            f"limit_order 'quantity' must be a finite number, got "
            f"{quantity}"
        )
    if quantity < 0:
        raise ValueError(
            f"limit_order 'quantity' must be non-negative, got {quantity}"
        )
    if action == "hold" and quantity != 0:
        raise ValueError(
            f"limit_order 'quantity' must be 0 when action='hold', got "
            f"{quantity}"
        )
    if action in ("buy", "sell") and quantity <= 0:
        raise ValueError(
            f"limit_order '{action}' orders must have quantity > 0, got "
            f"{quantity}"
        )

    reasoning = decision.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError(
            "limit_order 'reasoning' must be a non-empty string"
        )


__all__ = [
    "NAME",
    "REQUIRED_FIELDS",
    "ACTION_VALUES",
    "FORMAT_TAIL",
    "validate_decision",
]
