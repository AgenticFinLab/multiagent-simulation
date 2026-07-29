"""Order format category — PARTICIPATION ORDER.

Signal structure
----------------
    action     : "buy" | "sell" | "hold"
    quantity   : non-negative integer proxy units
    reasoning  : short string

NOTE: there is intentionally NO ``bid_price`` in this category. Participation
markets aggregate positional / directional signals (bank-run pressure, panic
withdrawal, stampede) rather than price × quantity. Scenarios that use this
category (e.g. ``SVBBankRun``) compute market impact from participation
counts alone — a bid_price would be meaningless.

Two public surfaces
-------------------
* ``FORMAT_TAIL`` — literal text every category-consuming ``prompts.py``
  imports and concatenates onto its persona AT DEFINITION SITE::

      from masim.format.participation_order import FORMAT_TAIL

      _DEPOSITOR_PERSONA = \"""You are a DEPOSITOR ...\"""

      LLM_DEPOSITOR_SYS = _DEPOSITOR_PERSONA + "\\n\\n" + FORMAT_TAIL

* ``validate_decision(decision)`` — plugged into
  :func:`masim.utils.llm_utils.robust_llm_call` as ``validate_fn``. Raises
  :class:`ValueError` on missing / malformed fields; ``robust_llm_call``
  retries the LLM until the decision is fully specified.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Set

NAME: str = "participation_order"

REQUIRED_FIELDS: Set[str] = {"action", "quantity", "reasoning"}

ACTION_VALUES: Set[str] = {"buy", "sell", "hold"}

FORMAT_TAIL: str = """\
Respond with your thinking in <analysis>...</analysis> tags followed by your decision in <decision>...</decision> tags.

The decision JSON must follow this exact format:
{
    "action": "buy" | "sell" | "hold",
    "quantity": <int>,
    "reasoning": <str>
}

Field requirements:
- action: Must be exactly "buy", "sell", or "hold".
- quantity: Non-negative integer proxy units (e.g., 1, 3). NOT expressions or formulas. MUST be 0 when action is "hold" and MUST be >= 1 when action is "buy" or "sell".
- reasoning: Concise non-empty string summarizing your analysis and rationale.

Every field is REQUIRED. Do not include a bid_price field — this market aggregates participation counts, not prices. Do not omit any field, do not emit expressions, do not emit null / None."""


def validate_decision(decision: Mapping[str, Any]) -> None:
    """Strict schema check for a participation-order LLM decision.

    Raises :class:`ValueError` if any required field is missing or malformed.
    The exception is caught inside
    :func:`masim.utils.llm_utils.robust_llm_call`, which retries the LLM.
    No field is ever silently defaulted.
    """
    if not isinstance(decision, Mapping):
        raise ValueError(
            f"participation_order decision must be a mapping, got "
            f"{type(decision).__name__}"
        )

    missing = [f for f in REQUIRED_FIELDS if f not in decision]
    if missing:
        raise ValueError(
            f"participation_order decision missing required field(s): "
            f"{', '.join(sorted(missing))}"
        )

    action_raw = decision.get("action")
    if not isinstance(action_raw, str):
        raise ValueError(
            f"participation_order 'action' must be a string, got "
            f"{type(action_raw).__name__}"
        )
    action = action_raw.lower().strip()
    if action not in ACTION_VALUES:
        raise ValueError(
            f"participation_order 'action' must be one of "
            f"{sorted(ACTION_VALUES)}, got {action_raw!r}"
        )

    q_raw = decision["quantity"]
    if isinstance(q_raw, bool):  # bool is a subclass of int; explicitly reject
        raise ValueError(
            f"participation_order 'quantity' must be an integer, got bool "
            f"{q_raw!r}"
        )
    try:
        q_float = float(q_raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"participation_order 'quantity' must be numeric, got {q_raw!r}"
        ) from exc
    if not math.isfinite(q_float):
        raise ValueError(
            f"participation_order 'quantity' must be a finite number, got "
            f"{q_float}"
        )
    if q_float < 0:
        raise ValueError(
            f"participation_order 'quantity' must be non-negative, got "
            f"{q_float}"
        )
    if not q_float.is_integer():
        raise ValueError(
            f"participation_order 'quantity' must be an integer, got "
            f"{q_raw!r}"
        )
    q_int = int(q_float)
    if action == "hold" and q_int != 0:
        raise ValueError(
            f"participation_order 'quantity' must be 0 when action='hold', "
            f"got {q_int}"
        )
    if action in ("buy", "sell") and q_int < 1:
        raise ValueError(
            f"participation_order '{action}' orders must have quantity >= 1, "
            f"got {q_int}"
        )

    reasoning = decision.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise ValueError(
            "participation_order 'reasoning' must be a non-empty string"
        )


__all__ = [
    "NAME",
    "REQUIRED_FIELDS",
    "ACTION_VALUES",
    "FORMAT_TAIL",
    "validate_decision",
]
