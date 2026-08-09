"""technical-trader — Dual moving-average crossover trend-follower.

Canonical implementation of the ``technical-trader`` (aka moving-average
crossover trader) archetype documented in
``masim/agents/defines/finance/technical-trader.md``. Maintains a rolling
price buffer, computes short vs long moving averages, and takes a
signal-proportional position in the direction of the crossover.

Theoretical basis:
    Moskowitz, Ooi & Pedersen (2012) — time-series momentum.
    Brock, Lakonishok & LeBaron (1992) — profitability of simple MA rules.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    price_history <- rolling buffer of the last long_window prices
    short_ma       = mean of the last short_window prices
    long_ma        = mean of the full available buffer
    signal         = (short_ma - long_ma) / long_ma

    if  signal >  dead_zone:  buy  qty = int(scale * signal  * (max_position - position))
    elif signal < -dead_zone: sell qty = int(scale * |signal| * (max_position + position))
    else:                     hold

    Insufficient history (< short_window observations) -> hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``short_window`` : int   — short MA lookback (default 3).
    * ``long_window``  : int   — long MA lookback (default 10).
    * ``scale``        : float — signal→quantity multiplier (default 2.0).
    * ``max_position`` : int   — self-imposed |position| cap (default 60).
    * ``dead_zone``    : float — |signal| threshold (default 0.01).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleTechnicalTrader(CanonicalRulePlayer):
    STRATEGY = "technical-trader"
    DISPLAY_NAME = "Moving-Average Crossover Trader"
    SUMMARY = (
        "Signal-proportional MA-crossover trend follower "
        "(Moskowitz-Ooi-Pedersen 2012; Brock-Lakonishok-LeBaron 1992)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["short_window"] = int(
            extras.get("short_window", 3)
        )
        self.state.custom_state["long_window"] = int(
            extras.get("long_window", 10)
        )
        self.state.custom_state["scale"] = float(extras.get("scale", 2.0))
        self.state.custom_state["max_position"] = int(
            extras.get("max_position", 60)
        )
        self.state.custom_state["dead_zone"] = float(
            extras.get("dead_zone", 0.01)
        )
        self.state.custom_state["ma_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        try:
            price = float(market_data["price"])
        except (KeyError, TypeError, ValueError):
            return
        long_window = self.state.custom_state["long_window"]
        buf: List[float] = self.state.custom_state.setdefault("ma_history", [])
        buf.append(price)
        if len(buf) > long_window:
            del buf[: len(buf) - long_window]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        buf: List[float] = self.state.custom_state.get("ma_history") or []
        short_w = self.state.custom_state["short_window"]
        if len(buf) < short_w:
            return hold

        scale = self.state.custom_state["scale"]
        max_pos = self.state.custom_state["max_position"]
        dead = self.state.custom_state["dead_zone"]

        short_ma = sum(buf[-short_w:]) / short_w
        long_ma = sum(buf) / len(buf)
        if long_ma == 0:
            return hold
        signal = (short_ma - long_ma) / long_ma

        position_int = int(state.position)
        if signal > dead:
            capacity = max(0, max_pos - position_int)
            quantity = int(scale * signal * capacity)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if signal < -dead:
            capacity = max(0, max_pos + position_int)
            quantity = int(scale * abs(signal) * capacity)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMTechnicalTrader(CanonicalLLMPlayer):
    STRATEGY = "technical-trader"
    DEFAULT_SYS_PROMPT = """\
You are a dual moving-average crossover trader. You compute a short and
a long moving average from recent prices: when the short MA is above the
long MA by more than your dead-zone you buy the trend, when it is below
you sell, sizing each order by how strong the crossover signal is.

Output format:
<analysis>state the crossover signal and your trend stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy when the short MA is above the long MA by more than your dead-zone,
sell when below, otherwise hold. Size by signal magnitude.
"""


__all__ = ["RuleTechnicalTrader", "LLMTechnicalTrader"]
