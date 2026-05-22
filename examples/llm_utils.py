"""Shared LLM response parsing utilities for all examples.

Provides standardized parsing for LLM responses with analysis and decision sections.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput, InferOutput

NON_RETRYABLE_API_MARKERS = (
    "authentication",
    "unauthorized",
    "permissiondenied",
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


def is_retryable_llm_error(exc: BaseException) -> bool:
    """Return True for transient provider failures that should not kill a row."""
    message = f"{exc.__class__.__name__}: {exc}".lower()
    if any(marker in message for marker in NON_RETRYABLE_API_MARKERS):
        return False
    return any(marker in message for marker in RETRYABLE_API_MARKERS)


def _extract_analysis_and_decision(response_text: str) -> tuple[str, Dict[str, Any]]:
    """Extract analysis text and decision JSON from a tagged LLM response."""
    analysis = ""
    decision_json = None

    # Primary: extract analysis from <analysis>...</analysis> tags
    analysis_match = re.search(r"<analysis>(.*?)</analysis>", response_text, re.DOTALL)
    if not analysis_match:
        # Legacy fallback: accept <think>...</think>
        analysis_match = re.search(r"<think>(.*?)</think>", response_text, re.DOTALL)
    if analysis_match:
        analysis = analysis_match.group(1).strip()

    # Extract decision from <decision>...</decision> tags
    decision_match = re.search(r"<decision>(.*?)</decision>", response_text, re.DOTALL)
    if decision_match:
        decision_json = decision_match.group(1).strip()

    # Fallback: try to find JSON directly if no decision tags found
    if not decision_json:
        # Try code block first
        code_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if code_match:
            decision_json = code_match.group(1).strip()
        else:
            # Try to find JSON object
            json_match = re.search(r"\{[^{}]*\}", response_text, re.DOTALL)
            if json_match:
                decision_json = json_match.group(0)

    if not decision_json:
        raise ValueError(f"No decision JSON found in response: {response_text[:100]}")

    try:
        parsed = json.loads(decision_json)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse decision JSON: {decision_json[:100]}")
    if not isinstance(parsed, dict):
        raise ValueError(f"Decision JSON must be an object: {decision_json[:100]}")
    return analysis, parsed


def _require_fields(parsed: Dict[str, Any], fields: list[str]) -> None:
    """Raise when parsed decision is missing required non-null fields."""
    missing_or_null = [f for f in fields if f not in parsed or parsed[f] is None]
    if missing_or_null:
        raise ValueError(f"Fields missing or null in LLM response: {missing_or_null}")


def parse_llm_response_with_thinking(response_text: str) -> Dict[str, Any]:
    """Parse LLM response with canonical analysis and decision sections.

    Canonical output format (all LLM/RuleLLM/Rag agents must produce this):

        <analysis>
        ... reasoning about current market conditions ...
        </analysis>

        <decision>
        {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
        </decision>

    Fallback formats accepted for robustness:
        - <think>...</think> tags (legacy — treated as <analysis>)
        - Raw JSON without surrounding tags
        - JSON in code blocks

    Returns dict with keys: analysis, action, bid_price, quantity, reasoning
    Raises ValueError on parse failure.
    """
    # Validate required fields
    analysis, parsed = _extract_analysis_and_decision(response_text)
    _require_fields(parsed, ["action", "bid_price", "quantity", "reasoning"])

    # Include analysis in the returned dict
    parsed["analysis"] = analysis
    return parsed


def parse_llm_quantity_response_with_thinking(response_text: str) -> Dict[str, Any]:
    """Parse a current-market quantity-order LLM response.

    Some scenarios intentionally clear orders at the current market price and
    therefore do not ask for or consume `bid_price`. These scenarios still use
    the same `<analysis>` / `<decision>` envelope, but their decision JSON is:

        {"action": "buy"|"sell"|"hold", "quantity": float, "reasoning": string}

    Use this parser only for documented current-market quantity schemas.
    """
    analysis, parsed = _extract_analysis_and_decision(response_text)
    _require_fields(parsed, ["action", "quantity", "reasoning"])
    parsed["analysis"] = analysis
    return parsed


def build_messages(sys_msg: str, user_msg: str) -> List[Dict[str, str]]:
    """Build message list for LLM inference.

    Args:
        sys_msg: System message content
        user_msg: User message content

    Returns:
        List of message dicts with role and content keys
    """
    messages = []
    if sys_msg:
        messages.append({"role": "system", "content": sys_msg})
    if user_msg:
        messages.append({"role": "user", "content": user_msg})
    return messages


async def call_llm(
    messages: List[Dict[str, str]],
    lm_type: str = "api",
    lm_name: str = "",
    generation_config: Optional[Dict[str, Any]] = None,
) -> InferOutput:
    """Call LLM with messages and return inference output.

    Args:
        messages: List of message dicts with role and content
        lm_type: Type of LLM to use (default: "api")
        lm_name: Name of the language model
        generation_config: Generation configuration dict

    Returns:
        InferOutput containing the LLM response

    Raises:
        ValueError: If lm_name is empty or invalid
        RuntimeError: If LLM call fails
    """
    if not lm_name:
        raise ValueError("lm_name must be provided")

    config = generation_config or {}

    # Create LLM client
    llm_client = LangChainAPIInference(
        lm_name=lm_name,
        generation_config=config,
    )

    # Convert messages to InferInput
    sys_msg = ""
    user_msg = ""

    for msg in messages:
        if msg.get("role") == "system":
            sys_msg = msg.get("content", "")
        elif msg.get("role") == "user":
            user_msg = msg.get("content", "")

    infer_input = InferInput(system_msg=sys_msg, user_msg=user_msg)

    # Run inference (not async, so run directly)
    infer_output = llm_client.run([infer_input])

    return infer_output
