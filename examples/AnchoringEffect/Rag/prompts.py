"""AnchoringEffect Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
System prompts combine behavioral persona, quantitative rules, and RAG context injection.

Construction rule (create-example-skill.md — Rag variant):
    System prompts are identical to RuleLLM (== PERSONA == + == DECISION RULES ==).
    User prompt template adds {rag_context} placeholder after portfolio state.
    If no documents are retrieved, inject: "(No relevant knowledge retrieved this round.)"

Output format required for all agents:
    <analysis>...</analysis><decision>JSON</decision>
    JSON fields: action ("buy"|"sell"|"hold"), bid_price (float), quantity (float), reasoning (string)
"""

from examples.AnchoringEffect.RuleLLM.prompts import (
    RULELLM_ANCHORED_TRADER_SYS,
    RULELLM_HISTORICAL_ANCHOR_SYS,
    RULELLM_RATIONAL_UPDATER_SYS,
    RULELLM_MOMENTUM_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

# RAG system prompts are identical to RuleLLM system prompts.
# The variant-specific knowledge injection is handled in the user template.
RAG_ANCHORED_TRADER_SYS = RULELLM_ANCHORED_TRADER_SYS
RAG_HISTORICAL_ANCHOR_SYS = RULELLM_HISTORICAL_ANCHOR_SYS
RAG_RATIONAL_UPDATER_SYS = RULELLM_RATIONAL_UPDATER_SYS
RAG_MOMENTUM_TRADER_SYS = RULELLM_MOMENTUM_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Previous Price: ${prev_price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Change: {price_change:+.2%}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position:.2f} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your DECISION RULES to this market state, incorporating the domain knowledge above.
Show your step-by-step calculations in the analysis section, then provide your decision.

Respond with your thinking in <analysis>...</analysis> tags followed by your decision in
<decision>...</decision> tags.
The decision JSON must contain: action ("buy", "sell", or "hold"), bid_price (float, numeric value),
quantity (float, positive numeric value), and reasoning (string).
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas.
"""
