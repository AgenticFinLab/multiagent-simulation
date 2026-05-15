"""FramingEffect Rag Prompts

RAG variant prompts: imports system prompts from RuleLLM and adds RAG user template.
"""

from examples.FramingEffect.RuleLLM.prompts import (
    RULELLM_GAIN_FRAME_FOLLOWER_SYS as RAGLLM_GAIN_FRAME_FOLLOWER_SYS,
    RULELLM_LOSS_FRAME_REACTOR_SYS as RAGLLM_LOSS_FRAME_REACTOR_SYS,
    RULELLM_FRAME_INVARIANT_TRADER_SYS as RAGLLM_FRAME_INVARIANT_TRADER_SYS,
    RULELLM_ARBITRAGE_FRAMER_SYS as RAGLLM_ARBITRAGE_FRAMER_SYS,
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
