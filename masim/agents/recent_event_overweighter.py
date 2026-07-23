"""recent-event-overweighter — Availability-biased salient-return chaser.

Canonical implementation of the ``recent-event-overweighter`` archetype
documented in ``examples/AGENT_POOL/finance/recent-event-overweighter.md``.
Blends the salient recent return with the objective deviation via a
recency weight; trades in the direction of the perceived signal when it
crosses a salience threshold.

Theoretical basis:
    Tversky & Kahneman (1973) — availability heuristic: easily recalled
    events feel more probable than they are.
    De Bondt & Thaler (1985) — overreaction to salient prior returns.
    Jegadeesh & Titman (1993) — parent momentum mechanism (return
    continuation).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    r = (price - prev_price) / prev_price
    s = recency_weight * r + (1 - recency_weight) * deviation

    If ``s > salience_threshold``:  buy  qty = min(max_order, |s| * quantity_scale)
    If ``s < -salience_threshold``: sell qty = min(max_order, |s| * quantity_scale)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``recency_weight``      : float — weight on the recent return
                                 (default 0.70, Tversky & Kahneman 1973).
    * ``salience_threshold``  : float — activation band on |s|
                                 (default 0.02, De Bondt & Thaler 1985).
    * ``quantity_scale``      : float — |s|→qty conversion (default 5000).
    * ``max_order``           : float — per-tick order cap (default 300).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRecentEventOverweighter(CanonicalRulePlayer):
    STRATEGY = "recent-event-overweighter"
    DISPLAY_NAME = "Recent-Event Overweighter"
    SUMMARY = (
        "Availability-biased trader who overweights the salient recent "
        "return relative to the objective deviation (Tversky & Kahneman "
        "1973; De Bondt & Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["recency_weight"] = float(
            extras.get("recency_weight", 0.70)
        )
        self.state.custom_state["salience_threshold"] = float(
            extras.get("salience_threshold", 0.02)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 300.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.prev_price <= 0:
            return hold
        if math.isnan(state.deviation):
            # Availability channel still works from the return alone —
            # blend with 0 for the missing base rate.
            deviation = 0.0
        else:
            deviation = state.deviation

        rho = self.state.custom_state["recency_weight"]
        theta = self.state.custom_state["salience_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        qmax = self.state.custom_state["max_order"]

        r = (state.price - state.prev_price) / state.prev_price
        s = rho * r + (1.0 - rho) * deviation

        if abs(s) <= theta:
            return hold

        quantity = min(qmax, abs(s) * scale)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.buy if s > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRecentEventOverweighter(CanonicalLLMPlayer):
    STRATEGY = "recent-event-overweighter"
    DEFAULT_SYS_PROMPT = """\
You are a retail trader whose attention is captured by the latest vivid
price move. You overweight the most recent return relative to the
objective price-fundamental gap and act on that blended signal. When it
crosses your salience threshold you chase the direction of the recent
move; small moves you ignore.

Output format:
<analysis>state the recent return, blended perceived signal, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Chase the direction of the recent move when the salient signal is large;
hold otherwise.
"""


__all__ = ["RuleRecentEventOverweighter", "LLMRecentEventOverweighter"]
