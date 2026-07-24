"""contrarian-statistical — Statistical (position-capped) contrarian.

Canonical implementation of the ``contrarian-statistical`` archetype
documented in ``examples/AGENT_POOL/finance/contrarian-statistical.md``.
Trades opposite deviation with quantity proportional to |deviation|,
capped by a position limit and per-round order cap.

Theoretical basis:
    Lakonishok, Shleifer & Vishny (1994) — contrarian investment,
    extrapolation and risk.
    Poterba & Summers (1988) — mean reversion in stock prices.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    IF deviation >  contrarian_threshold: SELL
    IF deviation < -contrarian_threshold: BUY
    qty = min(quantity_cap, round(|deviation| * sizing_scale))
    (subject to position_limit clamp for both sides)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``contrarian_threshold`` : float > 0 — |deviation| trigger
                                   (default 0.05).
    * ``position_size``        : float > 0 — nominal position target
                                   (default 3000.0; retained for parity).
    * ``position_limit``       : int > 0 — |position| cap (default 3000).
    * ``quantity_cap``         : int > 0 — per-round order cap
                                   (default 500).
    * ``sizing_scale``         : float > 0 — |deviation| → qty scale
                                   (default 3000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContrarianStatistical(CanonicalRulePlayer):
    STRATEGY = "contrarian-statistical"
    DISPLAY_NAME = "Statistical Contrarian"
    SUMMARY = (
        "Position-capped statistical contrarian trader "
        "(Lakonishok, Shleifer & Vishny 1994; Poterba & Summers 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["contrarian_threshold"] = float(
            extras.get("contrarian_threshold", 0.05)
        )
        self.state.custom_state["position_size"] = float(
            extras.get("position_size", 3000.0)
        )
        self.state.custom_state["position_limit"] = int(
            extras.get("position_limit", 3000)
        )
        self.state.custom_state["quantity_cap"] = int(
            extras.get("quantity_cap", 500)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 3000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        theta = self.state.custom_state["contrarian_threshold"]
        cap = self.state.custom_state["quantity_cap"]
        pos_lim = self.state.custom_state["position_limit"]
        sizing = self.state.custom_state["sizing_scale"]

        dev = state.deviation
        if abs(dev) <= theta:
            return hold

        qty = min(cap, round(abs(dev) * sizing))
        if qty <= 0:
            return hold
        if dev > 0:
            if state.position <= -pos_lim:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.position >= pos_lim:
            return hold
        return InvestorOrder.buy(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMContrarianStatistical(CanonicalLLMPlayer):
    STRATEGY = "contrarian-statistical"
    DEFAULT_SYS_PROMPT = """\
You are a statistical contrarian. Your trades are simple, mechanical
bets against deviation from fundamental: sell into premium, buy into
discount, sized proportional to |deviation| with strict per-round and
position caps (Lakonishok, Shleifer & Vishny 1994).

Output format:
<analysis>state the deviation and your sized contrarian order.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade against deviation when |deviation| clears the threshold, subject
to your position and per-round caps; otherwise hold.
"""


__all__ = ["RuleContrarianStatistical", "LLMContrarianStatistical"]
