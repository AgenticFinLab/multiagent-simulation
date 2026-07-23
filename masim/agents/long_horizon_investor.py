"""long-horizon-investor — Portfolio-weight rebalancing investor.

Canonical implementation of the ``long-horizon-investor`` archetype
documented in ``examples/AGENT_POOL/finance/long-horizon-investor.md``. The
archetype maintains a target equity weight in a long-horizon portfolio and
rebalances only when the realised weight drifts outside a band. When price
is deep-discounted relative to fundamental, buys are scaled up
opportunistically.

Theoretical basis:
    Merton (1969) — lifetime portfolio selection with fixed-share targets.
    Campbell & Viceira (2002) — strategic asset allocation and rebalancing.
    Fama & French (1988) — long-horizon mean reversion in equity returns.

Decision rule (verbatim from AGENT_POOL profile §Behavioral Framework):

    On every round compute the realised equity weight::

        actual_weight = (position * price) / portfolio_value

    If ``actual_weight < target_weight - rebalance_threshold``:
        base rebalance size returns weight to target, i.e.
        ``buy_qty = ((target_weight - actual_weight) * portfolio_value) / price``.
        If ``price / fundamental < discount_threshold`` (deep discount),
        multiply ``buy_qty`` by ``opportunistic_multiplier``.
    If ``actual_weight > target_weight + rebalance_threshold``:
        ``sell_qty = ((actual_weight - target_weight) * portfolio_value) / price``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_weight``            : float in [0, 1] — desired equity share of
                                      portfolio value (default 0.70).
    * ``rebalance_threshold``      : float in [0, 1] — one-sided no-trade band
                                      around the target weight (default 0.10).
    * ``discount_threshold``       : float in (0, 1] — ``price / fundamental``
                                      level below which opportunistic scaling
                                      activates (default 0.85).
    * ``opportunistic_multiplier`` : float >= 1.0 — multiplier applied to
                                      buys under deep discount (default 1.5).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLongHorizonInvestor(CanonicalRulePlayer):
    STRATEGY = "long-horizon-investor"
    DISPLAY_NAME = "Long-Horizon Rebalancing Investor"
    SUMMARY = (
        "Maintains a target equity weight and rebalances only when drift "
        "exceeds a band; buys deeper on deep discounts "
        "(Merton 1969; Campbell & Viceira 2002)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_weight"] = float(
            extras.get("target_weight", 0.70)
        )
        self.state.custom_state["rebalance_threshold"] = float(
            extras.get("rebalance_threshold", 0.10)
        )
        self.state.custom_state["discount_threshold"] = float(
            extras.get("discount_threshold", 0.85)
        )
        self.state.custom_state["opportunistic_multiplier"] = float(
            extras.get("opportunistic_multiplier", 1.5)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target_w = self.state.custom_state["target_weight"]
        band = self.state.custom_state["rebalance_threshold"]
        discount = self.state.custom_state["discount_threshold"]
        mult = self.state.custom_state["opportunistic_multiplier"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        pv = state.portfolio_value
        if not math.isfinite(pv) or pv <= 0 or state.price <= 0:
            return hold

        actual_w = (state.position * state.price) / pv

        if actual_w < target_w - band:
            gap = (target_w - actual_w) * pv
            qty = gap / state.price
            fundamental = state.fundamental
            if (
                math.isfinite(fundamental)
                and fundamental > 0
                and (state.price / fundamental) < discount
            ):
                qty *= mult
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if actual_w > target_w + band:
            gap = (actual_w - target_w) * pv
            qty = gap / state.price
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLongHorizonInvestor(CanonicalLLMPlayer):
    STRATEGY = "long-horizon-investor"
    DEFAULT_SYS_PROMPT = """\
You are a long-horizon investor who maintains a target equity weight in
your portfolio. You rebalance back toward the target only when realised
weight drifts outside a band, and you scale up buys when price is deeply
discounted relative to fundamental value.

Output format:
<analysis>state your current equity weight, the target, and whether a
           deep-discount opportunity is active.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance toward your target equity weight; scale buys up if price is
deeply discounted vs fundamental. Otherwise hold.
"""


__all__ = ["RuleLongHorizonInvestor", "LLMLongHorizonInvestor"]
