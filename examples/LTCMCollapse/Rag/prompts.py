"""LTCMCollapse Rag Prompts

System prompts for RAG-augmented agents in the LTCMCollapse simulation.
"""

from examples.LTCMCollapse.LLM.prompts import (
    LLM_CONVERGENCEARBITRAGEUR_PROMPT as RAG_CONVERGENCEARBITRAGEUR_PROMPT,
    LLM_LEVERAGETRADER_PROMPT as RAG_LEVERAGETRADER_PROMPT,
    LLM_RISKMANAGER_PROMPT as RAG_RISKMANAGER_PROMPT,
    LLM_LIQUIDITYPROVIDER_PROMPT as RAG_LIQUIDITYPROVIDER_PROMPT,
    LLM_CENTRALBANK_PROMPT as RAG_CENTRALBANK_PROMPT,
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
    "RAG_CONVERGENCEARBITRAGEUR_PROMPT",
    "RAG_LEVERAGETRADER_PROMPT",
    "RAG_RISKMANAGER_PROMPT",
    "RAG_LIQUIDITYPROVIDER_PROMPT",
    "RAG_CENTRALBANK_PROMPT",
    "RAG_USER_TEMPLATE",
]
