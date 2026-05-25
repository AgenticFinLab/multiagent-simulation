"""AsianFinancialCrisis Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
System prompts combine behavioral persona, quantitative rules, and RAG context injection.
"""

from examples.AsianFinancialCrisis.RuleLLM.prompts import (
    RULELLM_HOT_MONEY_FUNDER_SYS,
    RULELLM_CONTAGION_TRADER_SYS,
    RULELLM_IMF_RESCUER_SYS,
    RULELLM_VALUE_CONTRARIAN_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_USER_TEMPLATE,
)

RAG_HOT_MONEY_FUNDER_SYS = RULELLM_HOT_MONEY_FUNDER_SYS
RAG_CONTAGION_TRADER_SYS = RULELLM_CONTAGION_TRADER_SYS
RAG_IMF_RESCUER_SYS = RULELLM_IMF_RESCUER_SYS
RAG_VALUE_CONTRARIAN_SYS = RULELLM_VALUE_CONTRARIAN_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Previous Price: ${prev_price:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Fundamental Value: ${fundamental:.2f}
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
IMPORTANT: bid_price must be strictly positive; for hold, use the current price as bid_price; never output bid_price: 0.
quantity (float, non-negative), and reasoning (string).
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
