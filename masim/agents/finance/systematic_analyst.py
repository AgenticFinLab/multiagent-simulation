"""systematic-analyst — Rational Bayesian benchmark trader.

Canonical implementation of the ``systematic-analyst`` archetype
documented in ``masim/agents/defines/finance/systematic-analyst.md``.
Treats fundamental as the precision-weighted Bayesian posterior and
trades the resulting price-vs-posterior deviation using symmetric
threshold rules.

Theoretical basis:
    Graham (1949) — margin-of-safety and disciplined value analysis.
    Mullainathan & Thaler (2002) — rational vs. heuristic decision making.
    Simon (1955) — bounded rationality benchmark.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    posterior = fundamental
    dev       = (posterior - price) / price

    if dev >  buy_threshold:
        q = min(base_position_size, dev * sizing_scale)   -> buy
    elif dev < -sell_threshold and position > 0:
        q = min(position, base_position_size)             -> sell
    else:
        hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``buy_threshold``      : float — buy-side dev threshold (default 0.03).
    * ``sell_threshold``     : float — sell-side dev threshold
                               (default 0.05).
    * ``sizing_scale``       : float — dev→quantity scale (default 3000.0).
    * ``base_position_size`` : float — order-size cap (default 200.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSystematicAnalyst(CanonicalRulePlayer):
    STRATEGY = "systematic-analyst"
    DISPLAY_NAME = "Systematic Bayesian Analyst"
    SUMMARY = (
        "Rational Bayesian benchmark: trades price-vs-posterior deviations "
        "without recency bias (Graham 1949; Mullainathan-Thaler 2002; "
        "Simon 1955)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.03)
        )
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", 0.05)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 3000.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 200.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        buy_thr = self.state.custom_state["buy_threshold"]
        sell_thr = self.state.custom_state["sell_threshold"]
        sizing = self.state.custom_state["sizing_scale"]
        base = self.state.custom_state["base_position_size"]

        posterior = state.fundamental
        dev = (posterior - state.price) / state.price

        if dev > buy_thr:
            quantity = min(base, dev * sizing)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev < -sell_thr and state.position > 0:
            quantity = min(state.position, base)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMSystematicAnalyst(CanonicalLLMPlayer):
    STRATEGY = "systematic-analyst"
    DEFAULT_SYS_PROMPT = """\
You are a rational, systematic analyst. You treat the reported
fundamental as the precision-weighted Bayesian posterior for true value.
You buy when price is meaningfully below the posterior and sell when it
is meaningfully above, without overweighting recent or vivid news.

Output format:
<analysis>state posterior vs price and your threshold call.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy when price is below posterior by more than your buy threshold; sell
(with position) when price is above posterior by more than your sell
threshold; otherwise hold.
"""


__all__ = ["RuleSystematicAnalyst", "LLMSystematicAnalyst"]
