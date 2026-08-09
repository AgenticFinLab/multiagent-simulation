"""AnchoringEffect Rule-Based Simulation — pure canonical re-export.

Every class exposed here is a thin alias to a canonical implementation in
:mod:`masim.agents`.  The historical PascalCase names are preserved so the
existing ``configs/AnchoringEffect/Rule/players.yml`` (which pins classes
via ``"examples.AnchoringEffect.Rule.players:X"``) continues to resolve
without edits, but no simulation logic lives here anymore.

Contract
--------

* ``Market`` → :class:`masim.agents.MarketStockStandardPriceImpact`
  (archetype ``stock-standard-price-impact``; the yaml already declares
  this archetype and passes matching extras — ``initial_price``,
  ``fundamental_value``, ``price_impact``, ``mean_reversion``,
  ``noise_std``, ``record_path``, ``custom_state_hot_limit``).
* Every investor archetype below aliases the shipped ``Rule<Camel>``
  class whose ``STRATEGY`` attribute equals the AGENT_POOL kebab stem.

Any scenario-specific tuning still lives in ``players.yml`` via
``extras`` and ``persona.yml``.  This module contains **no** inline
formulas, no bookkeeping, and no LLM plumbing — that is by design and
matches the framework's "everything is an agent, everything is an
import" policy (see :mod:`masim.agents._base`,
:mod:`masim.agents._coordinator_base`, and
:mod:`masim.format.finalize`).
"""

from __future__ import annotations

from masim.agents import (
    # Coordinator (rule-executed even for LLM-participant simulations)
    MarketStockStandardPriceImpact as Market,
    # Rule investor archetypes
    RuleAnchoredTrader as AnchoredTrader,
    RuleContrarianTrader as ContrarianTrader,
    RuleDispositionTrader as DispositionTrader,
    RuleFundamentalAnalyst as FundamentalAnalyst,
    RuleHistoricalAnchor as HistoricalAnchor,
    RuleLiquidityProvider as LiquidityProvider,
    RuleMomentumTrader as MomentumTrader,
    RuleNoiseTrader as NoiseTrader,
    RuleRationalUpdater as RationalUpdater,
)

__all__ = [
    "Market",
    "AnchoredTrader",
    "HistoricalAnchor",
    "RationalUpdater",
    "MomentumTrader",
    "NoiseTrader",
    "DispositionTrader",
    "ContrarianTrader",
    "FundamentalAnalyst",
    "LiquidityProvider",
]
