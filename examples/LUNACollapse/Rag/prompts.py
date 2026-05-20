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
- Price Deviation: {deviation:+.2f}%
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Based on your trading strategy and the background knowledge above, what action do you take?
Provide your analysis and decision in the specified format.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

__all__ = [
    "RAG_STABLECOINHOLDER_PROMPT",
    "RAG_ARBITRAGEUR_PROMPT",
    "RAG_DEFILENDER_PROMPT",
    "RAG_ANCHORDEPOSITOR_PROMPT",
    "RAG_VALUEBUYER_PROMPT",
    "RAG_USER_TEMPLATE",
]
