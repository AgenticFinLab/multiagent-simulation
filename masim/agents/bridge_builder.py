"""bridge-builder — Inventory-aware two-sided market maker.

Canonical implementation of the ``bridge-builder`` archetype documented in
``examples/AGENT_POOL/finance/bridge-builder.md``.

Theoretical basis:
    Kyle (1985) — market microstructure with a risk-averse market maker;
    Glosten & Milgrom (1985) — bid-ask spreads with inventory risk.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    inv_ratio = |position| / inventory_limit
    eff_hs    = half_spread * (1 + inventory_penalty * inv_ratio)
    band      = eff_hs * price
    gap       = price - fundamental                       # in price units

    If gap < -band AND position <  inventory_limit:
        buy  q = min(base_size * |gap| / price * sizing_scale,
                     cash / price,
                     inventory_limit - position)
    If gap >  band AND position > 0:
        sell q = min(base_size * |gap| / price * sizing_scale,
                     position)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``half_spread``       : float — base half-spread (default 0.015).
    * ``inventory_limit``   : float — inventory cap (default 1000.0).
    * ``inventory_penalty`` : float — inv skew gain (default 1.0).
    * ``base_size``         : float — base share unit (default 200.0).
    * ``sizing_scale``      : float — gap -> qty gain (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBridgeBuilder(CanonicalRulePlayer):
    STRATEGY = "bridge-builder"
    DISPLAY_NAME = "Inventory-Aware Market Maker"
    SUMMARY = (
        "Inventory-aware two-sided market maker widening the effective "
        "spread with inventory risk (Kyle 1985; Glosten & Milgrom 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["half_spread"] = float(
            extras.get("half_spread", 0.015)
        )
        self.state.custom_state["inventory_limit"] = float(
            extras.get("inventory_limit", 1000.0)
        )
        self.state.custom_state["inventory_penalty"] = float(
            extras.get("inventory_penalty", 1.0)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 200.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        half_spread = self.state.custom_state["half_spread"]
        inv_limit = self.state.custom_state["inventory_limit"]
        inv_penalty = self.state.custom_state["inventory_penalty"]
        base = self.state.custom_state["base_size"]
        scale = self.state.custom_state["sizing_scale"]

        if inv_limit <= 0:
            return hold
        inv_ratio = abs(state.position) / inv_limit
        eff_hs = half_spread * (1.0 + inv_penalty * inv_ratio)
        band = eff_hs * state.price
        gap = state.price - state.fundamental  # positive => overpriced

        if gap < -band and state.position < inv_limit:
            room = inv_limit - state.position
            raw = base * abs(gap) / state.price * scale
            quantity = min(raw, room)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if gap > band and state.position > 0:
            raw = base * abs(gap) / state.price * scale
            quantity = min(raw, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMBridgeBuilder(CanonicalLLMPlayer):
    STRATEGY = "bridge-builder"
    DEFAULT_SYS_PROMPT = """\
You are an inventory-aware two-sided market maker. You quote around
fundamental value with an effective half-spread that widens as your
inventory grows. Buy when price is meaningfully below fundamental and
you have room to add; sell when price is meaningfully above and you
hold inventory. Inside your effective band you stay flat.

Output format:
<analysis>state gap, effective band, and inventory constraint.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Make markets inventory-aware: buy below your band if you have room,
sell above your band if you have inventory, else hold.
"""


__all__ = ["RuleBridgeBuilder", "LLMBridgeBuilder"]
