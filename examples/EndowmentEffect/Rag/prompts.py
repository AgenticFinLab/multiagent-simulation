"""EndowmentEffect Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.EndowmentEffect.RuleLLM.prompts import (  # noqa: F401
    RULELLM_ENDOWED_HOLDER_SYS,
    RULELLM_STATUS_QUO_SELLER_SYS,
    RULELLM_RATIONAL_ARBITRAGEUR_SYS,
    RULELLM_NEW_BUYER_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_ENDOWED_HOLDER_SYS = RULELLM_ENDOWED_HOLDER_SYS
RAG_STATUS_QUO_SELLER_SYS = RULELLM_STATUS_QUO_SELLER_SYS
RAG_RATIONAL_ARBITRAGEUR_SYS = RULELLM_RATIONAL_ARBITRAGEUR_SYS
RAG_NEW_BUYER_SYS = RULELLM_NEW_BUYER_SYS
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
Respond with <analysis>...</analysis> and <decision>{{"action": "buy", "bid_price": 100.0, "quantity": 1, "reasoning": "brief rationale"}}</decision>.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
