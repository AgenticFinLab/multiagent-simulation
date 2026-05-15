"""LossAversion Rag Prompts

System prompts for RAG-augmented LLM agents in the LossAversion simulation.
Imports base prompts from LLM variant and adds RAG user template.
"""

from examples.LossAversion.LLM.prompts import (  # noqa: F401
    LLM_LOSS_AVERSE_PROMPT,
    LLM_BREAK_EVEN_PROMPT,
    LLM_RATIONAL_PROMPT,
    LLM_MOMENTUM_PROMPT,
    LLM_MARKET_MAKER_PROMPT,
)
from examples.LossAversion.RuleLLM.prompts import (  # noqa: F401
    RULELLM_LOSS_AVERSE_PROMPT,
    RULELLM_BREAK_EVEN_PROMPT,
    RULELLM_RATIONAL_PROMPT,
    RULELLM_MOMENTUM_PROMPT,
    RULELLM_MARKET_MAKER_PROMPT,
)

# =============================================================================
# RAG User Message Template (adds {rag_context} placeholder)
# =============================================================================

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE (from your personal reference library) ==
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2f}%
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Apply your DECISION RULES, informed by the relevant knowledge above, and output your trade decision.

First output your reasoning inside <analysis>...</analysis> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {{"action": "buy", "bid_price": 100.0, "quantity": 1, "reasoning": "brief rationale"}}

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""
