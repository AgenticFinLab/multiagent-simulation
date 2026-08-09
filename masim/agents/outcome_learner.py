"""outcome-learner — Attribution-biased outcome learner.

Canonical implementation of the ``outcome-learner`` archetype documented in
``masim/agents/defines/finance/outcome-learner.md``. Trades pro-cyclically on
observed price deviation, but with asymmetric attribution: gains are
attributed to skill (scaling up size), losses are attributed to bad luck
(sizing at baseline).

Theoretical basis:
    Fischhoff & Beyth (1975) — hindsight and outcome-attribution biases.
    Odean (1998) — overconfident traders and excessive trading.
    Barber & Odean (2000) — signal-following retail behaviour.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= activation_threshold``: hold.
    Elif ``deviation > 0``:
        action = buy
        attribution_scale = success_attribution   (>= 1 typically)
    Elif ``deviation < 0``:
        action = sell
        attribution_scale = failure_discount      (<= 1 typically)

    Quantity = ``min(max_order,
                     int(|deviation| * quantity_scale * attribution_scale))``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold``  : float — trigger (default 0.02).
    * ``quantity_scale``        : float — |dev|→quantity (default 5000.0).
    * ``max_order``             : float — per-tick cap (default 800.0).
    * ``success_attribution``   : float — gain multiplier (default 1.3).
    * ``failure_discount``      : float — loss multiplier (default 1.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleOutcomeLearner(CanonicalRulePlayer):
    STRATEGY = "outcome-learner"
    DISPLAY_NAME = "Outcome-Attribution Learner"
    SUMMARY = (
        "Trades pro-cyclically on deviation with asymmetric attribution: "
        "up-tilts on gains, baseline on losses "
        "(Fischhoff & Beyth 1975; Odean 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 800.0)
        )
        self.state.custom_state["success_attribution"] = float(
            extras.get("success_attribution", 1.3)
        )
        self.state.custom_state["failure_discount"] = float(
            extras.get("failure_discount", 1.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        q_scale = self.state.custom_state["quantity_scale"]
        max_order = self.state.custom_state["max_order"]
        success = self.state.custom_state["success_attribution"]
        failure = self.state.custom_state["failure_discount"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        if deviation > 0:
            attribution = success
            factory = InvestorOrder.buy
        else:
            attribution = failure
            factory = InvestorOrder.sell

        raw = int(abs(deviation) * q_scale * attribution)
        quantity = float(min(max_order, float(raw)))
        if quantity <= 0:
            return hold
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMOutcomeLearner(CanonicalLLMPlayer):
    STRATEGY = "outcome-learner"
    DEFAULT_SYS_PROMPT = """\
You are an outcome-attribution learner. You trade in the direction of
observed price deviations. When you see the price above fundamental,
you interpret that as your skill being confirmed and you buy — often
scaling up your usual size. When you see it below fundamental, you
attribute the drift to bad luck and still sell, but at your baseline
size. Small mispricings do not move you.

Output format:
<analysis>state the deviation, the attribution frame, and the resulting size.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade pro-cyclically: buy positive deviations (skill-attributed, larger),
sell negative deviations (luck-attributed, baseline), hold below threshold.
"""


__all__ = ["RuleOutcomeLearner", "LLMOutcomeLearner"]
