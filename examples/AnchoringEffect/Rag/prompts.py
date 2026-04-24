"""AnchoringEffect Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
System prompts combine behavioral persona, quantitative rules, and RAG context injection.
"""

from examples.AnchoringEffect.RuleLLM.prompts import (
    RULELLM_ANCHORED_TRADER_SYS,
    RULELLM_HISTORICAL_ANCHOR_SYS,
    RULELLM_RATIONAL_UPDATER_SYS,
    RULELLM_MOMENTUM_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_USER_TEMPLATE,
)

RAG_ANCHORED_TRADER_SYS = RULELLM_ANCHORED_TRADER_SYS
RAG_HISTORICAL_ANCHOR_SYS = RULELLM_HISTORICAL_ANCHOR_SYS
RAG_RATIONAL_UPDATER_SYS = RULELLM_RATIONAL_UPDATER_SYS
RAG_MOMENTUM_TRADER_SYS = RULELLM_MOMENTUM_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Previous Price: ${prev_price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position:.2f} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules to this market state, incorporating the domain knowledge above.
Show your calculations in the thinking section.
Respond with your thinking in <analysis>...</analysis> tags followed by your decision in \
<decision>...</decision> tags.
The decision JSON must contain: action ("buy", "sell", or "hold"), bid_price (float), \
quantity (float, positive), and reasoning (string).
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
