"""LUNACollapse RAG prompts.

RAG uses the RuleLLM persona/rule prompts and injects retrieved stablecoin
crisis knowledge into the user message through ``{rag_context}``.
"""

from examples.LUNACollapse.RuleLLM.prompts import (
    RULELLM_ANCHORDEPOSITOR_PROMPT as RAG_ANCHORDEPOSITOR_PROMPT,
    RULELLM_ARBITRAGEUR_PROMPT as RAG_ARBITRAGEUR_PROMPT,
    RULELLM_DEFILENDER_PROMPT as RAG_DEFILENDER_PROMPT,
    RULELLM_STABLECOINHOLDER_PROMPT as RAG_STABLECOINHOLDER_PROMPT,
    RULELLM_VALUEBUYER_PROMPT as RAG_VALUEBUYER_PROMPT,
)

RAG_USER_TEMPLATE = """Relevant background knowledge:
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Apply your persona, decision rules, and retrieved knowledge to choose one trading action.
Respond with <analysis>...</analysis> and <decision>{{"action": "buy"|"sell"|"hold", "bid_price": {price:.2f}, "quantity": non-negative integer, "reasoning": "brief rationale"}}</decision>.
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""

__all__ = [
    "RAG_STABLECOINHOLDER_PROMPT",
    "RAG_ARBITRAGEUR_PROMPT",
    "RAG_DEFILENDER_PROMPT",
    "RAG_ANCHORDEPOSITOR_PROMPT",
    "RAG_VALUEBUYER_PROMPT",
    "RAG_USER_TEMPLATE",
]
