"""ConfirmationBias Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.ConfirmationBias.RuleLLM.prompts import (  # noqa: F401
    RULELLM_BELIEF_ANCHOR_SYS,
    RULELLM_SELECTIVE_SCANNER_SYS,
    RULELLM_BALANCED_ANALYST_SYS,
    RULELLM_CONTRARIAN_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_BELIEF_ANCHOR_SYS = RULELLM_BELIEF_ANCHOR_SYS
RAG_SELECTIVE_SCANNER_SYS = RULELLM_SELECTIVE_SCANNER_SYS
RAG_BALANCED_ANALYST_SYS = RULELLM_BALANCED_ANALYST_SYS
RAG_CONTRARIAN_TRADER_SYS = RULELLM_CONTRARIAN_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules and the domain knowledge above to decide your action.
Respond with <analysis>...</analysis> and <decision>{{"action": "buy", "bid_price": {price:.2f}, "quantity": 1, "reasoning": "brief rationale"}}</decision>.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string).
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
