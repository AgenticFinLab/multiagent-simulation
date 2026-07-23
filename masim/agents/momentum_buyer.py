"""momentum-buyer — Buy-only lookback-momentum trader.

Canonical implementation of the ``momentum-buyer`` archetype documented in
``examples/AGENT_POOL/finance/momentum-buyer.md``. Measures momentum over
a self-maintained price-history lookback and only buys when the signal
exceeds a threshold — never sells.

Theoretical basis:
    Jegadeesh & Titman (1993) — momentum returns.
    De Long, Shleifer, Summers & Waldmann (1990) — positive-feedback
    speculators.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain a rolling price_history list of length lookback+1 via
    on_market_data.

    momentum = (price - price_history[-lookback-1]) / price_history[-lookback-1]

    If ``momentum > threshold`` and ``cash > 0``:
        buy min(int(momentum * base_size * multiplier),
                max_quantity,
                int(cash / price)).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``     : int   — momentum lookback (default 5).
    * ``base_size``    : float — base order size (default 100.0).
    * ``threshold``    : float — momentum trigger (default 0.02).
    * ``multiplier``   : float — momentum-scaling factor (default 3.0).
    * ``max_quantity`` : float — per-round cap (default 500.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumBuyer(CanonicalRulePlayer):
    STRATEGY = "momentum-buyer"
    DISPLAY_NAME = "Buy-Only Lookback Momentum Trader"
    SUMMARY = (
        "Buys when lookback-window momentum exceeds a threshold; never "
        "sells (Jegadeesh-Titman 1993; De Long et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 5))
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 100.0)
        )
        self.state.custom_state["threshold"] = float(
            extras.get("threshold", 0.02)
        )
        self.state.custom_state["multiplier"] = float(
            extras.get("multiplier", 3.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 500.0)
        )
        self.state.custom_state["price_series"] = []  # own rolling series

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        price = market_data.get("price")
        if price is None:
            return
        series: List[float] = self.state.custom_state.setdefault(
            "price_series", []
        )
        series.append(float(price))
        # Cap at lookback+1 so we always have exactly enough history.
        lookback = self.state.custom_state.get("lookback", 5)
        max_len = lookback + 1
        if len(series) > max_len:
            del series[: len(series) - max_len]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lookback = self.state.custom_state["lookback"]
        base = self.state.custom_state["base_size"]
        threshold = self.state.custom_state["threshold"]
        mult = self.state.custom_state["multiplier"]
        max_qty = self.state.custom_state["max_quantity"]
        series: List[float] = self.state.custom_state.get("price_series", [])

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or state.cash <= 0:
            return hold
        if len(series) < lookback + 1:
            return hold
        anchor = series[-lookback - 1]
        if anchor <= 0:
            return hold

        momentum = (state.price - anchor) / anchor
        if momentum <= threshold:
            return hold

        affordable = int(state.cash / state.price)
        raw_qty = int(momentum * base * mult)
        qty = float(min(raw_qty, int(max_qty), max(affordable, 0)))
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMomentumBuyer(CanonicalLLMPlayer):
    STRATEGY = "momentum-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a buy-only lookback-momentum trader. You watch the price over a
short window (about 5 rounds) and only place buy orders when that window
shows strong positive momentum. You never sell — once shares are in your
book they stay. Small or negative momentum means hold.

Output format:
<analysis>state the lookback momentum and whether it clears your threshold.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a buy-only momentum trader: buy on strong positive momentum,
never sell, hold otherwise.
"""


__all__ = ["RuleMomentumBuyer", "LLMMomentumBuyer"]
