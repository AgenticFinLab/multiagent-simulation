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

Apply your DECISION RULES, informed by the relevant knowledge above.

Required output:
<analysis>brief calculation, retrieved-knowledge use, and rationale</analysis>
<decision>{{"action": "buy"|"sell"|"hold", "bid_price": {price:.2f},
"quantity": non-negative integer, "reasoning": "brief rationale"}}</decision>
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""

__all__ = [
    "RULELLM_OVERCONFIDENT_TRADER_SYS",
    "RULELLM_SELF_ATTRIBUTOR_SYS",
    "RULELLM_CALIBRATED_TRADER_SYS",
    "RULELLM_CONTRARIAN_INVESTOR_SYS",
    "RULELLM_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
