"""slow-adapter — Slow-updating perceived-value trader.

Canonical implementation of the ``slow-adapter`` archetype documented in
``masim/agents/defines/finance/slow-adapter.md``. Anchors perceived value
to a slow moving average of recent prices with a small fundamental
weight, and takes small trades against the perceived deviation.

Theoretical basis:
    Barberis, Shleifer & Vishny (1998) — under-reaction and slow diffusion
    of information.
    Hong & Stein (1999) — gradual information flow among heterogeneous
    investors.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    ma        = mean of last ``window`` observed prices
    perceived = fund_weight * fundamental + (1 - fund_weight) * ma
    dev       = (perceived - price) / price

    if |dev| > threshold:
        qty = clamp(sizing * dev, -max_order, +max_order)
        buy if qty > 0 else sell

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``window``       : int   — MA window length (default 10).
    * ``fund_weight``  : float — weight on fundamental in perceived value
                         (default 0.1).
    * ``threshold``    : float — activation |dev| threshold
                         (default 0.02).
    * ``sizing``       : float — dev→quantity multiplier (default 10.0).
    * ``max_order``    : float — order-size cap (default 10.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSlowAdapter(CanonicalRulePlayer):
    STRATEGY = "slow-adapter"
    DISPLAY_NAME = "Slow Adapter"
    SUMMARY = (
        "Anchors to a slow price MA blended with a small fundamental "
        "weight; under-reacts to information (Barberis-Shleifer-Vishny "
        "1998; Hong-Stein 1999)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["window"] = int(extras.get("window", 10))
        self.state.custom_state["fund_weight"] = float(
            extras.get("fund_weight", 0.1)
        )
        self.state.custom_state["threshold"] = float(
            extras.get("threshold", 0.02)
        )
        self.state.custom_state["sizing"] = float(extras.get("sizing", 10.0))
        self.state.custom_state["max_order"] = float(extras.get("max_order", 10.0))
        self.state.custom_state["price_window"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        try:
            price = float(market_data["price"])
        except (KeyError, TypeError, ValueError):
            return
        window = self.state.custom_state["window"]
        buf: List[float] = self.state.custom_state.setdefault("price_window", [])
        buf.append(price)
        if len(buf) > window:
            del buf[: len(buf) - window]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        buf: List[float] = self.state.custom_state.get("price_window") or []
        if not buf or state.price <= 0:
            return hold

        fund_weight = self.state.custom_state["fund_weight"]
        threshold = self.state.custom_state["threshold"]
        sizing = self.state.custom_state["sizing"]
        cap = self.state.custom_state["max_order"]

        ma = sum(buf) / len(buf)
        fundamental = state.fundamental
        if math.isnan(fundamental):
            perceived = ma
        else:
            perceived = fund_weight * fundamental + (1.0 - fund_weight) * ma

        dev = (perceived - state.price) / state.price
        if abs(dev) <= threshold:
            return hold

        raw_qty = sizing * dev
        clamped = max(-cap, min(cap, raw_qty))
        quantity = abs(clamped)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.buy if clamped > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSlowAdapter(CanonicalLLMPlayer):
    STRATEGY = "slow-adapter"
    DEFAULT_SYS_PROMPT = """\
You are a slow-adapting investor. Your view of fair value is mostly a
moving average of recent prices with only a tiny weight on the newest
fundamental. You trade small positions against the gap between this slow
perceived value and the current price.

Output format:
<analysis>state your perceived value vs price and your under-reaction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Anchor to your slow moving average, take a small trade if the gap is
material, otherwise hold.
"""


__all__ = ["RuleSlowAdapter", "LLMSlowAdapter"]
