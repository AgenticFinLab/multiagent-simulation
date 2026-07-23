"""block-trade-buyer — Opportunistic block-trade buyer at fire-sale discounts.

Canonical implementation of the ``block-trade-buyer`` archetype documented in
``examples/AGENT_POOL/finance/block-trade-buyer.md``.

Theoretical basis:
    Grossman & Miller (1988) — block liquidity provision with inventory-risk
    compensation; Shleifer & Vishny (1997) — limits of arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``deviation < discount_threshold`` (a negative number):
        buy quantity = (cash * buy_ratio) / price.
    Otherwise: hold. (Buy-only.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``discount_threshold`` : float — required discount (default -0.10).
    * ``buy_ratio``          : float — cash deployment (default 0.30).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBlockTradeBuyer(CanonicalRulePlayer):
    STRATEGY = "block-trade-buyer"
    DISPLAY_NAME = "Opportunistic Block Trade Buyer"
    SUMMARY = (
        "Distressed-block buyer stepping in when price trades at a "
        "material discount to fundamental (Grossman & Miller 1988; "
        "Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["discount_threshold"] = float(
            extras.get("discount_threshold", -0.10)
        )
        self.state.custom_state["buy_ratio"] = float(
            extras.get("buy_ratio", 0.30)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["discount_threshold"]
        if deviation >= threshold:
            return hold
        if state.cash <= 0 or state.price <= 0:
            return hold

        ratio = self.state.custom_state["buy_ratio"]
        quantity = (state.cash * ratio) / state.price
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBlockTradeBuyer(CanonicalLLMPlayer):
    STRATEGY = "block-trade-buyer"
    DEFAULT_SYS_PROMPT = """\
You are an opportunistic block-trade buyer at an asset manager or
family office. You wait for prices to trade materially below
fundamental value on forced-liquidation flow, then deploy a fraction
of your cash to absorb the block. You never sell; you only take
inventory when discounts are wide enough to compensate you.

Output format:
<analysis>state discount vs threshold and cash deployment.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If the discount to fundamental exceeds your threshold, deploy your
cash fraction; otherwise hold.
"""


__all__ = ["RuleBlockTradeBuyer", "LLMBlockTradeBuyer"]
