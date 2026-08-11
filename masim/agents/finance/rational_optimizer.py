"""rational-optimizer — Merton-style mean-variance optimizer.

Canonical implementation of the ``rational-optimizer`` archetype
documented in ``masim/agents/defines/finance/rational-optimizer.md``.
Every round the agent computes the closed-form Merton weight
``w* = (mu - rf) / (gamma * sigma^2)`` and rebalances partially toward
it whenever the deviation from current weight exceeds the rebalance band.

Theoretical basis:
    Merton (1969) — lifetime portfolio selection under uncertainty.
    Markowitz (1952) — mean-variance portfolio selection.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    w* = clip((expected_return - risk_free_rate) / (gamma * variance), 0, 1)
    wealth = position * price + cash
    current_weight = position * price / wealth
    gap = w* - current_weight

    If ``|gap| > rebalance_band``:
        quantity = rebalance_speed * |gap| * wealth / price
        direction: buy if gap > 0, sell if gap < 0.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gamma``           : float — CRRA risk-aversion coefficient
                             (default 3.0).
    * ``rebalance_speed`` : float — fraction of gap closed per tick
                             (default 0.20).
    * ``rebalance_band``  : float — no-trade band around target weight
                             (default 0.02).

``expected_return``, ``risk_free_rate``, and ``variance`` are read from
``state.raw``; the scenario coordinator must broadcast them.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalOptimizer(CanonicalRulePlayer):
    STRATEGY = "rational-optimizer"
    DISPLAY_NAME = "Rational Optimizer"
    SUMMARY = (
        "Merton closed-form mean-variance optimizer; rebalances partially "
        "toward the CRRA optimal weight (Merton 1969; Markowitz 1952)."
    )
    REQUIRES_FEATURES: tuple = ("expected_return", "risk_free_rate", "variance")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gamma"] = float(extras.get("gamma", 3.0))
        self.state.custom_state["rebalance_speed"] = float(
            extras.get("rebalance_speed", 0.20)
        )
        self.state.custom_state["rebalance_band"] = float(
            extras.get("rebalance_band", 0.02)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        mu = state.raw_require("expected_return", cast=float)
        rf = state.raw_require("risk_free_rate", cast=float)
        var = state.raw_require("variance", cast=float)
        if var <= 0:
            return hold

        gamma = self.state.custom_state["gamma"]
        speed = self.state.custom_state["rebalance_speed"]
        band = self.state.custom_state["rebalance_band"]

        w_star = (mu - rf) / (gamma * var)
        w_star = max(0.0, min(1.0, w_star))

        wealth = state.position * state.price + state.cash
        if wealth <= 0:
            return hold
        current_w = state.position * state.price / wealth
        gap = w_star - current_w

        if abs(gap) <= band:
            return hold

        quantity = speed * abs(gap) * wealth / state.price
        if quantity <= 0:
            return hold

        if gap > 0:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRationalOptimizer(CanonicalLLMPlayer):
    STRATEGY = "rational-optimizer"
    DEFAULT_SYS_PROMPT = """\
You are a Merton-style mean-variance optimizer. Each round you consider
expected excess return, variance, and your CRRA risk aversion, then
target the closed-form optimal risky weight w* = (mu - rf) / (gamma *
sigma^2). You never rebalance in one shot: you close a fraction of the
gap each tick, and you don't trade at all inside a small band.

Output format:
<analysis>state target weight, current weight, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance toward the Merton optimal weight computed from expected
return, risk-free rate, and variance.
"""


__all__ = ["RuleRationalOptimizer", "LLMRationalOptimizer"]
