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
The decision must be valid JSON: {{"action": "buy" or "sell" or "hold", "quantity": integer}}
IMPORTANT: quantity MUST be a positive integer, NOT negative or a formula.
"""

__all__ = [
    "RULELLM_OVERCONFIDENT_TRADER_SYS",
    "RULELLM_SELF_ATTRIBUTOR_SYS",
    "RULELLM_CALIBRATED_TRADER_SYS",
    "RULELLM_CONTRARIAN_INVESTOR_SYS",
    "RULELLM_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
