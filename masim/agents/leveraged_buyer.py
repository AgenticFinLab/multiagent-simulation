"""leveraged-buyer — Momentum chaser with procyclical leverage.

Canonical implementation of the ``leveraged-buyer`` archetype documented in
``examples/AGENT_POOL/finance/leveraged-buyer.md``. Amplifies short-run
momentum with balance-sheet leverage and is force-deleveraged when equity
falls below a margin call level.

Theoretical basis:
    Adrian & Shin (2010) — Procyclical leverage of financial intermediaries.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    MA_k     = simple moving average of price over ``lookback`` ticks
    momentum = (price - MA_k) / MA_k
    equity   = cash + position * price

    If ``momentum > buy_threshold`` and ``equity > 0``:
        L   = min(leverage_max, equity / margin_base)
        qty = min(base_position_size * L, momentum * sizing_scale)
        qty <= equity * leverage_max / price   (cash-leverage cap)
        buy qty.
    Elif ``equity < margin_call``:
        sell qty = position * deleverage_ratio    (forced deleverage)
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``           : int > 0 (default 5).
    * ``buy_threshold``      : float > 0 (default 0.02).
    * ``leverage_max``       : float > 1 (default 3.0, Adrian & Shin 2010).
    * ``margin_call``        : float > 0 (default 100.0).
    * ``deleverage_ratio``   : float in (0, 1] (default 0.50).
    * ``sizing_scale``       : float > 0 (default 3000.0).
    * ``base_position_size`` : float > 0 (default 200.0).
    * ``margin_base``        : float > 0 (default 100.0).
"""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedBuyer(CanonicalRulePlayer):
    STRATEGY = "leveraged-buyer"
    DISPLAY_NAME = "Leveraged Momentum Buyer"
    SUMMARY = (
        "Procyclical leveraged momentum chaser; force-delevers when equity "
        "breaches the margin call floor (Adrian & Shin 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 5))
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.02)
        )
        self.state.custom_state["leverage_max"] = float(
            extras.get("leverage_max", 3.0)
        )
        self.state.custom_state["margin_call"] = float(
            extras.get("margin_call", 100.0)
        )
        self.state.custom_state["deleverage_ratio"] = float(
            extras.get("deleverage_ratio", 0.50)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 3000.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 200.0)
        )
        self.state.custom_state["margin_base"] = float(
            extras.get("margin_base", 100.0)
        )
        self.state.custom_state["price_window"] = deque(
            maxlen=self.state.custom_state["lookback"]
        )

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        window: Deque[float] = self.state.custom_state["price_window"]
        window.append(float(market_data["price"]))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        window: Deque[float] = self.state.custom_state["price_window"]
        buy_thr = self.state.custom_state["buy_threshold"]
        lev_max = self.state.custom_state["leverage_max"]
        margin_call = self.state.custom_state["margin_call"]
        delev = self.state.custom_state["deleverage_ratio"]
        scale = self.state.custom_state["sizing_scale"]
        base = self.state.custom_state["base_position_size"]
        margin_base = self.state.custom_state["margin_base"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if not window:
            return hold
        ma = sum(window) / len(window)
        if ma <= 0:
            return hold
        momentum = (state.price - ma) / ma
        equity = state.cash + state.position * state.price

        # Forced deleverage takes priority.
        if equity < margin_call and state.position > 0:
            qty = min(state.position, state.position * delev)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if momentum > buy_thr and equity > 0:
            leverage = min(lev_max, equity / margin_base) if margin_base > 0 else lev_max
            raw_qty = min(base * leverage, momentum * scale)
            if state.price > 0:
                cash_cap = equity * lev_max / state.price
                qty = min(raw_qty, cash_cap)
            else:
                qty = raw_qty
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLeveragedBuyer(CanonicalLLMPlayer):
    STRATEGY = "leveraged-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged momentum buyer. You track short-run momentum and use
balance-sheet leverage to amplify long entries when momentum turns
positive. Your leverage grows with equity; when equity falls below the
margin call floor you are forced to sell part of your position.

Output format:
<analysis>report momentum vs threshold and margin status.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Force-deleverage if equity breaches your margin floor; otherwise
leverage-buy on positive momentum; otherwise hold.
"""


__all__ = ["RuleLeveragedBuyer", "LLMLeveragedBuyer"]
