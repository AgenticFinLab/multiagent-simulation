"""EuropeanDebtCrisis Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.EuropeanDebtCrisis.RuleLLM.prompts import (  # noqa: F401
    RULELLM_PERIPHERY_BOND_SELLER_SYS,
    RULELLM_CREDITOR_PANICKER_SYS,
    RULELLM_CORE_BOND_BUYER_SYS,
    RULELLM_ECB_INTERVENOR_SYS,
    RULELLM_HEDGED_FUND_SYS,
)

RAG_PERIPHERY_BOND_SELLER_SYS = RULELLM_PERIPHERY_BOND_SELLER_SYS
RAG_CREDITOR_PANICKER_SYS = RULELLM_CREDITOR_PANICKER_SYS
RAG_CORE_BOND_BUYER_SYS = RULELLM_CORE_BOND_BUYER_SYS
RAG_ECB_INTERVENOR_SYS = RULELLM_ECB_INTERVENOR_SYS
RAG_HEDGED_FUND_SYS = RULELLM_HEDGED_FUND_SYS

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
Respond with <analysis>...</analysis> and <decision>{{"action": "buy"|"sell"|"hold", "quantity": integer}}</decision>."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
