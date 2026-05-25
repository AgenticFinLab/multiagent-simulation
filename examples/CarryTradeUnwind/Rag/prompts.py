"""CarryTradeUnwind Rag Prompts — reuses RuleLLM system prompts + RAG context template."""

from examples.CarryTradeUnwind.RuleLLM.prompts import (  # noqa: F401
    RULELLM_CARRY_TRADER_SYS,
    RULELLM_LEVERAGED_CARRY_FUND_SYS,
    RULELLM_FUNDING_CURRENCY_BUYER_SYS,
    RULELLM_HEDGED_CARRY_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_CARRY_TRADER_SYS = RULELLM_CARRY_TRADER_SYS
RAG_LEVERAGED_CARRY_FUND_SYS = RULELLM_LEVERAGED_CARRY_FUND_SYS
RAG_FUNDING_CURRENCY_BUYER_SYS = RULELLM_FUNDING_CURRENCY_BUYER_SYS
RAG_HEDGED_CARRY_TRADER_SYS = RULELLM_HEDGED_CARRY_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current FX Market State (Round {round}):
- Current Exchange Rate: {price:.4f}
- Fundamental Value: {fundamental:.4f}
- Rate Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} units
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules and the domain knowledge above to decide your action.
Respond with <analysis>...</analysis> and <decision>{{"action": "buy", "bid_price": {price:.4f}, "quantity": 1, "reasoning": "brief rationale"}}</decision>.
IMPORTANT: bid_price must be strictly positive. For hold, use the current price/exchange rate ({price:.4f}) as bid_price; never output bid_price: 0.

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
