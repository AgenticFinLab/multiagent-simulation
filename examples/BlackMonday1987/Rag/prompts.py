"""BlackMonday1987 Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.BlackMonday1987.RuleLLM.prompts import (  # noqa: F401
    RULELLM_PORTFOLIO_INSURER_SYS,
    RULELLM_INDEX_ARBITRAGEUR_SYS,
    RULELLM_PROGRAM_TRADER_SYS,
    RULELLM_VALUE_INVESTOR_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_PORTFOLIO_INSURER_SYS = RULELLM_PORTFOLIO_INSURER_SYS
RAG_INDEX_ARBITRAGEUR_SYS = RULELLM_INDEX_ARBITRAGEUR_SYS
RAG_PROGRAM_TRADER_SYS = RULELLM_PROGRAM_TRADER_SYS
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
Respond with <think>...</think> and <decision>{{"action": "buy"|"sell"|"hold", "quantity": integer}}</decision>."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
