"""RumorSpread-specific LLM response parser."""

from __future__ import annotations

import json
import re
from typing import Any, Dict


def parse_rumor_response(response_text: str) -> Dict[str, Any]:
    """Parse RumorSpread LLM output.

    RumorSpread is not a trading scenario. Its LLM agents emit social actions
    instead of orders, so the canonical trading parser is intentionally not
    used here.
    """

    analysis = ""
    decision_json = None

    analysis_match = re.search(r"<analysis>(.*?)</analysis>", response_text, re.DOTALL)
    if not analysis_match:
        analysis_match = re.search(r"<think>(.*?)</think>", response_text, re.DOTALL)
    if analysis_match:
        analysis = analysis_match.group(1).strip()

    decision_match = re.search(r"<decision>(.*?)</decision>", response_text, re.DOTALL)
    if decision_match:
        decision_json = decision_match.group(1).strip()

    if not decision_json:
        code_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if code_match:
            decision_json = code_match.group(1).strip()
        else:
            json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
            if json_match:
                decision_json = json_match.group(0)

    if not decision_json:
        raise ValueError(f"No decision JSON found in response: {response_text[:100]}")

    try:
        parsed = json.loads(decision_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse decision JSON: {decision_json[:100]}") from exc

    required_fields = ["action_type", "intensity", "reasoning"]
    missing_or_null = [
        field for field in required_fields if field not in parsed or parsed[field] is None
    ]
    if missing_or_null:
        raise ValueError(f"Fields missing or null in LLM response: {missing_or_null}")
    action_type = str(parsed["action_type"]).lower()
    if action_type not in {"spread", "ignore", "correct"}:
        raise ValueError(f"Invalid action_type: {parsed['action_type']!r}")
    try:
        intensity = float(parsed["intensity"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid intensity: {parsed['intensity']!r}") from exc
    reasoning = str(parsed["reasoning"]).strip()
    if not reasoning:
        raise ValueError("Empty reasoning")

    parsed["action_type"] = action_type
    parsed["intensity"] = max(0.0, min(1.0, intensity))
    parsed["reasoning"] = reasoning
    parsed["analysis"] = analysis
    return parsed
