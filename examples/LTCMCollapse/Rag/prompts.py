"""LTCMCollapse RAG prompts.

RAG uses the RuleLLM persona/rule system prompts and injects retrieved crisis
knowledge into the user message through ``{rag_context}``.
"""

from examples.LTCMCollapse.RuleLLM.prompts import (
    RULELLM_CENTRALBANK_PROMPT as RAG_CENTRALBANK_PROMPT,
    RULELLM_CONVERGENCEARBITRAGEUR_PROMPT as RAG_CONVERGENCEARBITRAGEUR_PROMPT,
    RULELLM_LEVERAGETRADER_PROMPT as RAG_LEVERAGETRADER_PROMPT,
    RULELLM_LIQUIDITYPROVIDER_PROMPT as RAG_LIQUIDITYPROVIDER_PROMPT,
    RULELLM_RISKMANAGER_PROMPT as RAG_RISKMANAGER_PROMPT,
)

RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

RAG_USER_TEMPLATE = """Relevant crisis knowledge retrieved for this decision:
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Initial Price: ${initial_price:.2f}
- Initial Position: {initial_position} shares
- Portfolio Value: ${portfolio_value:.2f}

Use the retrieved knowledge as contextual evidence, but still follow your persona and decision rules.
Respond with <analysis>...</analysis> and <decision>{{"action": "buy"|"sell"|"hold", "bid_price": {price:.2f}, "quantity": non-negative integer, "reasoning": "brief rationale"}}</decision>.
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""

__all__ = [
    "RAG_CONVERGENCEARBITRAGEUR_PROMPT",
    "RAG_LEVERAGETRADER_PROMPT",
    "RAG_RISKMANAGER_PROMPT",
    "RAG_LIQUIDITYPROVIDER_PROMPT",
    "RAG_CENTRALBANK_PROMPT",
    "RAG_USER_TEMPLATE",
    "RAG_FALLBACK",
]
