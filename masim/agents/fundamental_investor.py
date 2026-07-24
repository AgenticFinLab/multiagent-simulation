"""fundamental-investor — Value-driven long-horizon investor.

Canonical implementation of the ``fundamental-investor`` archetype
documented in ``examples/AGENT_POOL/finance/fundamental-investor.md``.
Buys when price is discounted relative to fundamental and sells when
overvalued; sizes by discount magnitude subject to a base-position cap.

Theoretical basis:
    Graham & Dodd (1934) — Security Analysis.
    Fama & French (1993) — Common risk factors in the returns on stocks
    and bonds.
    Shleifer & Vishny (1997) — The limits of arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    discount = (fundamental - price) / price
    If ``discount > buy_threshold``: buy
        ``min(base_position_size, discount * sizing_scale, cash / price)``.
    Elif ``discount < -sell_threshold`` and ``position > 0``: sell
        ``min(position, base_position_size)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``buy_threshold``      : float — undervaluation gate (default 0.05).
    * ``sell_threshold``     : float — overvaluation gate (default 0.10).
    * ``sizing_scale``       : float — discount→qty factor (default 4000.0).
    * ``base_position_size`` : float — per-tick cap (default 200.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalInvestor(CanonicalRulePlayer):
    STRATEGY = "fundamental-investor"
    DISPLAY_NAME = "Fundamental Investor"
    SUMMARY = (
        "Long-horizon value investor buying discounts and selling premia "
        "(Graham & Dodd 1934; Fama & French 1993)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["buy_threshold"] = float(extras.get("buy_threshold", 0.05))
        cs["sell_threshold"] = float(extras.get("sell_threshold", 0.10))
        cs["sizing_scale"] = float(extras.get("sizing_scale", 4000.0))
        cs["base_position_size"] = float(extras.get("base_position_size", 200.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        buy_th = cs["buy_threshold"]
        sell_th = cs["sell_threshold"]
        sizing = cs["sizing_scale"]
        base = cs["base_position_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or math.isnan(state.fundamental):
            return hold
        discount = (state.fundamental - state.price) / state.price

        if discount > buy_th:
            quantity = min(base, discount * sizing, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if discount < -sell_th and state.position > 0:
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


class LLMFundamentalInvestor(CanonicalLLMPlayer):
    STRATEGY = "fundamental-investor"
    DEFAULT_SYS_PROMPT = """\
You are a long-horizon value investor. You buy when price trades at a
meaningful discount to fundamental value, and you sell when price is
significantly above fundamental. You size trades by the magnitude of
the discount, subject to a base position cap.

Output format:
<analysis>state the discount vs fundamental and your value stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy discounts, sell premia, hold in between.
"""


__all__ = ["RuleFundamentalInvestor", "LLMFundamentalInvestor"]
