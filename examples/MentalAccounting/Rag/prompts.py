"""MentalAccounting Rag Prompts

RAG-augmented prompts: re-exports LLM and RuleLLM prompts and adds RAG user template.
"""

from examples.MentalAccounting.LLM.prompts import (  # noqa: F401
    LLM_MENTAL_ACCOUNTANT_PROMPT,
    LLM_HOUSE_MONEY_PROMPT,
    LLM_RATIONAL_PORTFOLIO_PROMPT,
    LLM_SUNK_COST_PROMPT,
    LLM_NOISE_TRADER_PROMPT,
)
from examples.MentalAccounting.RuleLLM.prompts import (  # noqa: F401
    RULELLM_MENTAL_ACCOUNTANT_SYS,
    RULELLM_HOUSE_MONEY_SYS,
    RULELLM_RATIONAL_PORTFOLIO_SYS,
    RULELLM_SUNK_COST_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE ==
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2f}%

Your Portfolio:
- Cash: ${cash:.2f}
- Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}
- Entry Price: ${entry_price:.2f}
- Unrealised P&L: {pnl:+.2f}%

Apply your DECISION RULES, informed by the relevant knowledge above.

Required output:
<analysis>brief calculation, retrieved-knowledge use, and rationale</analysis>
<decision>{{"action": "buy"|"sell"|"hold", "bid_price": {price:.2f},
"quantity": non-negative integer, "reasoning": "brief rationale"}}</decision>
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""
