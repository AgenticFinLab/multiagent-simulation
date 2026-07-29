"""AnchoringEffect Rag Prompts

RAG-augmented prompts for agents using domain knowledge retrieval.
System prompts combine behavioral persona, quantitative rules, and RAG context injection.

Construction rule (implement-simulation-skill.md — Rag variant):
    System prompts are identical to RuleLLM (== PERSONA == + == DECISION RULES ==).
    User prompt template adds {rag_context} placeholder after portfolio state.
    If no documents are retrieved, inject: "(No relevant knowledge retrieved this round.)"

Format tail (analysis/decision tag block + JSON schema block) is imported
from :mod:`masim.format.limit_order` and concatenated at DEFINITION SITE of
each RuleLLM system prompt (which this module re-exports)::

    RAG_XXX_SYS = RULELLM_XXX_SYS   # already _XXX_PERSONA + "\\n\\n" + FORMAT_TAIL

Runtime (:mod:`masim.utils.llm_utils.robust_llm_call`) sends this exact
string to the model — no hidden framework composition — and validates the
response through ``limit_order.validate_decision``; a schema-invalid reply
triggers a retry rather than silent field defaulting.
"""

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

# RAG system prompts are identical to RuleLLM system prompts (persona +
# decision rules + FORMAT_TAIL). The variant-specific knowledge injection is
# handled in the user template via the {rag_context} placeholder.
RAG_ANCHORED_TRADER_SYS = RULELLM_ANCHORED_TRADER_SYS
RAG_HISTORICAL_ANCHOR_SYS = RULELLM_HISTORICAL_ANCHOR_SYS
RAG_RATIONAL_UPDATER_SYS = RULELLM_RATIONAL_UPDATER_SYS
RAG_MOMENTUM_TRADER_SYS = RULELLM_MOMENTUM_TRADER_SYS
RAG_NOISE_TRADER_SYS = RULELLM_NOISE_TRADER_SYS
RAG_DISPOSITION_TRADER_SYS = RULELLM_DISPOSITION_TRADER_SYS
RAG_CONTRARIAN_TRADER_SYS = RULELLM_CONTRARIAN_TRADER_SYS
RAG_FUNDAMENTAL_ANALYST_SYS = RULELLM_FUNDAMENTAL_ANALYST_SYS
RAG_LIQUIDITY_PROVIDER_SYS = RULELLM_LIQUIDITY_PROVIDER_SYS

# -----------------------------------------------------------------------------
# User Prompt Template
# Placeholders: {round}, {price}, {prev_price}, {fundamental}, {price_change},
#               {deviation}, {cash}, {position}, {portfolio_value}, {rag_context}
# -----------------------------------------------------------------------------
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
    "Make your trading decision as instructed in your system prompt, "
    "incorporating the domain knowledge above where relevant.\n"
)
