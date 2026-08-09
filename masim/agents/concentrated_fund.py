"""concentrated-fund — Margin-call forced-seller fund (sell-only).

Canonical implementation of the ``concentrated-fund`` archetype
documented in ``masim/agents/defines/finance/concentrated-fund.md``.
Sells a fixed fraction of its position when the deviation from
fundamental is deeply negative — models a concentrated, levered fund
that faces margin calls in stress.

Theoretical basis:
    Shleifer & Vishny (1997) — limits of arbitrage; forced liquidations.
    Brunnermeier & Pedersen (2009) — market and funding liquidity
    spirals.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    dev = (price - fundamental) / fundamental
    IF dev < margin_threshold:            # margin_threshold is a NEGATIVE
        SELL min(position, position * trs_sell_ratio)
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``margin_threshold`` : float < 0 — deviation trigger for margin
                              call (default -0.15).
    * ``trs_sell_ratio``   : float in [0, 1] — fraction of position
                              liquidated per trigger (default 0.50).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleConcentratedFund(CanonicalRulePlayer):
    STRATEGY = "concentrated-fund"
    DISPLAY_NAME = "Margin-Call Concentrated Fund"
    SUMMARY = (
        "Forced-seller: liquidates a fixed fraction of position when "
        "deviation is deeply negative "
        "(Shleifer & Vishny 1997; Brunnermeier & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["margin_threshold"] = float(
            extras.get("margin_threshold", -0.15)
        )
        self.state.custom_state["trs_sell_ratio"] = float(
            extras.get("trs_sell_ratio", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        theta = self.state.custom_state["margin_threshold"]
        ratio = self.state.custom_state["trs_sell_ratio"]

        if state.deviation >= theta:
            return hold
        pos = max(state.position, 0.0)
        if pos <= 0:
            return hold
        qty = min(pos, pos * ratio)
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMConcentratedFund(CanonicalLLMPlayer):
    STRATEGY = "concentrated-fund"
    DEFAULT_SYS_PROMPT = """\
You run a concentrated, levered fund. You do not add exposure. When the
market falls deeply below fundamental your prime broker margins you
out, and you must dump a fixed fraction of your position — a
forced-selling amplifier of downside pressure
(Shleifer & Vishny 1997; Brunnermeier & Pedersen 2009).

Output format:
<analysis>state whether the margin trigger has fired.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Sell a fixed fraction of your position only when deviation is deeply
negative; otherwise hold. Never buy.
"""


__all__ = ["RuleConcentratedFund", "LLMConcentratedFund"]
