"""inertial-holder — Status-quo-biased sticky holder.

Canonical implementation of the ``inertial-holder`` archetype documented
in ``masim/agents/defines/finance/inertial-holder.md``. Holds through
normal market conditions; only extreme mispricings overcome its inertia,
and even then the trade is heavily dampened.

Theoretical basis:
    Samuelson & Zeckhauser (1988) — status quo bias.
    Kahneman, Knetsch & Thaler (1991) — endowment effect.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= change_threshold: hold.
    Else (contrarian direction):
        damping    = 1 - inertia_strength + 0.1
        quantity   = base_size * |deviation| / change_threshold * damping
        deviation > 0 -> sell (overvalued -> reluctantly reduce)
        deviation < 0 -> buy  (undervalued -> reluctantly add)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``change_threshold`` : float — |deviation| required to overcome
                              status quo bias (default 0.30).
    * ``inertia_strength`` : float in [0,1] — dampening intensity
                              (default 0.90).
    * ``base_size``        : float — base quantity before dampening
                              (default 200).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInertialHolder(CanonicalRulePlayer):
    STRATEGY = "inertial-holder"
    DISPLAY_NAME = "Status-Quo Inertial Holder"
    SUMMARY = (
        "Sticky holder that trades only on extreme mispricings and even then "
        "with an 80%-dampened order (Samuelson & Zeckhauser 1988; Kahneman "
        "et al. 1991)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["change_threshold"] = float(
            extras.get("change_threshold", 0.30)
        )
        self.state.custom_state["inertia_strength"] = float(
            extras.get("inertia_strength", 0.90)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 200.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["change_threshold"]
        inertia = self.state.custom_state["inertia_strength"]
        base_size = self.state.custom_state["base_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if threshold <= 0:
            return hold
        if abs(deviation) <= threshold:
            return hold

        damping = 1.0 - inertia + 0.1
        qty = base_size * abs(deviation) / threshold * damping
        if qty <= 0:
            return hold

        # CONTRARIAN direction.
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMInertialHolder(CanonicalLLMPlayer):
    STRATEGY = "inertial-holder"
    DEFAULT_SYS_PROMPT = """\
You are an inertial holder ruled by status-quo bias. The psychological
cost of acting is much larger than the expected gain from rebalancing, so
you hold through almost every market move. Only an extreme deviation
from fundamental will overcome your inertia, and even then your trade is
heavily dampened — a fraction of what a rational agent would deploy.

Output format:
<analysis>state whether the deviation is extreme enough to overcome your
inertia.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Hold by default; only extreme deviations trigger a dampened contrarian
trade.
"""


__all__ = ["RuleInertialHolder", "LLMInertialHolder"]
