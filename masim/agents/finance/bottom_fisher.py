"""bottom-fisher — Crash-reactive bottom-fishing buyer.

Canonical implementation of the ``bottom-fisher`` archetype documented in
``masim/agents/defines/finance/bottom-fisher.md``.

Theoretical basis:
    Lakonishok, Shleifer & Vishny (1994) — contrarian value from bought
    losers; De Bondt & Thaler (1985) — overreaction and reversal.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain own price history (>= lookback entries).
    recent_avg    = mean(price_history[-lookback:])
    discount      = (price - recent_avg) / recent_avg
    price_return  = (price - prev_price) / prev_price

    If price_return < crash_buy_threshold AND
       discount < -discount_threshold:
        quantity = min(max_crash_buy, buy_size * |price_return| * 10)
    Elif discount < -1.5 * discount_threshold:
        quantity = buy_size * 0.5
    Else: hold. (Buy-only. Cold start: hold.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``             : int   — window (default 10).
    * ``crash_buy_threshold``  : float — return trigger (default -0.03).
    * ``discount_threshold``   : float — discount trigger (default 0.10).
    * ``buy_size``             : float — base share unit (default 15.0).
    * ``max_crash_buy``        : float — hard cap (default 25.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBottomFisher(CanonicalRulePlayer):
    STRATEGY = "bottom-fisher"
    DISPLAY_NAME = "Crash-Reactive Bottom Fisher"
    SUMMARY = (
        "Contrarian bottom fisher stepping into sharp declines and "
        "extended discounts (Lakonishok et al. 1994; De Bondt & Thaler "
        "1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 10))
        self.state.custom_state["crash_buy_threshold"] = float(
            extras.get("crash_buy_threshold", -0.03)
        )
        self.state.custom_state["discount_threshold"] = float(
            extras.get("discount_threshold", 0.10)
        )
        self.state.custom_state["buy_size"] = float(
            extras.get("buy_size", 15.0)
        )
        self.state.custom_state["max_crash_buy"] = float(
            extras.get("max_crash_buy", 25.0)
        )
        self.state.custom_state["own_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["own_price_history"]
        history.append(float(market_data["price"]))
        cap = max(64, self.state.custom_state["lookback"] * 4)
        if len(history) > cap:
            del history[: len(history) - cap]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        history: List[float] = self.state.custom_state["own_price_history"]
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        lookback = self.state.custom_state["lookback"]
        if len(history) < lookback or lookback <= 0:
            return hold
        if state.prev_price <= 0:
            return hold

        window = history[-lookback:]
        recent_avg = sum(window) / len(window)
        if recent_avg <= 0:
            return hold
        discount = (state.price - recent_avg) / recent_avg
        price_return = (state.price - state.prev_price) / state.prev_price

        crash_thresh = self.state.custom_state["crash_buy_threshold"]
        disc_thresh = self.state.custom_state["discount_threshold"]
        buy_size = self.state.custom_state["buy_size"]
        max_buy = self.state.custom_state["max_crash_buy"]

        quantity = 0.0
        if price_return < crash_thresh and discount < -disc_thresh:
            quantity = min(max_buy, buy_size * abs(price_return) * 10.0)
        elif discount < -1.5 * disc_thresh:
            quantity = buy_size * 0.5

        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBottomFisher(CanonicalLLMPlayer):
    STRATEGY = "bottom-fisher"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian bottom fisher. You wait for sharp single-tick
declines combined with an extended discount below the recent price
average, then step in with a size proportional to the crash magnitude.
For milder, sustained discounts you take a smaller half-size position.
You never sell; you only buy dips.

Output format:
<analysis>state price return, recent-avg discount, and buy size.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy the dip when a sharp decline coincides with an extended discount;
half-size for milder discounts; otherwise hold.
"""


__all__ = ["RuleBottomFisher", "LLMBottomFisher"]
