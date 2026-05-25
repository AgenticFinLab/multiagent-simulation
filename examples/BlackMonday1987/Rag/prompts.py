"""BlackMonday1987 Rag Prompts

Rag-variant system prompts: identical to RuleLLM system prompts (PERSONA + DECISION RULES),
with the user template extended to include {rag_context}.

System prompts are aliased from RuleLLM — the Rag variant adds retrieved domain knowledge
via the {rag_context} placeholder in the user prompt.

If no documents are retrieved, inject: "(No relevant knowledge retrieved this round.)"

Output format (canonical):
  <analysis>...</analysis>
  <decision>{"action": "buy"|"sell"|"hold", "bid_price": float,
             "quantity": float, "reasoning": string}</decision>
"""

from examples.BlackMonday1987.RuleLLM.prompts import (  # noqa: F401
    RULELLM_INDEX_ARBITRAGEUR_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_PORTFOLIO_INSURER_SYS,
    RULELLM_PROGRAM_TRADER_SYS,
    RULELLM_VALUE_INVESTOR_SYS,
)

# Rag system prompts are identical to RuleLLM — extend via {rag_context} in user template
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

Apply your DECISION RULES step-by-step, incorporating the domain knowledge above.
Show calculations in <analysis>...</analysis>, then provide your decision in <decision>...</decision>.
The decision must be valid JSON:
{{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
IMPORTANT: bid_price must be strictly positive; for hold, use the current price as bid_price; never output bid_price: 0.
"""

__all__ = [
    "RAG_PORTFOLIO_INSURER_SYS",
    "RAG_INDEX_ARBITRAGEUR_SYS",
    "RAG_PROGRAM_TRADER_SYS",
    "RAG_VALUE_INVESTOR_SYS",
    "RAG_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
