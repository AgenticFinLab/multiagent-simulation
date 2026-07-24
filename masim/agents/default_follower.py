"""default-follower — Default-effect dampened contrarian.

Canonical implementation of the ``default-follower`` archetype documented
in ``examples/AGENT_POOL/finance/default-follower.md``. The agent adheres
to its default allocation until the deviation |price - fundamental| /
fundamental exceeds an activation cutoff. When it does trade, its
response is dampened by a ``default_weight`` factor that reflects
adherence friction.

Theoretical basis:
    Madrian & Shea (2001) — default effects in retirement allocation.
    Cronqvist & Thaler (2004) — sticky defaults in retail investment.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= active_deviation: hold.
    Else:
        direction  = "sell" if deviation > 0 else "buy"
        quantity   = base_size * |deviation| / active_deviation * default_weight
        (clipped to cash / position by the base finalizer).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``active_deviation`` : float — minimum |deviation| to override
                             default (default 0.15).
    * ``default_weight``   : float in (0, 1] — dampening factor
                             (default 0.50).
    * ``base_size``        : float — base position size before dampening
                             (default 250.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDefaultFollower(CanonicalRulePlayer):
    STRATEGY = "default-follower"
    DISPLAY_NAME = "Default-Follower (Sticky-Allocation Investor)"
    SUMMARY = (
        "Sticks to default allocation until deviation is large; then "
        "trades at half-strength (Madrian & Shea 2001; Cronqvist & Thaler 2004)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["active_deviation"] = float(
            extras.get("active_deviation", 0.15)
        )
        self.state.custom_state["default_weight"] = float(
            extras.get("default_weight", 0.50)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 250.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        cs = self.state.custom_state
        active_deviation = cs["active_deviation"]
        default_weight = cs["default_weight"]
        base_size = cs["base_size"]

        if active_deviation <= 0:
            return hold
        if abs(state.deviation) <= active_deviation:
            return hold

        quantity = base_size * abs(state.deviation) / active_deviation * default_weight
        if quantity <= 0:
            return hold

        if state.deviation > 0:
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMDefaultFollower(CanonicalLLMPlayer):
    STRATEGY = "default-follower"
    DEFAULT_SYS_PROMPT = """\
You are a default-following investor. You strongly prefer to keep your
initial allocation and only override the default when the market is
CLEARLY mispriced — meaning the deviation from fundamental is large. Even
then, your reaction is dampened: you trade at roughly half-strength
compared to a fully attentive investor. Small deviations do not tempt
you at all.

Output format:
<analysis>note the deviation and whether it clears your activation cutoff.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Hold at your default allocation unless the deviation is clearly large;
when you do trade, do so at reduced size due to default adherence.
"""


__all__ = ["RuleDefaultFollower", "LLMDefaultFollower"]
