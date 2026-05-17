"""LTCMCollapse RuleLLM Prompts

System prompts for RuleLLM agents using LangChainAPIInference (lmbase).
Each prompt defines an investor personality WITHOUT naming the specific crisis.
"""

from examples.LTCMCollapse.LLM.prompts import (
    LLM_CONVERGENCEARBITRAGEUR_PROMPT as RULELLM_CONVERGENCEARBITRAGEUR_PROMPT,
    LLM_LEVERAGETRADER_PROMPT as RULELLM_LEVERAGETRADER_PROMPT,
    LLM_RISKMANAGER_PROMPT as RULELLM_RISKMANAGER_PROMPT,
    LLM_LIQUIDITYPROVIDER_PROMPT as RULELLM_LIQUIDITYPROVIDER_PROMPT,
    LLM_CENTRALBANK_PROMPT as RULELLM_CENTRALBANK_PROMPT,
)

__all__ = [
    "RULELLM_CONVERGENCEARBITRAGEUR_PROMPT",
    "RULELLM_LEVERAGETRADER_PROMPT",
    "RULELLM_RISKMANAGER_PROMPT",
    "RULELLM_LIQUIDITYPROVIDER_PROMPT",
    "RULELLM_CENTRALBANK_PROMPT",
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
