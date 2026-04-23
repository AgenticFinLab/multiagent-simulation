"""CurrencyCrisis Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.CurrencyCrisis.RuleLLM.prompts import (  # noqa: F401
    RULELLM_SPECULATIVE_ATTACKER_SYS,
    RULELLM_SELF_FULFILLING_TRADER_SYS,
    RULELLM_CENTRAL_BANK_DEFENDER_SYS,
    RULELLM_FUNDAMENTAL_HEDGER_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_SPECULATIVE_ATTACKER_SYS = RULELLM_SPECULATIVE_ATTACKER_SYS
RAG_SELF_FULFILLING_TRADER_SYS = RULELLM_SELF_FULFILLING_TRADER_SYS
RAG_CENTRAL_BANK_DEFENDER_SYS = RULELLM_CENTRAL_BANK_DEFENDER_SYS
RAG_FUNDAMENTAL_HEDGER_SYS = RULELLM_FUNDAMENTAL_HEDGER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.4f}
- Fundamental Value: ${fundamental:.4f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules and the domain knowledge above to decide your action.
Respond with <think>...</think> and <decision>{{"action": "buy"|"sell"|"hold", "quantity": integer}}</decision>."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
