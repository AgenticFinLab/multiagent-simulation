"""value-investor — Graham-style margin-of-safety value investor.

Canonical implementation of the ``value-investor`` archetype documented
in ``examples/AGENT_POOL/finance/value-investor.md``. Buys fixed lots
when price is below fundamental by more than the margin of safety, and
sells fixed lots at symmetric premiums. Never short-sells, never uses
leverage — a patient institutional value buyer providing the price floor.

Theoretical basis:
    Graham & Dodd (1934) — Security Analysis / margin of safety.
    Shleifer & Vishny (1997) — Limits of arbitrage / partial stabilisation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    The profile writes ``dev = (F - P) / F``: positive when price is
    below fundamental. In StandardMarketState the broadcast
    ``state.deviation`` is ``(P - F) / F``; so we simply negate it.

    dev = -state.deviation

    If ``dev > value_discount``:
        buy q = min(base_position_size, cash / price).
    Elif ``dev < -value_discount`` and position > 0:
        sell q = min(base_position_size, position).
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``value_discount``      : float — margin-of-safety threshold
                                 (default 0.15).
    * ``base_position_size``  : float — fixed order size (default 40.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleValueInvestor(CanonicalRulePlayer):
    STRATEGY = "value-investor"
    DISPLAY_NAME = "Graham-Style Value Investor"
    SUMMARY = (
        "Patient margin-of-safety value buyer providing the crash-price "
        "floor (Graham & Dodd 1934; Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["value_discount"] = float(
            extras.get("value_discount", 0.15)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 40.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold

        # Profile-native sign convention: dev > 0 ↔ price below fundamental.
        dev = -state.deviation
        threshold = self.state.custom_state["value_discount"]
        base = self.state.custom_state["base_position_size"]

        if dev > threshold:
            if state.cash <= 0:
                return hold
            quantity = min(base, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev < -threshold and state.position > 0:
            quantity = min(base, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMValueInvestor(CanonicalLLMPlayer):
    STRATEGY = "value-investor"
    DEFAULT_SYS_PROMPT = """\
You are a Graham-style value investor. You buy in fixed lots when price
is well below your fundamental estimate by more than the margin of
safety, and you sell in fixed lots at symmetric premiums. You never
short-sell and you never use leverage; when price is near fundamental
you patiently hold.

Output format:
<analysis>brief reasoning (1-2 sentences) on the margin of safety.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Value-investor discipline: buy fixed lots on deep discounts to
fundamental, sell fixed lots on deep premiums, hold otherwise.
"""


__all__ = ["RuleValueInvestor", "LLMValueInvestor"]
