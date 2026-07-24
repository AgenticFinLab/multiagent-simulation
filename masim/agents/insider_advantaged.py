"""insider-advantaged — Privately-informed early mover.

Canonical implementation of the ``insider-advantaged`` archetype documented
in ``examples/AGENT_POOL/finance/insider-advantaged.md``. Trades pro-
cyclically on the deviation signal, riding bubbles up and exiting before
crashes; the ``information_advantage`` parameter scales the effective
response size.

Theoretical basis:
    Temin & Voth (2004) — insider trading during the South Sea Bubble;
    connected traders exit before less-informed participants.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= activation_threshold: hold.
    Else:
        raw_qty = |deviation| * scaling_factor * information_advantage
        qty     = min(max_quantity, raw_qty)
        deviation > 0 -> buy (ride the bubble up)
        deviation < 0 -> sell (exit ahead of collapse)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold``  : float — |deviation| trigger (default 0.02).
    * ``scaling_factor``        : float — deviation->qty scaling
                                   (default 5000).
    * ``max_quantity``          : float — per-round order cap (default 800).
    * ``information_advantage`` : float in [0,1] — confidence multiplier
                                   (default 0.8, Temin & Voth 2004).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInsiderAdvantaged(CanonicalRulePlayer):
    STRATEGY = "insider-advantaged"
    DISPLAY_NAME = "Insider-Advantaged Early Mover"
    SUMMARY = (
        "Pro-cyclical informed trader who rides bubbles up and exits before "
        "collapse, sized by information advantage (Temin & Voth 2004)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["scaling_factor"] = float(
            extras.get("scaling_factor", 5000.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 800.0)
        )
        self.state.custom_state["information_advantage"] = float(
            extras.get("information_advantage", 0.8)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["scaling_factor"]
        max_qty = self.state.custom_state["max_quantity"]
        advantage = self.state.custom_state["information_advantage"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        raw_qty = abs(deviation) * scale * advantage
        qty = float(min(max_qty, raw_qty))
        if qty <= 0:
            return hold

        # Pro-cyclical direction: ride the bubble up, exit ahead of collapse.
        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMInsiderAdvantaged(CanonicalLLMPlayer):
    STRATEGY = "insider-advantaged"
    DEFAULT_SYS_PROMPT = """\
You are an insider-advantaged trader with privileged information about
fundamentals and market direction. You enter early during bubble
inflation — buying when price runs above fundamental because you know
the run has further to go — and you exit early when the deviation turns
negative, leaving less-informed participants holding the bag. Your
information advantage amplifies your sizing.

Output format:
<analysis>state the deviation and your insider stance (ride vs. exit).</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Ride the bubble while deviation is positive, exit ahead of the crowd
when it turns negative; hold inside the dead zone.
"""


__all__ = ["RuleInsiderAdvantaged", "LLMInsiderAdvantaged"]
