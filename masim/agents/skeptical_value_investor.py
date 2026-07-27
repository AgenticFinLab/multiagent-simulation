"""skeptical-value-investor — Margin-of-safety deep-value buyer.

Canonical implementation of the ``skeptical-value-investor`` archetype
documented in ``examples/AGENT_POOL/finance/skeptical-value-investor.md``.
Buys only when price trades at a large discount to intrinsic value and
sells only on a meaningful premium.

Theoretical basis:
    Graham & Dodd (1934) — margin-of-safety discipline.
    Piotroski (2000) — fundamental-based value screening.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    IV        = fundamental (proxy for intrinsic value)
    discount  = (IV - price) / IV
    premium   = (price - IV) / IV

    if discount > margin_of_safety:  buy  order_size
    elif premium  > sell_premium:    sell order_size
    else:                            hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``margin_of_safety`` : float — required discount to enter
                             (default 0.50).
    * ``sell_premium``     : float — required premium to exit
                             (default 0.10).
    * ``order_size``       : float — fixed order quantity
                             (default 150.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSkepticalValueInvestor(CanonicalRulePlayer):
    STRATEGY = "skeptical-value-investor"
    DISPLAY_NAME = "Skeptical Value Investor"
    SUMMARY = (
        "Buys only at deep discount to intrinsic value and sells on a "
        "meaningful premium (Graham & Dodd 1934; Piotroski 2000)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["margin_of_safety"] = float(
            extras.get("margin_of_safety", 0.50)
        )
        self.state.custom_state["sell_premium"] = float(
            extras.get("sell_premium", 0.10)
        )
        self.state.custom_state["order_size"] = float(
            extras.get("order_size", 150.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental <= 0:
            return hold

        margin = self.state.custom_state["margin_of_safety"]
        sell_premium = self.state.custom_state["sell_premium"]
        size = self.state.custom_state["order_size"]

        iv = state.fundamental
        discount = (iv - state.price) / iv
        premium = (state.price - iv) / iv

        if discount > margin:
            return InvestorOrder.buy(
                quantity=size,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if premium > sell_premium:
            return InvestorOrder.sell(
                quantity=size,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMSkepticalValueInvestor(CanonicalLLMPlayer):
    STRATEGY = "skeptical-value-investor"
    DEFAULT_SYS_PROMPT = """\
You are a sceptical, margin-of-safety value investor. You only buy when
price is a very deep discount to intrinsic value, and only sell when
price runs above intrinsic value by a meaningful premium. Otherwise you
sit tight — patience is your edge.

Output format:
<analysis>state the discount / premium vs intrinsic value and your call.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy on a deep discount, sell on a meaningful premium, otherwise hold.
"""


__all__ = ["RuleSkepticalValueInvestor", "LLMSkepticalValueInvestor"]
