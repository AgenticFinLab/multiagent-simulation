"""AnchoringEffect Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
System prompts combine behavioral persona, quantitative rules, and RAG context injection.

Construction rule (implement-simulation-skill.md — Rag variant):
    System prompts are identical to RuleLLM (== PERSONA == + == DECISION RULES ==).
    User prompt template adds {rag_context} placeholder after portfolio state.
    If no documents are retrieved, inject: "(No relevant knowledge retrieved this round.)"

Output format required for all agents:
    <analysis>...</analysis><decision>JSON</decision>
    JSON fields: action ("buy"|"sell"|"hold"), bid_price (float), quantity (float), reasoning (string)
"""

from masim.format.base_prompts import (
    ANALYSIS_DECISION_TAG,
    RAG_APPLY_RULES_WITH_KNOWLEDGE,
)
from masim.format.order_prompts import (
    DECISION_FORMAT_INSTRUCTION,
    DECISION_FORMAT_INSTRUCTION_TPL,
)

from examples.AnchoringEffect.RuleLLM.prompts import (
    RULELLM_ANCHORED_TRADER_SYS,
    RULELLM_HISTORICAL_ANCHOR_SYS,
    RULELLM_RATIONAL_UPDATER_SYS,
    RULELLM_MOMENTUM_TRADER_SYS,
    RULELLM_NOISE_TRADER_SYS,
    RULELLM_DISPOSITION_TRADER_SYS,
    RULELLM_CONTRARIAN_TRADER_SYS,
    RULELLM_FUNDAMENTAL_ANALYST_SYS,
    RULELLM_LIQUIDITY_PROVIDER_SYS,
)

# RAG system prompts are identical to RuleLLM system prompts.
# The variant-specific knowledge injection is handled in the user template.
RAG_ANCHORED_TRADER_SYS = RULELLM_ANCHORED_TRADER_SYS
RAG_HISTORICAL_ANCHOR_SYS = RULELLM_HISTORICAL_ANCHOR_SYS
RAG_RATIONAL_UPDATER_SYS = RULELLM_RATIONAL_UPDATER_SYS
RAG_MOMENTUM_TRADER_SYS = RULELLM_MOMENTUM_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS
RAG_DISPOSITION_TRADER_SYS = RULELLM_DISPOSITION_TRADER_SYS
RAG_CONTRARIAN_TRADER_SYS = RULELLM_CONTRARIAN_TRADER_SYS
RAG_FUNDAMENTAL_ANALYST_SYS = RULELLM_FUNDAMENTAL_ANALYST_SYS
RAG_LIQUIDITY_PROVIDER_SYS = RULELLM_LIQUIDITY_PROVIDER_SYS

RAG_USER_TEMPLATE = (
    "Current Market State (Round {round}):\n"
    "- Current Price: ${price:.2f}\n"
    "- Previous Price: ${prev_price:.2f}\n"
    "- Fundamental Value: ${fundamental:.2f}\n"
    "- Price Change: {price_change:+.2%}\n"
    "- Price Deviation from Fundamental: {deviation:+.2%}\n"
    "- Your Cash: ${cash:.2f}\n"
    "- Your Position: {position:.2f} shares\n"
    "- Portfolio Value: ${portfolio_value:.2f}\n\n"
    "Relevant Domain Knowledge:\n"
    "{rag_context}\n\n"
    + RAG_APPLY_RULES_WITH_KNOWLEDGE
    + "\n\n"
    + ANALYSIS_DECISION_TAG
    + "\n"
    + DECISION_FORMAT_INSTRUCTION_TPL
    + "\n"
)
