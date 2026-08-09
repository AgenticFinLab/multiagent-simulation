"""fundamental-anchor — Slow value-anchored arbitrageur.

Canonical implementation of the ``fundamental-anchor`` archetype documented
in ``masim/agents/defines/finance/fundamental-anchor.md``. Builds positions
gradually against mispricing, subject to a hard position cap.

Theoretical basis:
    Shleifer & Vishny (1997) — The limits of arbitrage.
    Grossman & Stiglitz (1980) — On the impossibility of informationally
    efficient markets.
    Mitchell & Pulvino (2001) — Characteristics of risk and return in
    risk arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    mispricing = (fundamental - price) / price
    If ``|mispricing| <= value_threshold``: hold.
    Elif ``mispricing > value_threshold``: buy — direction "buy";
        capacity = max_position - position.
    Elif ``mispricing < -value_threshold``: sell — direction "sell";
        capacity = max_position + position.
    raw_qty = scale * |mispricing| * (capacity * capacity_fraction)
    quantity = max(0, min(int(raw_qty), capacity)).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``value_threshold``    : float — activation gate (default 0.05).
    * ``scale``              : float — mispricing→qty factor (default 1.5).
    * ``max_position``       : int — long/short cap (default 50).
    * ``capacity_fraction``  : float — capacity utilization (default 0.5).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalAnchor(CanonicalRulePlayer):
    STRATEGY = "fundamental-anchor"
    DISPLAY_NAME = "Fundamental Anchor"
    SUMMARY = (
        "Value-anchored arbitrageur building positions gradually against "
        "mispricing (Shleifer & Vishny 1997; Grossman & Stiglitz 1980)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["value_threshold"] = float(extras.get("value_threshold", 0.05))
        cs["scale"] = float(extras.get("scale", 1.5))
        cs["max_position"] = int(extras.get("max_position", 50))
        cs["capacity_fraction"] = float(extras.get("capacity_fraction", 0.5))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["value_threshold"]
        scale = cs["scale"]
        max_position = cs["max_position"]
        cap_frac = cs["capacity_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or math.isnan(state.fundamental):
            return hold
        mispricing = (state.fundamental - state.price) / state.price

        if abs(mispricing) <= threshold:
            return hold

        if mispricing > 0:
            capacity = max(0.0, max_position - state.position)
        else:
            capacity = max(0.0, max_position + state.position)
        if capacity <= 0:
            return hold

        raw_qty = scale * abs(mispricing) * (capacity * cap_frac)
        quantity = max(0, min(int(raw_qty), int(capacity)))
        if quantity <= 0:
            return hold

        factory = InvestorOrder.buy if mispricing > 0 else InvestorOrder.sell
        return factory(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMFundamentalAnchor(CanonicalLLMPlayer):
    STRATEGY = "fundamental-anchor"
    DEFAULT_SYS_PROMPT = """\
You are a patient value arbitrageur anchored to a fundamental valuation.
You accumulate a position gradually when price is meaningfully below
fundamental and reduce (or short) when price is above. You size trades
by remaining capacity, respecting a hard position cap.

Output format:
<analysis>state the mispricing and remaining capacity.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade gradually against the mispricing, respecting your position cap.
"""


__all__ = ["RuleFundamentalAnchor", "LLMFundamentalAnchor"]
