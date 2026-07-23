"""momentum-speculator — Leveraged short-window momentum speculator.

Canonical implementation of the ``momentum-speculator`` archetype documented
in ``examples/AGENT_POOL/finance/momentum-speculator.md``. Chases a very
short moving-average momentum signal and amplifies buy-side positions via a
leverage multiplier; sells the entire held position when momentum turns
sharply negative.

Theoretical basis:
    Jegadeesh & Titman (1993) — short-horizon momentum returns.
    Adrian & Shin (2010) — pro-cyclical leverage in financial intermediaries.
    De Long, Shleifer, Summers & Waldmann (1990) — positive-feedback trading.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    MA_k     = mean(price_history[-lookback:])
    momentum = (price - MA_k) / MA_k

    If ``momentum > buy_threshold``:
        buy — quantity = min(base_position_size * leverage,
                              momentum * sizing_scale).
    If ``momentum < sell_threshold``:
        sell — quantity = min(position, base_position_size).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``            : int > 0 — MA window (default 5).
    * ``buy_threshold``       : float — momentum cut-off for entry (default 0.01).
    * ``sell_threshold``      : float — momentum cut-off for exit
                                 (default -0.02).
    * ``leverage``            : float — buy-side amplification (default 2.0).
    * ``sizing_scale``        : float — momentum→quantity factor
                                 (default 5000.0).
    * ``base_position_size``  : float — base order cap (default 300.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumSpeculator(CanonicalRulePlayer):
    STRATEGY = "momentum-speculator"
    DISPLAY_NAME = "Leveraged Momentum Speculator"
    SUMMARY = (
        "Chases short-window moving-average momentum with leverage; "
        "amplifies trends and rides them until they invert "
        "(Jegadeesh & Titman 1993; Adrian & Shin 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 5))
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.01)
        )
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", -0.02)
        )
        self.state.custom_state["leverage"] = float(extras.get("leverage", 2.0))
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 300.0)
        )
        # Own rolling history — HistoryBuffer at custom_state["price_history"]
        # is only provisioned when extras.record_path is set, so we keep our
        # own plain list to guarantee availability.
        self.state.custom_state["prices"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        prices = self.state.custom_state["prices"]
        prices.append(float(market_data["price"]))
        # Bound memory: only need the last `lookback` observations.
        lookback = self.state.custom_state["lookback"]
        if len(prices) > lookback + 2:
            del prices[: len(prices) - (lookback + 2)]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lookback = self.state.custom_state["lookback"]
        buy_th = self.state.custom_state["buy_threshold"]
        sell_th = self.state.custom_state["sell_threshold"]
        leverage = self.state.custom_state["leverage"]
        sizing = self.state.custom_state["sizing_scale"]
        base = self.state.custom_state["base_position_size"]
        prices = self.state.custom_state["prices"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # Need a full window (excluding current tick) to form the MA.
        history = prices[:-1] if len(prices) >= 1 else []
        if len(history) < lookback:
            return hold
        window = history[-lookback:]
        ma_k = sum(window) / lookback
        if ma_k <= 0:
            return hold
        momentum = (state.price - ma_k) / ma_k

        if momentum > buy_th:
            quantity = min(base * leverage, momentum * sizing)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if momentum < sell_th:
            position = float(self.state.custom_state.get("position", 0.0))
            quantity = min(max(position, 0.0), base)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMMomentumSpeculator(CanonicalLLMPlayer):
    STRATEGY = "momentum-speculator"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged momentum speculator. You track a very short moving
average of recent prices and only enter when the current price breaks
away from it. When momentum is positive you lean in aggressively with
leverage; when momentum turns sharply negative you unwind. Between
signals you stand aside — you are not a contrarian and you never fight
the trend.

Output format:
<analysis>describe the short-term momentum against your MA and your leverage stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide by chasing the short-term momentum: leveraged buy on strong
positive momentum, exit on sharp negative momentum, hold when the
market is flat.
"""


__all__ = ["RuleMomentumSpeculator", "LLMMomentumSpeculator"]
