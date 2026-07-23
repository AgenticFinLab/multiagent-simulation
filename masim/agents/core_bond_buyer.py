"""core-bond-buyer — Flight-to-quality core government bond buyer.

Canonical implementation of the ``core-bond-buyer`` archetype documented
in ``examples/AGENT_POOL/finance/core-bond-buyer.md``. Accumulates safe
government bonds when yield (relative to par/fundamental) exceeds a floor,
amplifying purchases under stress; sells only when bonds become materially
overpriced.

Theoretical basis:
    Vayanos (2004) — flight-to-quality / flight-to-liquidity.
    Caballero & Krishnamurthy (2008) — safe-asset shortage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    yield_signal = (fundamental - price) / fundamental

    If yield_signal > yield_floor:
        effective_size = base_size * (1 + stress_multiplier *
                                       (yield_signal - yield_floor)) * sizing_scale
        q = min(effective_size / price, allocation_cap * cash / price)  → buy
    Elif price > fundamental * (1 + overvaluation_threshold):
        q = min(position, base_size * (price - fundamental) * sizing_scale / price) → sell
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``yield_floor``              : float — minimum yield signal to buy
                                     (default 0.01).
    * ``stress_multiplier``        : float — size amplification per unit
                                     excess yield (default 2.0).
    * ``base_size``                : float — base order quantity
                                     (default 500.0).
    * ``sizing_scale``             : float — signal→quantity multiplier
                                     (default 5000.0).
    * ``allocation_cap``           : float — max fraction of cash per buy
                                     (default 0.15).
    * ``overvaluation_threshold``  : float — fraction above par triggering
                                     sell (default 0.03).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCoreBondBuyer(CanonicalRulePlayer):
    STRATEGY = "core-bond-buyer"
    DISPLAY_NAME = "Core Government Bond Buyer"
    SUMMARY = (
        "Flight-to-quality institutional accumulator of safe bonds "
        "(Vayanos 2004; Caballero & Krishnamurthy 2008)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["yield_floor"] = float(
            extras.get("yield_floor", 0.01)
        )
        self.state.custom_state["stress_multiplier"] = float(
            extras.get("stress_multiplier", 2.0)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 500.0))
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["allocation_cap"] = float(
            extras.get("allocation_cap", 0.15)
        )
        self.state.custom_state["overvaluation_threshold"] = float(
            extras.get("overvaluation_threshold", 0.03)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental <= 0 or state.price <= 0:
            return hold

        cs = self.state.custom_state
        yield_floor = cs["yield_floor"]
        stress_multiplier = cs["stress_multiplier"]
        base_size = cs["base_size"]
        sizing_scale = cs["sizing_scale"]
        allocation_cap = cs["allocation_cap"]
        overvaluation_threshold = cs["overvaluation_threshold"]

        yield_signal = (state.fundamental - state.price) / state.fundamental

        if yield_signal > yield_floor:
            effective_size = (
                base_size
                * (1.0 + stress_multiplier * (yield_signal - yield_floor))
                * sizing_scale
            )
            qty_by_size = effective_size / state.price
            qty_by_cap = allocation_cap * state.cash / state.price
            quantity = min(qty_by_size, qty_by_cap)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.price > state.fundamental * (1.0 + overvaluation_threshold):
            raw_qty = base_size * (state.price - state.fundamental) * sizing_scale / state.price
            quantity = min(state.position, raw_qty)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCoreBondBuyer(CanonicalLLMPlayer):
    STRATEGY = "core-bond-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a safety-seeking institutional bond buyer (sovereign wealth,
central-bank reserve manager, or insurance mandate). You accumulate core
government bonds when their yield above par is attractive, and you buy
more aggressively during market stress. You sell only when bonds are
materially overpriced. Capital preservation, not speculation, is your goal.

Output format:
<analysis>state the yield vs the floor and your flight-to-quality stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy when the bond yields above par (price below fundamental) exceed your
floor — size up during stress; sell only when bonds are clearly overpriced.
"""


__all__ = ["RuleCoreBondBuyer", "LLMCoreBondBuyer"]
