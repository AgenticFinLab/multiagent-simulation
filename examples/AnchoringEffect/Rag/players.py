"""AnchoringEffect Rag Simulation — thin scenario layer over CanonicalRagPlayer.

The RAG variant of AnchoringEffect differs from the plain LLM variant
only in three respects:

* The user template contains an extra ``{rag_context}`` placeholder that
  must be populated from a per-agent knowledge index each round.
* The retrieval query should mention the AnchoringEffect signal
  vocabulary (``anchoring bias``, ``price``, ``fundamental``,
  ``deviation``) so the RAG chunks that come back stay on-topic.
* Every persona is served by a distinct ``RagLLM<Camel>`` class so the
  yaml can pin them by classpath.

All of those requirements are already covered by
:class:`masim.agents.CanonicalRagPlayer`; this module simply subclasses
it once per archetype, sets ``STRATEGY`` to the shipped LLM/Rule
sibling's kebab stem (so downstream analytics group RAG runs with the
same archetype), and overrides :meth:`_build_rag_query` on a shared
scenario base to inject the anchoring-bias vocabulary.

No LLM loop, no cash bookkeeping, no ``bid_price <= 0 → state.price``
silent fallback, and no RAG-store bootstrap logic lives here — every
one of those lives in :mod:`masim.agents._rag_base` and
:mod:`masim.format.finalize`.
"""

from __future__ import annotations

from masim.agents import CanonicalRagPlayer
from masim.format.state import StandardMarketState

# Coordinator (rule-executed) — inherited from the Rule module which
# re-exports :class:`masim.agents.MarketStockStandardPriceImpact`.
from examples.AnchoringEffect.Rule.players import Market


class _AnchoringRagBase(CanonicalRagPlayer):
    """Scenario-specific RAG query for the AnchoringEffect deck.

    Overrides only :meth:`_build_rag_query` so retrieval mentions
    ``anchoring bias`` and the same market signals the LLM prompt
    consumes.  All infrastructure (index bootstrap, prompt injection,
    schema-validated retry, order finalisation) is inherited unchanged.
    """

    # Archetype STRATEGY is set on each concrete subclass below so
    # analytics can group across Rule / LLM / RuleLLM / Rag runs by
    # the AGENT_POOL kebab stem.
    STRATEGY: str = "CanonicalRagPlayer"

    def _build_rag_query(self, state: StandardMarketState) -> str:
        parts = [
            "anchoring bias trading strategy",
            f"price={state.price:.4g}",
            f"prev_price={state.prev_price:.4g}",
        ]
        if state.fundamental == state.fundamental:  # not NaN
            parts.append(f"fundamental={state.fundamental:.4g}")
        if state.deviation == state.deviation:  # not NaN
            parts.append(f"deviation={state.deviation:+.2%}")
        return "; ".join(parts)


class RagLLMAnchoredTrader(_AnchoringRagBase):
    """RAG-augmented anchored trader — Tversky & Kahneman (1974)."""

    STRATEGY = "anchored-trader"


class RagLLMHistoricalAnchor(_AnchoringRagBase):
    """RAG-augmented historical-anchor trader."""

    STRATEGY = "historical-anchor"


class RagLLMRationalUpdater(_AnchoringRagBase):
    """RAG-augmented Bayesian benchmark trader."""

    STRATEGY = "rational-updater"


class RagLLMMomentumTrader(_AnchoringRagBase):
    """RAG-augmented momentum trader."""

    STRATEGY = "momentum-trader"


class RagLLMNoiseTrader(_AnchoringRagBase):
    """RAG-augmented noise trader."""

    STRATEGY = "noise-trader"


class RagLLMDispositionTrader(_AnchoringRagBase):
    """RAG-augmented disposition (Prospect-Theory) trader."""

    STRATEGY = "disposition-trader"


class RagLLMContrarianTrader(_AnchoringRagBase):
    """RAG-augmented contrarian trader."""

    STRATEGY = "contrarian-trader"


class RagLLMFundamentalAnalyst(_AnchoringRagBase):
    """RAG-augmented fundamental analyst."""

    STRATEGY = "fundamental-analyst"


class RagLLMLiquidityProvider(_AnchoringRagBase):
    """RAG-augmented passive liquidity provider."""

    STRATEGY = "liquidity-provider"


# Historical alias kept so downstream imports of ``LLMInvestor`` from
# the RAG module (rare, but present in legacy notebooks) still resolve.
RagLLMInvestor = _AnchoringRagBase


__all__ = [
    "Market",
    "RagLLMInvestor",
    "RagLLMAnchoredTrader",
    "RagLLMHistoricalAnchor",
    "RagLLMRationalUpdater",
    "RagLLMMomentumTrader",
    "RagLLMNoiseTrader",
    "RagLLMDispositionTrader",
    "RagLLMContrarianTrader",
    "RagLLMFundamentalAnalyst",
    "RagLLMLiquidityProvider",
]
