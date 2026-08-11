"""value-buyer — Contrarian value buyer entering after large discounts.

Canonical implementation of the ``value-buyer`` archetype documented in
``masim/agents/defines/finance/value-buyer.md``. Buys only, and only when
price is materially below the fundamental parity by more than
``discount_threshold``. Uses cash-fraction deployment capped at
``max_buy`` per tick — the "limits of arbitrage" contrarian who provides
partial stabilisation but is capital-constrained.

Theoretical basis:
    Shleifer & Vishny (1997) — The Limits of Arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - parity) / parity

    If ``deviation < -discount_threshold`` and cash > 0:
        buy_qty = floor(cash * cash_fraction / price)
        buy_qty = min(buy_qty, max_buy)
        Emit buy at ``price`` for ``buy_qty`` (0 -> hold).
    Otherwise: hold. Never sells.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``discount_threshold`` : float — minimum discount to enter
                                (default 0.30).
    * ``cash_fraction``      : float — per-round cash deployment fraction
                                (default 0.2).
    * ``max_buy``            : float — per-tick order cap (default 1000.0).
    * ``parity``             : float — fallback parity if fundamental is
                                NaN (default 1.0). Uses ``state.fundamental``
                                when available.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleValueBuyer(CanonicalRulePlayer):
    STRATEGY = "value-buyer"
    DISPLAY_NAME = "Contrarian Value Buyer"
    SUMMARY = (
        "Buy-only capital-constrained contrarian; enters only after deep "
        "discounts from parity (Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["discount_threshold"] = float(
            extras.get("discount_threshold", 0.30)
        )
        self.state.custom_state["cash_fraction"] = float(
            extras.get("cash_fraction", 0.2)
        )
        self.state.custom_state["max_buy"] = float(extras.get("max_buy", 1000.0))
        self.state.custom_state["parity"] = float(extras.get("parity", 1.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        # Missing-signal policy: hold if price/parity reference is missing.
        parity = (
            state.fundamental
            if not math.isnan(state.fundamental)
            else self.state.custom_state["parity"]
        )
        if math.isnan(parity) or parity <= 0 or state.price <= 0:
            return hold

        deviation = (state.price - parity) / parity
        threshold = self.state.custom_state["discount_threshold"]
        if deviation >= -threshold:
            return hold

        cash = state.cash
        if cash <= 0 or cash < state.price:
            return hold

        cash_fraction = self.state.custom_state["cash_fraction"]
        max_buy = self.state.custom_state["max_buy"]

        buy_qty = math.floor(cash * cash_fraction / state.price)
        buy_qty = min(buy_qty, max_buy)
        # Affordability guard.
        buy_qty = min(buy_qty, math.floor(cash / state.price))
        if buy_qty <= 0:
            return hold

        return InvestorOrder.buy(
            quantity=float(buy_qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMValueBuyer(CanonicalLLMPlayer):
    STRATEGY = "value-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian value buyer. You only buy — never sell — and you
only step in when the market price is far below the parity/fundamental
reference by a wide margin. Your capital is finite so you deploy only a
fraction of your remaining cash on each opportunity, capped at a
per-tick maximum.

Output format:
<analysis>brief reasoning (1-2 sentences) on the discount and deployment.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy only at deep discounts, sizing off a fraction of remaining cash;
otherwise hold. Never sell.
"""


__all__ = ["RuleValueBuyer", "LLMValueBuyer"]
