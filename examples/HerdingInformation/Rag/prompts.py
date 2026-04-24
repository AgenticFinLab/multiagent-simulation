"""HerdingInformation Rag Prompts

System prompts for RAG-augmented LLM agents in the HerdingInformation simulation.
"""

from examples.HerdingInformation.RuleLLM.prompts import (
    RULELLM_CASCADE_FOLLOWER_SYS as RAGLLM_CASCADE_FOLLOWER_SYS,
    RULELLM_REPUTATION_HERDER_SYS as RAGLLM_REPUTATION_HERDER_SYS,
    RULELLM_INDEPENDENT_THINKER_SYS as RAGLLM_INDEPENDENT_THINKER_SYS,
    RULELLM_CONTRARIAN_SYS as RAGLLM_CONTRARIAN_SYS,
    RULELLM_NOISE_TRADER_SYS as RAGLLM_NOISE_TRADER_SYS,
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

Using the retrieved context and your trading rules, make your decision.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
