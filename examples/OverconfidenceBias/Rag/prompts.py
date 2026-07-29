"""OverconfidenceBias Rag Prompts.

Re-exports RuleLLM system prompts (already composed as
``_PERSONA + "\\n\\n" + FORMAT_TAIL`` at definition site in
:mod:`examples.OverconfidenceBias.RuleLLM.prompts`) and adds a RAG-aware
user template that injects retrieved knowledge.

Format tail convention: every scenario's system-prompt constant is built by
concatenating a private ``_XXX_PERSONA`` string with
:data:`masim.format.limit_order.FORMAT_TAIL` at DEFINITION SITE. Because the
persona + tail are already baked into ``RULELLM_XXX_SYS``, this module does
not need to touch ``FORMAT_TAIL`` directly — it only imports it to make the
convention explicit and to satisfy static analysis if a future prompt is
added here.

Public constant names retain the historical ``_SYS`` suffix because
``players.py`` binds against those names.
"""

from masim.format.limit_order import FORMAT_TAIL  # noqa: F401  (format-tail convention)

from examples.OverconfidenceBias.RuleLLM.prompts import (
    RULELLM_OVERCONFIDENT_TRADER_SYS,
    RULELLM_SELF_ATTRIBUTOR_SYS,
    RULELLM_CALIBRATED_TRADER_SYS,
    RULELLM_CONTRARIAN_INVESTOR_SYS,
    RULELLM_NOISE_TRADER_SYS,
)

RAG_USER_TEMPLATE = """== RELEVANT KNOWLEDGE ==
{rag_context}

Current Market State (Round {round_num}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2f}%
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Make your trading decision as instructed in your system prompt, informed by the relevant knowledge above.
"""

__all__ = [
    "RULELLM_OVERCONFIDENT_TRADER_SYS",
    "RULELLM_SELF_ATTRIBUTOR_SYS",
    "RULELLM_CALIBRATED_TRADER_SYS",
    "RULELLM_CONTRARIAN_INVESTOR_SYS",
    "RULELLM_NOISE_TRADER_SYS",
    "RAG_USER_TEMPLATE",
]
