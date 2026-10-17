"""Agent templates — the contract for writing a player.

This package is part of the **platform**. It defines *how a player is written*,
not *which players exist*:

  * :class:`~masim.agents._base.CanonicalRulePlayer` — deterministic, formula
    driven; a subclass implements ``decide_order``.
  * :class:`~masim.agents._base.CanonicalLLMPlayer` — decision delegated to an
    LLM; a subclass supplies prompts and parsing.
  * :class:`~masim.agents._rag_base.CanonicalRagPlayer` — the LLM base plus
    optional retrieval grounding.
  * :class:`~masim.agents._coordinator_base.CanonicalMarketCoordinator` — the
    world-facing side: aggregates order flow and forms the market signal.

Mixins supplied here and mixed into the bases: ``SeededRngMixin`` (per-agent
salted RNG), ``MarketPerceptionMixin`` (per-source market signals),
``BookkeepingMixin`` (portfolio + fill model).

The concrete archetype library — 209 implementations and their profiles — is
**not** part of the platform and lives in the top-level ``agent_library``
package. A scenario imports its players from there, or defines its own by
subclassing one of the bases above.
"""


from masim.format.state import StandardMarketState as StandardMarketState
from masim.agents._base import (
    CanonicalLLMPlayer as CanonicalLLMPlayer,
    CanonicalRulePlayer as CanonicalRulePlayer,
)
from masim.agents._rag_base import (
    RAG_FALLBACK_MESSAGE as RAG_FALLBACK_MESSAGE,
    CanonicalRagPlayer as CanonicalRagPlayer,
)
from masim.agents._coordinator_base import CanonicalMarketCoordinator as CanonicalMarketCoordinator

# The template surface, explicitly. The concrete archetype library builds its
# own ``__all__`` in ``agent_library``; keeping this list static means a typo in
# a re-export is caught here rather than at a scenario's import time.
__all__ = [
    "StandardMarketState",
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
    "CanonicalRagPlayer",
    "CanonicalMarketCoordinator",
    "RAG_FALLBACK_MESSAGE",
]
