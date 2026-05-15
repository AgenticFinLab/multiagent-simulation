"""GamblerFallacy Rag Prompts

RAG variant prompts: imports system prompts from RuleLLM and adds RAG user template.
"""

from examples.GamblerFallacy.RuleLLM.prompts import (
    RULELLM_STREAK_REVERSAL_TRADER_SYS as RAGLLM_STREAK_REVERSAL_TRADER_SYS,
    RULELLM_HOT_HAND_TRADER_SYS as RAGLLM_HOT_HAND_TRADER_SYS,
    RULELLM_INDEPENDENT_ASSESSOR_SYS as RAGLLM_INDEPENDENT_ASSESSOR_SYS,
    RULELLM_ARBITRAGEUR_SYS as RAGLLM_ARBITRAGEUR_SYS,
    RULELLM_NOISE_TRADER_SYS as RAGLLM_NOISE_TRADER_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE (Retrieved Context) ==
{rag_context}

== MARKET STATE (Round {round}) ==
Current Price: ${price:.2f}
Fundamental Value: ${fundamental:.2f}
Price Deviation from Fundamental: {deviation:+.2%}

== YOUR PORTFOLIO ==
Cash Available: ${cash:.2f}
Shares Held: {position}
Portfolio Value: ${portfolio_value:.2f}

Using the retrieved knowledge and your trading rules, provide your decision.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
