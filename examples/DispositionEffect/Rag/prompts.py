"""DispositionEffect Rag prompts - reuses RuleLLM system prompts with RAG user template."""

from examples.DispositionEffect.RuleLLM.prompts import (
    RULELLM_DISPOSITION_BIASED_SYS,
    RULELLM_RATIONAL_SYS,
    RULELLM_TAX_AWARE_SYS,
    RULELLM_INSTITUTIONAL_SYS,
    RULELLM_LOSS_AVERSE_SYS,
    RULELLM_USER_TEMPLATE,
)

# Re-export system prompts with RAG_ prefix for players.yml compatibility
RAG_DISPOSITION_BIASED_SYS = RULELLM_DISPOSITION_BIASED_SYS
RAG_RATIONAL_SYS = RULELLM_RATIONAL_SYS
RAG_TAX_AWARE_SYS = RULELLM_TAX_AWARE_SYS
RAG_INSTITUTIONAL_SYS = RULELLM_INSTITUTIONAL_SYS
RAG_LOSS_AVERSE_SYS = RULELLM_LOSS_AVERSE_SYS

# RAG user template — extends RuleLLM template with {rag_context} placeholder.
# Context is injected via .format(rag_context=...) in players.py decide().
RAG_USER_TEMPLATE = (
    RULELLM_USER_TEMPLATE
    + """
== RELEVANT KNOWLEDGE (from RAG retrieval) ==
{rag_context}
IMPORTANT: bid_price must be strictly positive. For hold, use the current price shown above as bid_price; never output bid_price: 0.
"""
)

# Alias required by players.yml (user_message: "...prompts:LLM_USER_TEMPLATE")
LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
