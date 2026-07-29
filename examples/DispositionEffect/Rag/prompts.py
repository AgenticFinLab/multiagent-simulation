"""DispositionEffect Rag prompts - reuses RuleLLM personas with RAG user template.

Format tail (analysis/decision tag block + JSON schema block) is imported from
``masim.format.limit_order`` and concatenated at DEFINITION SITE so the full
system prompt is visible in one place:

    RAG_XXX_SYS = _RAG_XXX_PERSONA + "\\n\\n" + FORMAT_TAIL

The persona bodies mirror the RuleLLM counterparts (imported privately) so
the Rag agents share behavioral definitions with their non-RAG twins while
producing a single, self-contained system string sent to the model. Runtime
(:mod:`masim.utils.llm_utils.robust_llm_call`) validates the response via
``limit_order.validate_decision``; a schema-invalid reply triggers a retry.
"""

from masim.format.limit_order import FORMAT_TAIL

from examples.DispositionEffect.RuleLLM.prompts import (
    _RULELLM_DISPOSITION_BIASED_PERSONA as _RAG_DISPOSITION_BIASED_PERSONA,
    _RULELLM_RATIONAL_PERSONA as _RAG_RATIONAL_PERSONA,
    _RULELLM_TAX_AWARE_PERSONA as _RAG_TAX_AWARE_PERSONA,
    _RULELLM_INSTITUTIONAL_PERSONA as _RAG_INSTITUTIONAL_PERSONA,
    RULELLM_USER_TEMPLATE,
)

# =============================================================================
# Rag system prompts — persona (shared with RuleLLM) + FORMAT_TAIL
# =============================================================================

RAG_DISPOSITION_BIASED_SYS = _RAG_DISPOSITION_BIASED_PERSONA + "\n\n" + FORMAT_TAIL
RAG_RATIONAL_SYS = _RAG_RATIONAL_PERSONA + "\n\n" + FORMAT_TAIL
RAG_TAX_AWARE_SYS = _RAG_TAX_AWARE_PERSONA + "\n\n" + FORMAT_TAIL
RAG_INSTITUTIONAL_SYS = _RAG_INSTITUTIONAL_PERSONA + "\n\n" + FORMAT_TAIL

# =============================================================================
# Rag Index Holder (Passive Benchmark)
# =============================================================================

_RAG_INDEX_HOLDER_PERSONA = """== PERSONA ==
You are a passive index holder. You accept market returns and do not time
realized gains or losses. Retrieved material may inform your explanation, but
it must never cause an active trade.

== DECISION RULES ==
In every market state, choose hold with quantity 0 and the current positive
market price as bid_price."""

RAG_INDEX_HOLDER_SYS = _RAG_INDEX_HOLDER_PERSONA + "\n\n" + FORMAT_TAIL

# =============================================================================
# RAG User Message Template
# Extends RuleLLM template with a {rag_context} placeholder injected by
# players.py decide() via .format(rag_context=...).
# =============================================================================

RAG_USER_TEMPLATE = (
    RULELLM_USER_TEMPLATE
    + """
== RELEVANT KNOWLEDGE (from RAG retrieval) ==
{rag_context}
"""
)

# Alias required by players.yml (user_message: "...prompts:LLM_USER_TEMPLATE")
LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
