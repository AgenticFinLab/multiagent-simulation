"""AvailabilityBias Rag Prompts"""

from examples.AvailabilityBias.RuleLLM.prompts import (
    RULELLM_RECENT_EVENT_OVERWEIGHTER_SYS,
    RULELLM_MEDIA_INFLUENCED_TRADER_SYS,
    RULELLM_SYSTEMATIC_ANALYST_SYS,
    RULELLM_VALUE_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_USER_TEMPLATE,
)

RAG_RECENT_EVENT_OVERWEIGHTER_SYS = RULELLM_RECENT_EVENT_OVERWEIGHTER_SYS
RAG_MEDIA_INFLUENCED_TRADER_SYS = RULELLM_MEDIA_INFLUENCED_TRADER_SYS
RAG_SYSTEMATIC_ANALYST_SYS = RULELLM_SYSTEMATIC_ANALYST_SYS
RAG_VALUE_TRADER_SYS = RULELLM_VALUE_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Previous Price: ${prev_price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Recent Return: {return_pct:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position:.2f} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules to this market state, incorporating the domain knowledge above.
Show your calculations in the thinking section.
Respond with your thinking in <think>...</think> tags followed by your decision in \
<decision>...</decision> tags.
The decision JSON must contain: action ("buy", "sell", or "hold"), bid_price (float), \
quantity (float, positive), and reasoning (string).
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
