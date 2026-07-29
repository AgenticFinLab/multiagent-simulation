"""GameStopShortSqueeze Rag Prompts

System prompts for RAG-augmented LLM agents in the GameStopShortSqueeze simulation.
Imports system prompts from RuleLLM and adds a RAG user template with retrieved context.
"""

from examples.GameStopShortSqueeze.RuleLLM.prompts import (
    RULELLM_RETAIL_COORDINATED_SYS as RAGLLM_RETAIL_COORDINATED_SYS,
    RULELLM_SHORT_SELLER_HF_SYS as RAGLLM_SHORT_SELLER_HF_SYS,
    RULELLM_MARKET_MAKER_GAMMA_SYS as RAGLLM_MARKET_MAKER_GAMMA_SYS,
    RULELLM_INSTITUTIONAL_VALUE_SYS as RAGLLM_INSTITUTIONAL_VALUE_SYS,
    RULELLM_MOMENTUM_RETAIL_SYS as RAGLLM_MOMENTUM_RETAIL_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE (Retrieved Context) ==
{rag_context}

== MARKET STATE (Round {round}) ==
Current Price:      ${price:.2f}
Fundamental Value:  ${fundamental:.2f}
Price Deviation:    {deviation:+.2%}

== YOUR PORTFOLIO ==
Cash Available: ${cash:.2f}
Position:       {position} shares
Portfolio Value: ${portfolio_value:.2f}

== CONFIGURED PARAMETERS ==
{decision_params}

Using the retrieved context and your trading rules, make your decision.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
