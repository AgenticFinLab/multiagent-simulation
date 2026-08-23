"""TulipMania Rule Simulation — canonical re-export.

Historical PascalCase class names are preserved so the existing
``configs/TulipMania/Rule/players.yml`` continues to resolve without edits,
but every agent is now a thin alias to a canonical implementation in
:mod:`masim.agents`.  No simulation logic, cash bookkeeping, or LLM plumbing
lives here.

Contract
--------
* ``Market`` → :class:`masim.agents.MarketStockStandardPriceImpact`
  (archetype ``stock-standard-price-impact``).
* Each investor aliases the shipped ``Rule<Camel>`` class whose ``STRATEGY``
  matches its AGENT_POOL kebab stem.
"""

from __future__ import annotations

from masim.agents import (
    MarketStockStandardPriceImpact as Market,
    RuleEarlyExitTrader as EarlyExitTrader,
    RuleIntrinsicValueTrader as IntrinsicValueTrader,
    RuleNoiseTrader as NoiseTrader,
    RuleSocialProofFollower as SocialProofFollower,
    RuleTrendChaser as TrendChaser,
)

__all__ = [
    "Market",
    "TrendChaser",
    "SocialProofFollower",
    "IntrinsicValueTrader",
    "EarlyExitTrader",
    "NoiseTrader",
]
