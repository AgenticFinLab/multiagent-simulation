"""DotComBubble Rag Prompts — reuses RuleLLM system prompts + RAG context template.

The RuleLLM ``prompts.py`` composes each ``RULELLM_XXX_SYS`` at definition site
as ``_XXX_PERSONA + "\\n\\n" + FORMAT_TAIL`` (where ``FORMAT_TAIL`` comes from
``masim.format.limit_order``). Aliasing here preserves that full composition —
no additional framework-side concatenation is performed at runtime.
"""

from masim.format.limit_order import FORMAT_TAIL  # noqa: F401  (re-exported for parity)

from examples.DotComBubble.RuleLLM.prompts import (  # noqa: F401
    RULELLM_NEW_ECONOMY_EVANGELIST_SYS,
    RULELLM_IPO_FLIPPER_SYS,
    RULELLM_MOMENTUM_FOLLOWER_SYS,
    RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS,
    RULELLM_SHORT_SELLER_SYS,
)

RAG_NEW_ECONOMY_EVANGELIST_SYS = RULELLM_NEW_ECONOMY_EVANGELIST_SYS
RAG_IPO_FLIPPER_SYS = RULELLM_IPO_FLIPPER_SYS
RAG_MOMENTUM_FOLLOWER_SYS = RULELLM_MOMENTUM_FOLLOWER_SYS
RAG_SKEPTICAL_VALUE_INVESTOR_SYS = RULELLM_SKEPTICAL_VALUE_INVESTOR_SYS
RAG_SHORT_SELLER_SYS = RULELLM_SHORT_SELLER_SYS

RAG_USER_TEMPLATE = """Current Market State (Round {round}):
- Current Price: ${price:.2f}
- Fundamental Value: ${fundamental:.2f}
- Price Deviation from Fundamental: {deviation:+.2%}
- Your Cash: ${cash:.2f}
- Your Position: {position} shares
- Portfolio Value: ${portfolio_value:.2f}

Relevant Domain Knowledge:
{rag_context}

Apply your trading rules and the domain knowledge above to decide your action.
"""

LLM_USER_TEMPLATE = RAG_USER_TEMPLATE
