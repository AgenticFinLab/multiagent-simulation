"""Shared prompt components for LLM-based trading agents."""

ANALYSIS_DECISION_TAG = (
    "Respond with your thinking in <analysis>...</analysis> tags "
    "followed by your decision in <decision>...</decision> tags."
)

TRADING_CONSTRAINTS = (
    "TRADING CONSTRAINTS:\n"
    "- Cannot spend more than your available cash\n"
    "- Cannot sell more shares than you currently hold"
)

MARKET_ACTION_QUESTION = (
    "Based on your trading personality and current market conditions, "
    "what action do you take?"
)

RULELLM_APPLY_RULES = (
    "Apply your DECISION RULES to this market state. "
    "Show your step-by-step calculations in the analysis section, "
    "then provide your decision."
)

RAG_APPLY_RULES_WITH_KNOWLEDGE = (
    "Apply your DECISION RULES to this market state, "
    "incorporating the domain knowledge above. "
    "Show your step-by-step calculations in the analysis section, "
    "then provide your decision."
)
