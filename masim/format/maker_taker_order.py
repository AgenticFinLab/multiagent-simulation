"""Order format category — MAKER/TAKER ORDER.

Signal structure
----------------
    action              : "buy" | "sell" | "hold"
    bid_price           : positive float
    quantity            : non-negative float (0 iff action == "hold")
    reasoning           : short string
    provides_liquidity  : bool  ← the extra field vs limit_order

The ``provides_liquidity`` flag lets HFT / microstructure scenarios (e.g.
``FlashCrash2010``) distinguish liquidity-providing quotes (market makers,
passive fills) from liquidity-taking quotes (aggressive marketable orders).

Two public surfaces
-------------------
* ``FORMAT_TAIL`` — literal text every category-consuming ``prompts.py``
  imports and concatenates onto its persona AT DEFINITION SITE::

      from masim.format.maker_taker_order import FORMAT_TAIL

      _MM_PERSONA = \"""You are a HIGH-FREQUENCY MARKET MAKER ...\"""

      LLM_HFT_MARKET_MAKER_SYS = _MM_PERSONA + "\\n\\n" + FORMAT_TAIL

* ``validate_decision(decision)`` — plugged into
  :func:`masim.utils.llm_utils.robust_llm_call` as ``validate_fn``. Raises
  :class:`ValueError` on missing / malformed fields so the LLM is retried
  until it emits a fully-specified decision. No silent defaulting.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Set

NAME: str = "maker_taker_order"

REQUIRED_FIELDS: Set[str] = {
    "action",
    "bid_price",
    "quantity",
    "reasoning",
    "provides_liquidity",
}

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
    "reasoning": <str>,
    "provides_liquidity": <bool>
}

Field requirements:
- action: Must be exactly "buy", "sell", or "hold".
- bid_price: Strictly positive numeric value (e.g., 102.5). NOT expressions or formulas. Use the current market price if you are holding.
- quantity: Non-negative numeric value (e.g., 5.0). NOT expressions or formulas. MUST be 0 when action is "hold" and MUST be > 0 when action is "buy" or "sell".
- reasoning: Concise non-empty string summarizing your analysis and rationale.
- provides_liquidity: Boolean literal true or false. Set true when your quote adds resting liquidity to the book (passive maker); false when it consumes liquidity (aggressive taker).

Every field is REQUIRED. Do not omit any field, do not emit expressions, do not emit null / None."""


def _coerce_bool(value: Any) -> bool:
    """Reject soft-truthy junk. Accept only Python bool or the JSON literals."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low == "true":
            return True
        if low == "false":
            return False
    raise ValueError(
        f"maker_taker_order 'provides_liquidity' must be a boolean literal "
        f"(true / false), got {value!r}"
    )


def validate_decision(decision: Mapping[str, Any]) -> None:
    """Strict schema check for a maker/taker LLM decision.

    Raises :class:`ValueError` if any required field is missing or malformed.
    The exception is caught inside
    :func:`masim.utils.llm_utils.robust_llm_call`, which retries the LLM.
    No field is ever silently defaulted.
    """
    if not isinstance(decision, Mapping):
        raise ValueError(
            f"maker_taker_order decision must be a mapping, got "
            f"{type(decision).__name__}"
        )

    missing = [f for f in REQUIRED_FIELDS if f not in decision]
    if missing:
        raise ValueError(
            f"maker_taker_order decision missing required field(s): "
            f"{', '.join(sorted(missing))}"
        )

    action_raw = decision.get("action")
    if not isinstance(action_raw, str):
        raise ValueError(
            f"maker_taker_order 'action' must be a string, got "
            f"{type(action_raw).__name__}"
        )
    action = action_raw.lower().strip()
    if action not in ACTION_VALUES:
        raise ValueError(
            f"maker_taker_order 'action' must be one of "
            f"{sorted(ACTION_VALUES)}, got {action_raw!r}"
        )

    try:
        bid_price = float(decision["bid_price"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"maker_taker_order 'bid_price' must be numeric, got "
            f"{decision['bid_price']!r}"
        ) from exc
    if not math.isfinite(bid_price):
        raise ValueError(
            f"maker_taker_order 'bid_price' must be a finite number, got "
            f"{bid_price}"
        )
    if bid_price <= 0:
        raise ValueError(
            f"maker_taker_order 'bid_price' must be strictly positive, got "
            f"{bid_price}"
        )

    try:
        quantity = float(decision["quantity"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"maker_taker_order 'quantity' must be numeric, got "
            f"{decision['quantity']!r}"
        ) from exc
    if not math.isfinite(quantity):
        raise ValueError(
            f"maker_taker_order 'quantity' must be a finite number, got "
            f"{quantity}"
        )
    if quantity < 0:
        raise ValueError(
            f"maker_taker_order 'quantity' must be non-negative, got "
            f"{quantity}"
        )
    if action == "hold" and quantity != 0:
        raise ValueError(
            f"maker_taker_order 'quantity' must be 0 when action='hold', "
            f"got {quantity}"
        )
    if action in ("buy", "sell") and quantity <= 0:
        raise ValueError(
            f"maker_taker_order '{action}' orders must have quantity > 0, "
            f"got {quantity}"
        )

    reasoning = decision.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError(
            "maker_taker_order 'reasoning' must be a non-empty string"
        )

    _coerce_bool(decision["provides_liquidity"])  # raises on bad type


__all__ = [
    "NAME",
    "REQUIRED_FIELDS",
    "ACTION_VALUES",
    "FORMAT_TAIL",
    "validate_decision",
]
