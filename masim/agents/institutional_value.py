"""institutional-value — Sell-only fundamental value investor.

Canonical implementation of the ``institutional-value`` archetype documented
in ``examples/AGENT_POOL/finance/institutional-value.md``. Sells shares into
overvaluation once ``deviation`` exceeds a valuation threshold and holds
otherwise — never buys.

Theoretical basis:
    Shleifer & Vishny (1997) — Limits to arbitrage (capital-constrained
    stabiliser).
    Graham & Dodd (1934) — Fundamental value discipline.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``deviation <= sell_threshold`` OR ``position <= 0``: hold.
    Else: sell ``quantity = min(max_sell, position)``.

    The agent NEVER buys; its inventory is monotonically non-increasing.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``sell_threshold``  : float > 0 — minimum overvaluation triggering
                             sell (default 0.30, Shleifer & Vishny 1997).
    * ``max_sell``        : float > 0 — maximum shares sold per round
                             (default 1000.0, Campbell et al. 2009).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInstitutionalValue(CanonicalRulePlayer):
    STRATEGY = "institutional-value"
    DISPLAY_NAME = "Institutional Value Seller"
    SUMMARY = (
        "Sell-only fundamental value investor that provides the stabilising "
        "supply into overvaluation (Shleifer & Vishny 1997; Graham & Dodd 1934)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", 0.30)
        )
        self.state.custom_state["max_sell"] = float(extras.get("max_sell", 1000.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        sell_threshold = self.state.custom_state["sell_threshold"]
        max_sell = self.state.custom_state["max_sell"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or math.isnan(state.fundamental) or state.fundamental <= 0:
            return hold
        deviation = state.deviation
        if math.isnan(deviation):
            return hold
        if deviation <= sell_threshold:
            return hold
        if state.position <= 0:
            return hold

        quantity = min(max_sell, state.position)
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMInstitutionalValue(CanonicalLLMPlayer):
    STRATEGY = "institutional-value"
    DEFAULT_SYS_PROMPT = """\
You are a fundamental value investor at a large institution (pension fund,
long-only value fund). Your discipline is strict: you sell shares from a
finite inventory when price meaningfully exceeds fundamental value, and
you hold otherwise. You NEVER buy under any circumstance — you are a
pure seller/holder providing supply into overvaluation.

Output format:
<analysis>state the deviation vs your sell threshold and inventory.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Sell into overvaluation if deviation exceeds your sell threshold and you
still hold inventory; otherwise hold. Do not buy.
"""


__all__ = ["RuleInstitutionalValue", "LLMInstitutionalValue"]
