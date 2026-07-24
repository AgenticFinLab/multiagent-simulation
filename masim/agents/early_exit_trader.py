"""early-exit-trader — Strategic "smart-money" early exit trader.

Canonical implementation of the ``early-exit-trader`` archetype documented
in ``examples/AGENT_POOL/finance/early-exit-trader.md``. When the price
diverges from fundamental beyond an activation threshold, the agent
trades contrarian to the divergence — selling into overvaluation
(strategic exit) or buying into undervaluation (strategic entry).

Theoretical basis:
    Brunnermeier & Nagel (2004) — "smart money" that rides then exits
    bubbles. Thompson (2007) — strategic-exit discipline.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= activation_threshold: hold.
    Else:
        raw_qty = |deviation| * scaling_factor
        quantity = min(max_quantity, raw_qty)
        direction = "sell" if deviation > 0 else "buy"
        (base finalizer applies cash / position clipping.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — minimum |deviation| to trade
                                 (default 0.05).
    * ``scaling_factor``       : float — |deviation|→quantity multiplier
                                 (default 3000.0).
    * ``max_quantity``         : float — hard per-round size cap
                                 (default 500.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleEarlyExitTrader(CanonicalRulePlayer):
    STRATEGY = "early-exit-trader"
    DISPLAY_NAME = "Strategic Early-Exit Trader"
    SUMMARY = (
        "Contrarian graduated entry/exit around fundamental deviation "
        "(Brunnermeier & Nagel 2004; Thompson 2007)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["scaling_factor"] = float(
            extras.get("scaling_factor", 3000.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 500.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        cs = self.state.custom_state
        activation_threshold = cs["activation_threshold"]
        scaling_factor = cs["scaling_factor"]
        max_quantity = cs["max_quantity"]

        if abs(state.deviation) <= activation_threshold:
            return hold

        raw_qty = abs(state.deviation) * scaling_factor
        quantity = min(max_quantity, raw_qty)
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


class LLMEarlyExitTrader(CanonicalLLMPlayer):
    STRATEGY = "early-exit-trader"
    DEFAULT_SYS_PROMPT = """\
You are a strategic "smart money" trader. You are willing to enter and
exit around fundamental value with discipline — buying meaningful
undervaluation and selling meaningful overvaluation. Unlike a bubble
rider, you do not wait for the exact peak; you take graduated positions
as the divergence grows, and never let a single trade exceed your
per-round cap.

Output format:
<analysis>state deviation vs activation threshold and your posture.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade contrarian to the deviation once it clears your activation
threshold; scale size with the deviation up to your per-round cap.
"""


__all__ = ["RuleEarlyExitTrader", "LLMEarlyExitTrader"]
