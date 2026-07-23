"""equity-trader — Risk-controlled equity desk with two-band gate.

Canonical implementation of the ``equity-trader`` archetype documented
in ``examples/AGENT_POOL/finance/equity-trader.md``. A risk-controlled
equity desk that de-risks (sells) when the deviation breaks above a
two-band gate and rebuilds (buys) when it breaks below; the gate is
``gate = 2 * risk_limit``.

Theoretical basis:
    Moreira & Muir (2017) — volatility-managed portfolios; asymmetric
    risk aversion under vol regimes.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gate = 2 * risk_limit
    If |deviation| <= gate: hold.
    Else:
        q_raw = min(1000, int(|deviation| * K_eq))
        If deviation > gate and position > 0:
            q = min(q_raw, position)          → sell
        Elif deviation < -gate:
            q = min(q_raw, int(cash / price)) → buy
        Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``risk_limit`` : float — half-width of the two-band gate
                       (default 0.10; gate = 0.20).
    * ``k_eq``       : float — linear size coefficient in |deviation|
                       (default 3000.0).
    * ``per_round_cap`` : float — hard per-round quantity cap
                       (default 1000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleEquityTrader(CanonicalRulePlayer):
    STRATEGY = "equity-trader"
    DISPLAY_NAME = "Risk-Controlled Equity Trader"
    SUMMARY = (
        "Two-band risk gate on deviation; de-risks/rebuilds only outside "
        "the gate (Moreira & Muir 2017)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["risk_limit"] = float(
            extras.get("risk_limit", 0.10)
        )
        self.state.custom_state["k_eq"] = float(extras.get("k_eq", 3000.0))
        self.state.custom_state["per_round_cap"] = float(
            extras.get("per_round_cap", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        cs = self.state.custom_state
        risk_limit = cs["risk_limit"]
        k_eq = cs["k_eq"]
        per_round_cap = cs["per_round_cap"]

        gate = 2.0 * risk_limit
        if abs(state.deviation) <= gate:
            return hold

        q_raw = min(per_round_cap, float(int(abs(state.deviation) * k_eq)))
        if q_raw <= 0:
            return hold

        if state.deviation > gate and state.position > 0:
            quantity = min(q_raw, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.deviation < -gate and state.price > 0:
            budget_qty = float(int(state.cash / state.price))
            quantity = min(q_raw, budget_qty)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMEquityTrader(CanonicalLLMPlayer):
    STRATEGY = "equity-trader"
    DEFAULT_SYS_PROMPT = """\
You run a risk-controlled equity desk. You maintain a two-band tolerance
around fundamental: within the band you do nothing; outside the band
you de-risk (sell if overvalued) or rebuild (buy if undervalued) with a
size scaled by the size of the breach, subject to a strict per-round
share cap. You never over-commit relative to your risk budget.

Output format:
<analysis>state deviation vs the two-band gate and your risk stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade only when deviation exceeds twice your risk limit; scale size with
the deviation magnitude and stay within the per-round cap.
"""


__all__ = ["RuleEquityTrader", "LLMEquityTrader"]
