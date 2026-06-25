"""MarketMakerLiquidityAgent — passive two-sided liquidity provider around an EMA.

Theoretical basis: Glosten & Milgrom (1985); Hendershott et al. (2011);
Kyle (1985).

Decision rule:
    Maintain an EMA of the price with smoothing alpha = 2/(ema_window + 1).
    fair_quote = 0.5 * (price + ema)
    band       = half_spread * fair_quote
    If price < fair_quote - band: post buy-side liquidity.
    If price > fair_quote + band: post sell-side liquidity.

Parameters (read from ``extras``):
    * ``ema_window``: int — EMA window for fair-quote anchor (default 20).
    * ``half_spread``: float — half of the no-trade band as a fraction of
      fair_quote (default 0.015 = 1.5%).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleMarketMakerLiquidityAgent(CanonicalRulePlayer):
    STRATEGY = "MarketMakerLiquidityAgent"
    DISPLAY_NAME = "Market Maker / Liquidity Agent"
    SUMMARY = (
        "Passive two-sided liquidity provider quoting around a short-term EMA "
        "(Glosten-Milgrom 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["ema_window"] = int(extras.get("ema_window", 20))
        self.state.custom_state["half_spread"] = float(
            extras.get("half_spread", 0.015)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 30.0)
        )
        self.state.custom_state["ema"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("ema") is None:
            self.state.custom_state["ema"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        ema_window = self.state.custom_state["ema_window"]
        half_spread = self.state.custom_state["half_spread"]
        base = self.state.custom_state["base_position_size"]

        ema = self.state.custom_state.get("ema") or state.price
        alpha = 2.0 / (ema_window + 1)
        ema = alpha * state.price + (1.0 - alpha) * ema
        self.state.custom_state["ema"] = ema

        fair_quote = 0.5 * (state.price + ema)
        if fair_quote <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}
        band = half_spread * fair_quote

        if state.price < fair_quote - band:
            dev = abs(state.price - fair_quote) / fair_quote
            quantity = min(base, dev * 2000.0)
            return {"action": "buy", "quantity": quantity, "bid_price": state.price}
        if state.price > fair_quote + band:
            dev = abs(state.price - fair_quote) / fair_quote
            quantity = min(base, dev * 2000.0)
            return {"action": "sell", "quantity": quantity, "bid_price": state.price}
        return {"action": "hold", "quantity": 0.0, "bid_price": state.price}


class LLMMarketMakerLiquidityAgent(CanonicalLLMPlayer):
    STRATEGY = "MarketMakerLiquidityAgent"
    DEFAULT_SYS_PROMPT = """\
You are a passive market maker. You maintain a fair quote roughly
equal to a smoothed (EMA-style) reference price. You buy when price
dips below your fair quote minus a half-spread; you sell when price
rises above plus a half-spread. You prefer small, frequent fades —
not directional bets.

Output format:
<analysis>state your reference level and where price sits vs the band</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, prev_price={prev_price:.2f}
(return {price_change:+.2%}), fundamental={fundamental:.2f}.
Cash={cash:.2f}, position={position:.2f}.
Quote a small fade around your smoothed reference; otherwise hold.
"""


__all__ = [
    "RuleMarketMakerLiquidityAgent",
    "LLMMarketMakerLiquidityAgent",
]
