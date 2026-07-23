"""prime-broker-delayed-liquidator — Slow prime-broker liquidator.

Canonical implementation of the ``prime-broker-delayed-liquidator``
archetype documented in
``examples/AGENT_POOL/finance/prime-broker-delayed-liquidator.md``.
Contrast with ``prime-broker-first-mover``: this creditor waits for a
deeper stress trigger and pays a price penalty when it finally liquidates.

Theoretical basis:
    Gorton & Metrick (2012) — securitized banking and the run on repo:
    later-movers face fire-sale discounts.
    Diamond & Dybvig (1983) — sequential-service constraint disadvantages
    delayed claimants.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``deviation < threshold`` (i.e. dev < -0.15) AND position > 0:
        sell = min(position, position * sell_ratio)
        at effective price = price * price_penalty (default 0.97 — 3%
        fire-sale discount).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``threshold``      : float — deeper deviation trigger (default -0.15).
    * ``sell_ratio``     : float — fraction of book offloaded per event
                            (default 0.35).
    * ``price_penalty``  : float — fire-sale discount factor applied to
                            the fill price (default 0.97).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePrimeBrokerDelayedLiquidator(CanonicalRulePlayer):
    STRATEGY = "prime-broker-delayed-liquidator"
    DISPLAY_NAME = "Prime Broker (Delayed Liquidator)"
    SUMMARY = (
        "Slower creditor who waits for a deeper stress trigger and pays a "
        "fire-sale price penalty (Gorton & Metrick 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["threshold"] = float(
            extras.get("threshold", -0.15)
        )
        self.state.custom_state["sell_ratio"] = float(
            extras.get("sell_ratio", 0.35)
        )
        self.state.custom_state["price_penalty"] = float(
            extras.get("price_penalty", 0.97)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        threshold = self.state.custom_state["threshold"]
        ratio = self.state.custom_state["sell_ratio"]
        penalty = self.state.custom_state["price_penalty"]

        if state.deviation < threshold and state.position > 0:
            quantity = min(state.position, state.position * ratio)
            if quantity <= 0:
                return hold
            fill_price = state.price * penalty
            if fill_price <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=fill_price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPrimeBrokerDelayedLiquidator(CanonicalLLMPlayer):
    STRATEGY = "prime-broker-delayed-liquidator"
    DEFAULT_SYS_PROMPT = """\
You are a delayed-liquidator prime broker. You are slower than the
first-mover crowd: you only unwind when stress is severe, and you accept
a fire-sale discount because the best liquidity is already gone. Outside
that deep-stress regime you hold.

Output format:
<analysis>state deviation, your deeper-stress trigger, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Liquidate only under deep stress and accept the fire-sale discount.
"""


__all__ = [
    "RulePrimeBrokerDelayedLiquidator",
    "LLMPrimeBrokerDelayedLiquidator",
]
