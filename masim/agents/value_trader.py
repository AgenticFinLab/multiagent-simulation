"""value-trader — Fundamental-anchored value trader ignoring salience.

Canonical implementation of the ``value-trader`` archetype documented in
``examples/AGENT_POOL/finance/value-trader.md``. Trades strictly on the
price-vs-fundamental gap using the ``(F - P) / P`` signal — the
availability-heuristic antithesis: ignores recency and salience,
converges on fundamental value.

Theoretical basis:
    Graham & Dodd (1934) — Security Analysis, margin of safety.
    Tversky & Kahneman (1973) — availability heuristic (contrast).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (fundamental - price) / price

    If ``deviation > buy_threshold`` and cash > 0:
        q = min(base_position_size, deviation * sizing_scale)
        q = min(q, cash / price)  → buy at price.
    Elif ``deviation < -sell_threshold`` and position > 0:
        q = min(position, base_position_size)         → sell at price.
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``buy_threshold``       : float — discount trigger (default 0.05).
    * ``sell_threshold``      : float — premium trigger (default 0.10).
    * ``sizing_scale``        : float — deviation→quantity multiplier
                                 (default 3500.0).
    * ``base_position_size``  : float — per-tick order cap (default 200.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleValueTrader(CanonicalRulePlayer):
    STRATEGY = "value-trader"
    DISPLAY_NAME = "Fundamental-Anchored Value Trader"
    SUMMARY = (
        "Trades strictly on (F-P)/P; ignores salience and recency "
        "(Graham & Dodd 1934; Tversky & Kahneman 1973)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.05)
        )
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", 0.10)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 3500.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 200.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        # Profile-native signal: (F - P) / P — NOT state.deviation, which
        # is (P - F) / F. Keep the profile formula literally.
        deviation = (state.fundamental - state.price) / state.price

        buy_theta = self.state.custom_state["buy_threshold"]
        sell_theta = self.state.custom_state["sell_threshold"]
        sizing = self.state.custom_state["sizing_scale"]
        base = self.state.custom_state["base_position_size"]

        if deviation > buy_theta:
            if state.cash <= 0:
                return hold
            quantity = min(base, deviation * sizing)
            quantity = min(quantity, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation < -sell_theta and state.position > 0:
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


class LLMValueTrader(CanonicalLLMPlayer):
    STRATEGY = "value-trader"
    DEFAULT_SYS_PROMPT = """\
You are a disciplined value trader. You ignore recent-event salience,
media noise, and momentum entirely; you only trade on the objective
gap between the fundamental value and the current price. You buy when
that discount exceeds your buy threshold and sell when the premium
exceeds your sell threshold; otherwise you patiently hold.

Output format:
<analysis>brief reasoning (1-2 sentences) on the price-fundamental gap.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade only on the fundamental-price gap: buy discounts, sell premiums,
hold when close to fair value.
"""


__all__ = ["RuleValueTrader", "LLMValueTrader"]
