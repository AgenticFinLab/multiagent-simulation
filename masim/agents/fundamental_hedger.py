"""fundamental-hedger — Real-economy hedger rebalancing to a target ratio.

Canonical implementation of the ``fundamental-hedger`` archetype documented
in ``examples/AGENT_POOL/finance/fundamental-hedger.md``. Maintains a target
hedge position sized by exposure value, hedge ratio, and hedge
effectiveness; rebalances only when the position gap exceeds a tolerance.

Theoretical basis:
    Merton (1971) — Optimum consumption and portfolio rules in a
    continuous-time model.
    Anderson & Danthine (1981) — Cross hedging.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    target_position = (exposure_value / price)
                      * target_hedge_ratio * sqrt(hedge_effectiveness)
    position_gap = target_position - position

    If ``position_gap > rebalance_band * target_position``: buy
        ``min(position_gap, cash / price, max_order_size)``.
    If ``position_gap < -rebalance_band * target_position``: sell
        ``min(|position_gap|, position, max_order_size)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_hedge_ratio``  : float — coverage fraction (default 0.80).
    * ``hedge_effectiveness`` : float — R^2 vs instrument (default 0.75).
    * ``rebalance_band``      : float — tolerance band (default 0.10).
    * ``max_order_size``      : float — per-tick cap (default 300.0).
    * ``exposure_value``      : float — real exposure (default 100000.0).

Scenario-specific inputs (via ``state.raw``, declared through
``REQUIRES_FEATURES``): ``exposure_value``, ``hedge_effectiveness``.
Both fall back to the ``extras`` defaults when not broadcast.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalHedger(CanonicalRulePlayer):
    STRATEGY = "fundamental-hedger"
    DISPLAY_NAME = "Fundamental Hedger"
    SUMMARY = (
        "Rebalances toward a target hedge ratio sized by real-economy "
        "exposure (Merton 1971; Anderson & Danthine 1981)."
    )
    REQUIRES_FEATURES: tuple = ("exposure_value", "hedge_effectiveness")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["target_hedge_ratio"] = float(extras.get("target_hedge_ratio", 0.80))
        cs["hedge_effectiveness"] = float(extras.get("hedge_effectiveness", 0.75))
        cs["rebalance_band"] = float(extras.get("rebalance_band", 0.10))
        cs["max_order_size"] = float(extras.get("max_order_size", 300.0))
        cs["exposure_value"] = float(extras.get("exposure_value", 100000.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hedge_ratio = cs["target_hedge_ratio"]
        band = cs["rebalance_band"]
        max_order = cs["max_order_size"]

        exposure_value = state.raw_require("exposure_value", cast=float)
        effectiveness = state.raw_require("hedge_effectiveness", cast=float)

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or effectiveness < 0:
            return hold

        target_position = (
            (exposure_value / state.price) * hedge_ratio * math.sqrt(effectiveness)
        )
        position_gap = target_position - state.position
        tolerance = band * abs(target_position)

        if position_gap > tolerance:
            quantity = min(position_gap, state.cash / state.price, max_order)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if position_gap < -tolerance:
            quantity = min(abs(position_gap), max(state.position, 0.0), max_order)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMFundamentalHedger(CanonicalLLMPlayer):
    STRATEGY = "fundamental-hedger"
    DEFAULT_SYS_PROMPT = """\
You are a corporate hedger with real-economy exposure. Your goal is to
keep your derivative position at a target hedge ratio of your exposure,
scaled by how effectively the instrument tracks that exposure. You
rebalance only when the gap exceeds a tolerance band; you do not
speculate on direction.

Output format:
<analysis>state the target vs current hedge and the resulting adjustment.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance toward your hedge target when the gap exceeds tolerance.
"""


__all__ = ["RuleFundamentalHedger", "LLMFundamentalHedger"]
