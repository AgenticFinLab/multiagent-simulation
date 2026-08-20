"""Decision parsing helpers for EquityPremium stock/bond allocation variants."""

from __future__ import annotations

import json
import math
import re
from typing import Any, Dict


def parse_equity_premium_decision(response_text: str) -> Dict[str, Any]:
    """Parse the stock allocation decision contract.

    Required payload:
    ``{"stock_qty": float, "reasoning": str}``
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
        for field in ("stock_qty", "reasoning")
        if field not in parsed or parsed[field] is None
    ]
    if missing:
        raise ValueError(f"Fields missing or null in EquityPremium response: {missing}")

    try:
        stock_qty = float(parsed["stock_qty"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid stock_qty: {parsed['stock_qty']!r}") from exc
    if not math.isfinite(stock_qty):
        raise ValueError(f"Invalid non-finite stock_qty: {parsed['stock_qty']!r}")

    reasoning = str(parsed["reasoning"]).strip()
    if not reasoning:
        raise ValueError("EquityPremium reasoning must be a non-empty string")

    return {
        "stock_qty": stock_qty,
        "reasoning": reasoning,
        "analysis": analysis,
        "llm_fallback": False,
        "fallback_reason": "",
    }
