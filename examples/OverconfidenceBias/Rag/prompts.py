"""OverconfidenceBias Rag Prompts.

Re-exports system prompts from RuleLLM and adds RAG user template.
"""

from examples.OverconfidenceBias.RuleLLM.prompts import (
    RULELLM_OVERCONFIDENT_TRADER_SYS,
    RULELLM_SELF_ATTRIBUTOR_SYS,
    RULELLM_CALIBRATED_TRADER_SYS,
    RULELLM_CONTRARIAN_INVESTOR_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE ==
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2f}%
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Apply your DECISION RULES, informed by the relevant knowledge above and output your trade decision.

First output your reasoning inside <analysis>...</analysis> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {{"action": "buy", "bid_price": 100.0, "quantity": 1, "reasoning": "brief rationale"}}
IMPORTANT: quantity MUST be a positive integer, NOT negative or a formula.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

__all__ = [
    "RULELLM_OVERCONFIDENT_TRADER_SYS",
    "RULELLM_SELF_ATTRIBUTOR_SYS",
    "RULELLM_CALIBRATED_TRADER_SYS",
    "RULELLM_CONTRARIAN_INVESTOR_SYS",
    "RULELLM_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
