"""momentum-follower — Systematic CTA-style trend follower.

Canonical implementation of the ``momentum-follower`` archetype documented
in ``masim/agents/defines/finance/momentum-follower.md``. Buys winners and
sells losers based on a lookback-window return signal, sizing
proportionally to the signal-over-threshold ratio.

Theoretical basis:
    Jegadeesh & Titman (1993) — winner-minus-loser returns.
    Hong & Stein (1999) — unified underreaction/momentum mechanism.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain a rolling price_series of length lookback_period+1.

    m = (price - price_series[-lookback_period-1]) / price_series[-lookback_period-1]

    If ``m > buy_threshold``:
        q_buy = min(cash / price, base_size * m / buy_threshold) — buy.
    Elif ``m < sell_threshold``:
        q_sell = min(position, base_size * |m| / |sell_threshold|) — sell.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback_period`` : int   — momentum lookback (default 20).
    * ``buy_threshold``   : float — buy trigger (default 0.05).
    * ``sell_threshold``  : float — sell trigger (default -0.05).
    * ``base_size``       : float — order size at threshold (default 500.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumFollower(CanonicalRulePlayer):
    STRATEGY = "momentum-follower"
    DISPLAY_NAME = "Systematic Trend-Following CTA"
    SUMMARY = (
        "Buys lookback-window winners and sells losers, sizing by "
        "signal/threshold ratio (Jegadeesh-Titman 1993; Hong-Stein 1999)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback_period"] = int(
            extras.get("lookback_period", 20)
        )
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.05)
        )
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", -0.05)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 500.0)
        )
        self.state.custom_state["price_series"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        price = market_data.get("price")
        if price is None:
            return
        series: List[float] = self.state.custom_state.setdefault(
            "price_series", []
        )
        series.append(float(price))
        lookback = self.state.custom_state.get("lookback_period", 20)
        max_len = lookback + 1
        if len(series) > max_len:
            del series[: len(series) - max_len]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lookback = self.state.custom_state["lookback_period"]
        buy_th = self.state.custom_state["buy_threshold"]
        sell_th = self.state.custom_state["sell_threshold"]
        base = self.state.custom_state["base_size"]
        series: List[float] = self.state.custom_state.get("price_series", [])

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold
        if len(series) < lookback + 1:
            return hold
        anchor = series[-lookback - 1]
        if anchor <= 0:
            return hold

        m = (state.price - anchor) / anchor

        if m > buy_th:
            affordable = state.cash / state.price if state.price > 0 else 0.0
            qty = min(affordable, base * (m / buy_th))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if m < sell_th and sell_th != 0:
            qty = min(state.position, base * abs(m) / abs(sell_th))
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMMomentumFollower(CanonicalLLMPlayer):
    STRATEGY = "momentum-follower"
    DEFAULT_SYS_PROMPT = """\
You are a systematic trend follower (a CTA / managed-futures manager).
You buy on strong positive lookback-window returns and sell on strong
negative lookback-window returns. Size scales with the ratio of the
signal to your trigger threshold, subject to cash / position constraints.
No fundamental view, no contrarianism, no liquidity provision.

Output format:
<analysis>state the lookback return and which side, if any, activates.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a trend follower: buy winners, sell losers, hold when neither
threshold is breached.
"""


__all__ = ["RuleMomentumFollower", "LLMMomentumFollower"]
