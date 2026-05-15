"""CreditCycle Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.CreditCycle.RuleLLM.prompts import (  # noqa: F401
    RULELLM_PRO_CYCLICAL_LENDER_SYS,
    RULELLM_MINSKY_BORROWER_SYS,
    RULELLM_COUNTER_CYCLICAL_LENDER_SYS,
    RULELLM_VALUE_INVESTOR_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_PRO_CYCLICAL_LENDER_SYS = RULELLM_PRO_CYCLICAL_LENDER_SYS
RAG_MINSKY_BORROWER_SYS = RULELLM_MINSKY_BORROWER_SYS
RAG_COUNTER_CYCLICAL_LENDER_SYS = RULELLM_COUNTER_CYCLICAL_LENDER_SYS
RAG_VALUE_INVESTOR_SYS = RULELLM_VALUE_INVESTOR_SYS
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
Respond with <analysis>...</analysis> and <decision>{{"action": "buy"|"sell"|"hold", "bid_price": {price:.2f}, "quantity": integer, "reasoning": "brief rationale"}}</decision>."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
