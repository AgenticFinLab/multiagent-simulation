"""Decision parsing helpers for the SVBBankRun proxy-order schema."""

from __future__ import annotations

import json
import math
import re
from typing import Any, Dict


VALID_ACTIONS = {"buy", "sell", "hold"}


def parse_svbbankrun_decision(response_text: str) -> Dict[str, Any]:
    """Parse the SVBBankRun API decision contract.

    The SVBBankRun market consumes a bank-health proxy order, not a limit-order
    book bid. The required API payload is:

    ``{"action": "buy"|"sell"|"hold", "quantity": int, "reasoning": str}``
    """
    analysis = ""
    analysis_match = re.search(r"<analysis>(.*?)</analysis>", response_text, re.DOTALL)
    if analysis_match:
        analysis = analysis_match.group(1).strip()

    decision_text = ""
    decision_match = re.search(r"<decision>(.*?)</decision>", response_text, re.DOTALL)
    if decision_match:
        decision_text = decision_match.group(1).strip()
    else:
        code_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if code_match:
            decision_text = code_match.group(1).strip()
        else:
            json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
            if json_match:
                decision_text = json_match.group(0)

    if not decision_text:
        raise ValueError(f"No decision JSON found in response: {response_text[:120]}")

    try:
        parsed = json.loads(decision_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse decision JSON: {decision_text[:120]}") from exc

    missing = [
        field
        for field in ("action", "quantity", "reasoning")
        if field not in parsed or parsed[field] is None
    ]
    if missing:
        raise ValueError(f"Fields missing or null in SVBBankRun response: {missing}")

    action = str(parsed["action"]).lower()
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid SVBBankRun action: {parsed['action']!r}")

    try:
        quantity_value = float(parsed["quantity"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid SVBBankRun quantity: {parsed['quantity']!r}") from exc
    if not math.isfinite(quantity_value):
        raise ValueError(f"Invalid non-finite SVBBankRun quantity: {parsed['quantity']!r}")
    quantity = int(quantity_value)

    reasoning = str(parsed["reasoning"]).strip()
    if not reasoning:
        raise ValueError("SVBBankRun reasoning must be a non-empty string")

    return {
        "action": action,
        "quantity": quantity,
        "reasoning": reasoning,
        "analysis": analysis,
        "llm_fallback": False,
        "fallback_reason": "",
    }
