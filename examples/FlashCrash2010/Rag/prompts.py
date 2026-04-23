"""FlashCrash2010 Rag Prompts - RAG-augmented Rule+LLM System and User Message Templates

Design principle (extends FlashCrash2010 RuleLLM):
    Each agent's system prompt retains the two sections from RuleLLM:
        1. PERSONA     — who you are: identity, style, risk attitude
        2. DECISION RULES — explicit quantitative rules from the rule-based counterpart

    The user message template ADDS a third section:
        3. RELEVANT KNOWLEDGE — top-k chunks retrieved from the agent's personal
           RAG library, dynamically injected at each round.

Agents:
    - RAG HFT Market Maker   → HFT liquidity withdrawal rules + RAG
    - RAG Momentum Chaser    → Trend-following momentum rules + RAG
    - RAG Fundamental Trader → Value deviation rules + RAG
    - RAG Stop-Loss Trader   → Stop-loss trigger rules + RAG
    - RAG Noise Trader       → Random trading rules + RAG
"""

from examples.FlashCrash2010.RuleLLM.prompts import (  # noqa: F401
    RULELLM_HFT_MARKET_MAKER_SYS as RAGLLM_HFT_MARKET_MAKER_SYS,
    RULELLM_MOMENTUM_CHASER_SYS as RAGLLM_MOMENTUM_CHASER_SYS,
    RULELLM_FUNDAMENTAL_SYS as RAGLLM_FUNDAMENTAL_SYS,
    RULELLM_STOP_LOSS_SYS as RAGLLM_STOP_LOSS_SYS,
    RULELLM_NOISE_TRADER_SYS as RAGLLM_NOISE_TRADER_SYS,
)

# =============================================================================
# RAG User Message Template (includes {rag_context} section)
# =============================================================================

RAG_USER_TEMPLATE = """
== RELEVANT KNOWLEDGE (from your personal reference library) ==
{rag_context}

== MARKET STATE (Round {round}) ==
- Current Price:    ${price:.2f}
- Previous Price:   ${prev_price:.2f}
- Return:           {return_pct:+.2f}%
- Fundamental:      ${fundamental:.2f}
- Deviation:        {deviation:+.2f}%
- Bid-Ask Spread:   {spread:.4f}
- Order Book Depth: {depth:.0f}
- Volatility:       {volatility:.4f}
- Recent Prices:    {recent_prices}

== YOUR PORTFOLIO ==
- Cash: ${cash:.2f}
- Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Apply your DECISION RULES, informed by the relevant knowledge above, and output your trade decision.

First output your reasoning inside <think>...</think> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {{"action": "buy" | "sell" | "hold", "bid_price": <your price as NUMBER>, "quantity": <shares as NUMBER, +buy/-sell>, "reasoning": "<brief>"}}
IMPORTANT: bid_price and quantity MUST be numeric values, NOT expressions.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
