"""portfolio-insurer — Portfolio-insurance / delta-hedge selling.

Canonical implementation of the ``portfolio-insurer`` archetype
documented in ``examples/AGENT_POOL/finance/portfolio-insurer.md``.
Sells into declines (feedback selling) and buys into rallies to
restore a target delta. This is the mechanism famously implicated in
the October 1987 crash by the Brady Commission (1988).

Theoretical basis:
    Leland (1980) — synthetic put via dynamic hedging.
    Brady Report (1988) — portfolio-insurance-driven feedback selling
    on 19 October 1987.
    Gennotte & Leland (1990) — informational cascade under portfolio
    insurance.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``deviation < -theta_pi``:
        sell = min(position, hedge_ratio * |deviation| * position)
    If ``deviation > theta_pi``:
        buy = min(cash/price, hedge_ratio * deviation * cash/price)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_pi``     : float — activation band around fair value
                          (default 0.02, Leland 1980).
    * ``hedge_ratio``  : float — fraction of exposure adjusted per event
                          (default 0.50, Brady 1988 empirical).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePortfolioInsurer(CanonicalRulePlayer):
    STRATEGY = "portfolio-insurer"
    DISPLAY_NAME = "Portfolio Insurer"
    SUMMARY = (
        "Delta-hedge feedback trader: sells into declines and buys into "
        "rallies (Leland 1980; Brady 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_pi"] = float(extras.get("theta_pi", 0.02))
        self.state.custom_state["hedge_ratio"] = float(
            extras.get("hedge_ratio", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold

        theta = self.state.custom_state["theta_pi"]
        hr = self.state.custom_state["hedge_ratio"]
        dev = state.deviation

        if dev < -theta and state.position > 0:
            quantity = min(state.position, hr * abs(dev) * state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev > theta and state.cash > 0:
            affordable = state.cash / state.price
            quantity = min(affordable, hr * dev * affordable)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPortfolioInsurer(CanonicalLLMPlayer):
    STRATEGY = "portfolio-insurer"
    DEFAULT_SYS_PROMPT = """\
You run a portfolio-insurance / delta-hedging book. When the market falls
below fair value, your synthetic put requires you to SELL more into the
decline; when the market rallies above fair value you REBUY to restore
delta. You never fight the direction: you amplify it. Trade size scales
with the mispricing magnitude.

Output format:
<analysis>state the deviation and your delta-hedge stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Execute portfolio insurance: sell into declines, buy into rallies, hold
inside the neutral band.
"""


__all__ = ["RulePortfolioInsurer", "LLMPortfolioInsurer"]
