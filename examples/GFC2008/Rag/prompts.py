"""GFC2008 Rag Prompts

RAG variant prompts: imports system prompts from RuleLLM and adds RAG user template.

The re-exported ``*_SYS`` constants already carry the ``limit_order`` FORMAT_TAIL
concatenated at definition site inside :mod:`examples.GFC2008.RuleLLM.prompts`,
so no additional format composition is needed here.
"""

from examples.GFC2008.RuleLLM.prompts import (
    RULELLM_MBS_ORIGINATOR_SYS as RAGLLM_MBS_ORIGINATOR_SYS,
    RULELLM_RATING_AGENCY_SYS as RAGLLM_RATING_AGENCY_SYS,
    RULELLM_LEVERAGED_INVESTOR_SYS as RAGLLM_LEVERAGED_INVESTOR_SYS,
    RULELLM_DISTRESSED_BUYER_SYS as RAGLLM_DISTRESSED_BUYER_SYS,
    RULELLM_REGULATOR_SYS as RAGLLM_REGULATOR_SYS,
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

Using the retrieved knowledge and your trading rules, provide your decision."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
