"""trend-chaser — Positive-feedback speculator chasing deviation direction.

Canonical implementation of the ``trend-chaser`` archetype documented in
``examples/AGENT_POOL/finance/trend-chaser.md``. Buys when price is above
fundamental (rides the up-trend) and sells when price is below fundamental
(rides the down-trend) — the classic "greater fool" speculator that
amplifies mispricings.

Theoretical basis:
    Mackay (1841) — Extraordinary Popular Delusions and the Madness of Crowds.
    De Long, Shleifer, Summers & Waldmann (1990) — Positive feedback
    investment strategies and destabilizing rational speculation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= activation_threshold``: hold.
    If ``deviation > 0``: buy — chase the uptrend (procyclical).
    If ``deviation < 0``: sell — chase the downtrend (procyclical).

    quantity = ``min(max_quantity, |deviation| * scaling_factor)``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float in [0.01, 0.10] — minimum |deviation|
                                  to trigger a trade (default 0.02).
    * ``scaling_factor``       : float — multiplier from |deviation| to raw
                                  quantity (default 5000.0).
    * ``max_quantity``         : float — hard cap on order size per round
                                  (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleTrendChaser(CanonicalRulePlayer):
    STRATEGY = "trend-chaser"
    DISPLAY_NAME = "Positive-Feedback Trend Chaser"
    SUMMARY = (
        "Procyclical greater-fool speculator that chases the sign of the "
        "price↔fundamental deviation (Mackay 1841; De Long et al. 1990)."
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

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        # Missing-signal policy from §Design Purpose: hold if fundamental /
        # deviation is unavailable or NaN.
        if math.isnan(state.fundamental) or math.isnan(deviation):
            return hold

        threshold = self.state.custom_state["activation_threshold"]
        scaling = self.state.custom_state["scaling_factor"]
        cap = self.state.custom_state["max_quantity"]

        if abs(deviation) <= threshold:
            return hold

        quantity = min(cap, abs(deviation) * scaling)
        # Procyclical: sign(deviation) — buy overvalued, sell undervalued.
        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMTrendChaser(CanonicalLLMPlayer):
    STRATEGY = "trend-chaser"
    DEFAULT_SYS_PROMPT = """\
You are a positive-feedback trend chaser (greater-fool speculator). You
buy when price is above fundamental (chase the uptrend) and sell when
price is below fundamental (chase the downtrend). You never fade the
move — you always trade with the sign of the deviation. Small deviations
below your activation threshold leave you on the sidelines.

Output format:
<analysis>brief reasoning (1-2 sentences) on deviation and trend direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Chase the deviation: buy if price is above fundamental, sell if below;
hold when the gap is small.
"""


__all__ = ["RuleTrendChaser", "LLMTrendChaser"]
