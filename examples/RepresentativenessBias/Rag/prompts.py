"""RepresentativenessBias Rag Prompts

System prompts for Rag-driven agents in the RepresentativenessBias simulation.
Imports base system prompts from RuleLLM and adds RAG context injection.
"""

from examples.RepresentativenessBias.RuleLLM.prompts import (
    RULELLM_BAYESIAN_UPDATER_SYS,
    RULELLM_CATEGORY_OVERGENERALIZER_SYS,
    RULELLM_CONTRARIAN_STATISTICAL_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_PATTERN_MATCHER_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE ==
{rag_context}

== CURRENT MARKET STATE (Round {round_num}) ==
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Using the retrieved knowledge and current market state, apply your decision rules.

<analysis>Integrate retrieved knowledge with current market conditions to determine action</analysis>
<decision>{{"action": "buy", "bid_price": 100.0, "quantity": 1, "reasoning": "brief rationale"}}</decision>

Output format requirement: the <decision> JSON must include action ("buy", "sell", or "hold"), bid_price (current or limit price as a number), quantity (number of shares/contracts), and reasoning (brief string)."""

__all__ = [
    "RULELLM_PATTERN_MATCHER_SYS",
    "RULELLM_CATEGORY_OVERGENERALIZER_SYS",
    "RULELLM_BAYESIAN_UPDATER_SYS",
    "RULELLM_CONTRARIAN_STATISTICAL_SYS",
    "RULELLM_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
