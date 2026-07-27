"""DispositionEffect Rag prompts - reuses RuleLLM system prompts with RAG user template."""

import re

from examples.DispositionEffect.RuleLLM.prompts import (
    RULELLM_DISPOSITION_BIASED_SYS,
    RULELLM_RATIONAL_SYS,
    RULELLM_TAX_AWARE_SYS,
    RULELLM_INSTITUTIONAL_SYS,
    RULELLM_USER_TEMPLATE,
)

def _canonicalize_rule_heading(prompt: str) -> str:
    """Normalize inherited RuleLLM headings to the literal contract marker."""
    return re.sub(
        r"== DECISION RULES \(([^\n]+)\) ==",
        r"== DECISION RULES ==\nRule source: \1.",
        prompt,
    )


# Re-export system prompts with canonical Rag headings for players.yml.
RAG_DISPOSITION_BIASED_SYS = _canonicalize_rule_heading(
    RULELLM_DISPOSITION_BIASED_SYS
)
RAG_RATIONAL_SYS = _canonicalize_rule_heading(RULELLM_RATIONAL_SYS)
RAG_TAX_AWARE_SYS = _canonicalize_rule_heading(RULELLM_TAX_AWARE_SYS)
RAG_INSTITUTIONAL_SYS = _canonicalize_rule_heading(RULELLM_INSTITUTIONAL_SYS)
RAG_INDEX_HOLDER_SYS = """== PERSONA ==
You are a passive index holder. You accept market returns and do not time
realized gains or losses. Retrieved material may inform your explanation, but
it must never cause an active trade.

== DECISION RULES ==
In every market state, choose hold with quantity 0 and the current positive
market price as bid_price.

First output reasoning inside <analysis>...</analysis>, then output the decision
inside <decision>...</decision>. The decision must be valid JSON with exactly
these fields: {"action": "hold", "bid_price": 100.0, "quantity": 0,
"reasoning": "brief explanation"}.
"""

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
