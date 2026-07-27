"""ArchegosCollapse Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
"""

from examples.ArchegosCollapse.RuleLLM.prompts import (
    RULELLM_CONCENTRATED_FUND_SYS,
    RULELLM_PRIME_BROKER_FIRST_MOVER_SYS,
    RULELLM_PRIME_BROKER_DELAYED_LIQUIDATOR_SYS,
    RULELLM_BLOCK_TRADE_BUYER_SYS,
    RULELLM_INFORMATION_TRADER_SYS,
    RULELLM_USER_TEMPLATE,
)

RAG_CONCENTRATED_FUND_SYS = RULELLM_CONCENTRATED_FUND_SYS
RAG_PRIME_BROKER_FIRST_MOVER_SYS = RULELLM_PRIME_BROKER_FIRST_MOVER_SYS
RAG_PRIME_BROKER_DELAYED_LIQUIDATOR_SYS = RULELLM_PRIME_BROKER_DELAYED_LIQUIDATOR_SYS
RAG_BLOCK_TRADE_BUYER_SYS = RULELLM_BLOCK_TRADE_BUYER_SYS
RAG_INFORMATION_TRADER_SYS = RULELLM_INFORMATION_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Previous Price: ${prev_price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position:.2f} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules to this market state, incorporating the domain knowledge above.
Show your calculations in the analysis section.
Respond with your analysis in <analysis>...</analysis> tags followed by your decision in \
<decision>...</decision> tags.
The decision JSON must contain: action ("buy", "sell", or "hold"), bid_price (float), \
IMPORTANT: bid_price must be strictly positive; for hold, use the current price as bid_price; never output bid_price: 0.
quantity (float, positive), and reasoning (string).
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
