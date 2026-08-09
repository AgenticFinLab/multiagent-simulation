"""AnchoringEffect LLM Simulation — pure canonical re-export.

Every archetype is a thin alias to the shipped ``LLM<Camel>`` class in
:mod:`masim.agents`.  Canonical LLM plumbing (persona prompt loading via
``load_prompt``, retrying via ``robust_llm_call`` with the
``AnchoringEffect``-registered ``validate_decision``, fail-loud finalise
via :mod:`masim.format.finalize`) is entirely inherited — this module
contains **no** inline LLM loop, no silent ``bid_price`` fallback, and no
cash bookkeeping.

Contract
--------

* ``Market`` — imported from :mod:`examples.AnchoringEffect.Rule.players`
  which itself re-exports :class:`masim.agents.MarketStockStandardPriceImpact`.
* ``LLMInvestor`` alias — retained so downstream references to the base
  class still resolve; it is now literally
  :class:`masim.agents.CanonicalLLMPlayer`.
* Every ``LLM<Camel>`` archetype below aliases the shipped canonical
  ``LLM<Camel>`` class whose ``STRATEGY`` attribute equals the
  AGENT_POOL kebab stem.

Historical yaml references
--------------------------

``configs/AnchoringEffect/LLM/players.yml`` still pins each class by
``"examples.AnchoringEffect.LLM.players:LLM<Camel>"``.  The aliases below
preserve those exact names, so no yaml or bundle edit is required.
"""

from __future__ import annotations

from masim.agents import CanonicalLLMPlayer as LLMInvestor
from masim.agents import (
    LLMAnchoredTrader,
    LLMContrarianTrader,
    LLMDispositionTrader,
    LLMFundamentalAnalyst,
    LLMHistoricalAnchor,
    LLMLiquidityProvider,
    LLMMomentumTrader,
    LLMNoiseTrader,
    LLMRationalUpdater,
)

# Coordinator (rule-executed even in LLM-participant runs) — the Rule
# module already aliases the canonical Market coordinator, so we simply
# re-export it here to keep the historical yaml classpath valid.
from examples.AnchoringEffect.Rule.players import Market

__all__ = [
    "Market",
    "LLMInvestor",
    "LLMAnchoredTrader",
    "LLMHistoricalAnchor",
    "LLMRationalUpdater",
    "LLMMomentumTrader",
    "LLMNoiseTrader",
    "LLMDispositionTrader",
    "LLMContrarianTrader",
    "LLMFundamentalAnalyst",
    "LLMLiquidityProvider",
]
