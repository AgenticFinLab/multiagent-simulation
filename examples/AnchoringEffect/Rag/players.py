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

    STRATEGY is intentionally not re-declared on this base. The framework
    parent :class:`CanonicalRagPlayer` already carries a placeholder
    ``STRATEGY = "CanonicalRagPlayer"`` default; redeclaring the same
    placeholder here would be pure duplication (and would blur which
    class owns which archetype). Every concrete subclass below MUST
    override STRATEGY with its AGENT_POOL kebab stem so cross-variant
    analytics group Rule / LLM / RuleLLM / Rag runs by archetype.
    """

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


__all__ = [
    "Market",
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
