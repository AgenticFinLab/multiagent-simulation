"""LUNACollapse RuleLLM Prompts

System prompts for RuleLLM agents using LangChainAPIInference (lmbase).
"""

from examples.LUNACollapse.LLM.prompts import (
    LLM_STABLECOINHOLDER_PROMPT as RULELLM_STABLECOINHOLDER_PROMPT,
    LLM_ARBITRAGEUR_PROMPT as RULELLM_ARBITRAGEUR_PROMPT,
    LLM_DEFILENDER_PROMPT as RULELLM_DEFILENDER_PROMPT,
    LLM_ANCHORDEPOSITOR_PROMPT as RULELLM_ANCHORDEPOSITOR_PROMPT,
    LLM_VALUEBUYER_PROMPT as RULELLM_VALUEBUYER_PROMPT,
)

__all__ = [
    "RULELLM_STABLECOINHOLDER_PROMPT",
    "RULELLM_ARBITRAGEUR_PROMPT",
    "RULELLM_DEFILENDER_PROMPT",
    "RULELLM_ANCHORDEPOSITOR_PROMPT",
    "RULELLM_VALUEBUYER_PROMPT",
]

RULELLM_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Apply your persona and decision rules to decide your action.
Respond with <analysis>...</analysis> and <decision>{{"action": "buy"|"sell"|"hold", "bid_price": <number>, "quantity": <number>, "reasoning": "brief rationale"}}</decision>.
"""
