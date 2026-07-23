"""cascade-follower — Informational cascade follower.

Canonical implementation of the ``cascade-follower`` archetype documented
in ``examples/AGENT_POOL/finance/cascade-follower.md``. Accumulates a
count of rounds with abnormal deviation and, once the count exceeds a
trigger, commits to the sign of the current deviation — the sequential
informational-cascade mechanism.

Theoretical basis:
    Bikhchandani, Hirshleifer & Welch (1992) — theory of fads, fashion,
    custom and cultural change as informational cascades.
    Banerjee (1992) — simple model of herd behaviour.
    Anderson & Holt (1997) — experimental confirmation of cascades.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental
    IF |deviation| > 0.03: cascade_count += 1
    triggered = (cascade_count >= cascade_trigger)
    IF triggered:
        qty = min(800, int(|deviation| * social_weight * 5000))
        direction = sign(deviation)   (buy if +, sell if -)
    ELSE:
        qty = 0 (hold)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``social_weight``   : float > 0 — deviation → order-size multiplier
                             (default 0.8).
    * ``cascade_trigger`` : float > 0 — count threshold that arms cascade
                             (default 0.3).
    * ``deviation_gate``  : float > 0 — |deviation| that increments the
                             cascade counter (default 0.03).
    * ``max_order``       : int > 0 — per-round order-size cap
                             (default 800).
    * ``sizing_scale``    : float > 0 — deviation scale in the qty formula
                             (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCascadeFollower(CanonicalRulePlayer):
    STRATEGY = "cascade-follower"
    DISPLAY_NAME = "Informational Cascade Follower"
    SUMMARY = (
        "Accumulates evidence over rounds and, once cascade triggers, "
        "commits fully in the direction of deviation "
        "(Bikhchandani, Hirshleifer & Welch 1992)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["social_weight"] = float(
            extras.get("social_weight", 0.8)
        )
        self.state.custom_state["cascade_trigger"] = float(
            extras.get("cascade_trigger", 0.3)
        )
        self.state.custom_state["deviation_gate"] = float(
            extras.get("deviation_gate", 0.03)
        )
        self.state.custom_state["max_order"] = int(extras.get("max_order", 800))
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["cascade_count"] = 0.0

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        gate = self.state.custom_state["deviation_gate"]
        trigger = self.state.custom_state["cascade_trigger"]
        social_weight = self.state.custom_state["social_weight"]
        sizing = self.state.custom_state["sizing_scale"]
        cap = self.state.custom_state["max_order"]

        dev = state.deviation
        if abs(dev) > gate:
            self.state.custom_state["cascade_count"] += 1.0
        count = self.state.custom_state["cascade_count"]
        if count < trigger:
            return hold

        qty = min(cap, int(abs(dev) * social_weight * sizing))
        if qty <= 0:
            return hold

        factory = InvestorOrder.buy if dev > 0 else InvestorOrder.sell
        return factory(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMCascadeFollower(CanonicalLLMPlayer):
    STRATEGY = "cascade-follower"
    DEFAULT_SYS_PROMPT = """\
You are an informational cascade follower. You count rounds with abnormal
deviation from fundamental and, once enough evidence accumulates, you
commit to the crowd's implicit direction — buying premium, selling
discount, in proportion to the observed deviation
(Bikhchandani, Hirshleifer & Welch 1992).

Output format:
<analysis>note whether the cascade has triggered and which direction the deviation implies.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Follow the cascade: once evidence accumulates, trade in the direction of
deviation with quantity proportional to |deviation|; otherwise hold.
"""


__all__ = ["RuleCascadeFollower", "LLMCascadeFollower"]
