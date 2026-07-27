"""DotComBubble Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.DotComBubble.RuleLLM.prompts import (  # noqa: F401
    RULELLM_NEW_ECONOMY_EVANGELIST_SYS,
    RULELLM_IPO_FLIPPER_SYS,
    RULELLM_MOMENTUM_FOLLOWER_SYS,
    RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS,
    RULELLM_SHORT_SELLER_SYS,
)

RAG_NEW_ECONOMY_EVANGELIST_SYS = RULELLM_NEW_ECONOMY_EVANGELIST_SYS
RAG_IPO_FLIPPER_SYS = RULELLM_IPO_FLIPPER_SYS
RAG_MOMENTUM_FOLLOWER_SYS = RULELLM_MOMENTUM_FOLLOWER_SYS
RAG_SKEPTICAL_VALUE_INVESTOR_SYS = RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS
RAG_SHORT_SELLER_SYS = RULELLM_SHORT_SELLER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules and the domain knowledge above to decide your action.
Respond with <analysis>...</analysis> and a <decision> JSON object containing
action, bid_price, quantity, and reasoning.
IMPORTANT: bid_price must be strictly positive; for hold, use the current price
as bid_price; never output bid_price: 0.

Output format requirement: action must be "buy", "sell", or "hold"; bid_price
must be a number; quantity must be a number of shares; reasoning must be a
non-empty string."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
