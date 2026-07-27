"""belief-anchor — Conservatism-biased belief-anchored updater.

Canonical implementation of the ``belief-anchor`` archetype documented in
``examples/AGENT_POOL/finance/belief-anchor.md``.

Theoretical basis:
    Edwards (1968) — conservatism bias in belief revision;
    Barberis, Shleifer & Vishny (1998) — under-reaction from anchored beliefs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain internal belief seeded to first fundamental.
    belief_candidate = (1 - alpha) * belief + alpha * fundamental
    If |belief_candidate - belief| > max_step:
        belief = belief + sign(...) * max_step
    Else:
        belief = belief_candidate

    gap = belief - price
    If gap >  belief_threshold * price:
        buy  q = min(base_size * gap * sizing_scale / price, cash / price)
    If gap < -belief_threshold * price:
        sell q = min(base_size * |gap| * sizing_scale / price, position)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``alpha``            : float — belief update rate (default 0.1).
    * ``belief_threshold`` : float — gap/price gate      (default 0.02).
    * ``base_size``        : float — base share unit     (default 400.0).
    * ``sizing_scale``     : float — gap -> qty gain     (default 5000.0).
    * ``max_step``         : float — max belief step      (default 2.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBeliefAnchor(CanonicalRulePlayer):
    STRATEGY = "belief-anchor"
    DISPLAY_NAME = "Belief-Anchored Conservative Updater"
    SUMMARY = (
        "Slowly-updating belief-anchored trader embodying conservatism "
        "bias (Edwards 1968; Barberis, Shleifer & Vishny 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["alpha"] = float(extras.get("alpha", 0.1))
        self.state.custom_state["belief_threshold"] = float(
            extras.get("belief_threshold", 0.02)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 400.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["max_step"] = float(
            extras.get("max_step", 2.0)
        )
        self.state.custom_state["belief"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("belief") is None:
            fund = market_data.get("fundamental")
            if fund is None or (isinstance(fund, float) and math.isnan(fund)):
                # Fall back to price if fundamental unavailable on first tick.
                self.state.custom_state["belief"] = float(market_data["price"])
            else:
                self.state.custom_state["belief"] = float(fund)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental):
            # Hold and do not update belief when fundamental is missing.
            return hold

        alpha = self.state.custom_state["alpha"]
        threshold = self.state.custom_state["belief_threshold"]
        base = self.state.custom_state["base_size"]
        scale = self.state.custom_state["sizing_scale"]
        max_step = self.state.custom_state["max_step"]

        belief = self.state.custom_state.get("belief")
        if belief is None:
            belief = float(state.fundamental)

        candidate = (1.0 - alpha) * belief + alpha * state.fundamental
        step = candidate - belief
        if abs(step) > max_step:
            belief = belief + math.copysign(max_step, step)
        else:
            belief = candidate
        self.state.custom_state["belief"] = belief

        if state.price <= 0:
            return hold

        gap = belief - state.price
        band = threshold * state.price

        if gap > band:
            q = base * gap * scale / state.price
            if q <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(q),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if gap < -band:
            q = base * abs(gap) * scale / state.price
            if q <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(q),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMBeliefAnchor(CanonicalLLMPlayer):
    STRATEGY = "belief-anchor"
    DEFAULT_SYS_PROMPT = """\
You are a conservative institutional allocator whose beliefs about
fair value update slowly. Each round you nudge your internal belief a
small step toward the new fundamental signal, capped by a maximum
single-step revision. You trade only when the gap between your
anchored belief and the market price exceeds a small threshold.

Output format:
<analysis>state your updated belief, gap to price, and direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Update your anchored belief slowly toward fundamental; if the gap to
price exceeds the threshold, trade toward your belief.
"""


__all__ = ["RuleBeliefAnchor", "LLMBeliefAnchor"]
