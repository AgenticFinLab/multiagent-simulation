"""balanced-analyst — Hybrid fundamental-plus-trend balanced analyst.

Canonical implementation of the ``balanced-analyst`` archetype documented in
``examples/AGENT_POOL/finance/balanced-analyst.md``.

Theoretical basis:
    Grossman & Stiglitz (1980) — informed traders combining fundamental
    and price information; Fama & French (1988) — momentum + value hybrid.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain price_prev, seeded on first market broadcast.
    f_signal  = (fundamental - price) / fundamental
    t_signal  = (price - price_prev) / price_prev
    composite = w_f * f_signal + w_t * t_signal

    If ``composite > conviction_threshold``:
        buy  qty = base_size * composite * score_scale.
    If ``composite < -conviction_threshold``:
        sell qty = base_size * |composite| * score_scale.
    Otherwise: hold. price_prev <- price at end.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``w_f``                 : float — fundamental weight (default 0.5).
    * ``w_t``                 : float — trend weight        (default 0.5).
    * ``conviction_threshold``: float — trigger             (default 0.02).
    * ``base_size``           : float — base order size     (default 500.0).
    * ``score_scale``         : float — composite -> qty    (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBalancedAnalyst(CanonicalRulePlayer):
    STRATEGY = "balanced-analyst"
    DISPLAY_NAME = "Balanced Fundamental+Trend Analyst"
    SUMMARY = (
        "Balanced analyst combining fundamental deviation and short-term "
        "trend into a composite signal (Grossman & Stiglitz 1980; Fama & "
        "French 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["w_f"] = float(extras.get("w_f", 0.5))
        self.state.custom_state["w_t"] = float(extras.get("w_t", 0.5))
        self.state.custom_state["conviction_threshold"] = float(
            extras.get("conviction_threshold", 0.02)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 500.0)
        )
        self.state.custom_state["score_scale"] = float(
            extras.get("score_scale", 5000.0)
        )
        self.state.custom_state["price_prev"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Seed price_prev on the very first broadcast so t_signal is 0 the
        # first round rather than undefined.
        if self.state.custom_state.get("price_prev") is None:
            self.state.custom_state["price_prev"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental <= 0:
            self.state.custom_state["price_prev"] = state.price
            return hold

        price_prev = self.state.custom_state.get("price_prev")
        if price_prev is None or price_prev <= 0:
            self.state.custom_state["price_prev"] = state.price
            return hold

        w_f = self.state.custom_state["w_f"]
        w_t = self.state.custom_state["w_t"]
        threshold = self.state.custom_state["conviction_threshold"]
        base = self.state.custom_state["base_size"]
        scale = self.state.custom_state["score_scale"]

        f_signal = (state.fundamental - state.price) / state.fundamental
        t_signal = (state.price - price_prev) / price_prev
        composite = w_f * f_signal + w_t * t_signal

        # Update price_prev regardless of trade decision so it tracks price.
        self.state.custom_state["price_prev"] = state.price

        if composite > threshold:
            quantity = base * composite * scale
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if composite < -threshold:
            quantity = base * abs(composite) * scale
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMBalancedAnalyst(CanonicalLLMPlayer):
    STRATEGY = "balanced-analyst"
    DEFAULT_SYS_PROMPT = """\
You are a balanced sell-side analyst. You blend a fundamental signal
(fair value versus price) with a short-term trend signal (price vs
previous tick) into a single composite score. You buy when the
composite crosses your conviction threshold to the upside, sell when
it crosses to the downside, and hold otherwise.

Output format:
<analysis>state fundamental signal, trend signal, and composite.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Blend fundamental and trend into a composite; trade when the composite
crosses your conviction threshold.
"""


__all__ = ["RuleBalancedAnalyst", "LLMBalancedAnalyst"]
