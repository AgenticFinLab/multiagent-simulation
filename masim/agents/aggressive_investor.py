"""aggressive-investor — Momentum-plus-acceleration aggressive investor.

Canonical implementation of the ``aggressive-investor`` archetype documented
in ``examples/AGENT_POOL/finance/aggressive-investor.md``.

Theoretical basis:
    Nofsinger & Sias (1999) — institutional herding on positive-feedback
    momentum with acceleration bonus (De Long, Shleifer, Summers, Waldmann
    1990 positive-feedback traders).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain own price history (>=4 entries).
    r     = (P[-1] - P[-2]) / P[-2]
    accel = (P[-1] - P[-2]) - (P[-2] - P[-3])
    bid   = max(0.01, P[-1] * (1 + kappa * r))
    raw   = beta * r * cash / bid + accel_bonus * accel
    qty   = clip(round(raw), -max_qty, +max_qty)

    Direction is the sign of qty; positive -> buy, negative -> sell.
    Cold start: <2 history -> hold; <4 history -> accel = 0.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``kappa``        : float — bid-price momentum sensitivity (default 1.0).
    * ``beta``         : float — cash deployment coefficient (default 0.5).
    * ``accel_bonus``  : float — acceleration boost (default 0.3).
    * ``max_qty``      : float — absolute per-tick quantity cap (default 80.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleAggressiveInvestor(CanonicalRulePlayer):
    STRATEGY = "aggressive-investor"
    DISPLAY_NAME = "Aggressive Momentum Investor"
    SUMMARY = (
        "Aggressive positive-feedback investor sizing by cash-scaled "
        "momentum plus acceleration (Nofsinger & Sias 1999; DeLong et al. "
        "1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["kappa"] = float(extras.get("kappa", 1.0))
        self.state.custom_state["beta"] = float(extras.get("beta", 0.5))
        self.state.custom_state["accel_bonus"] = float(
            extras.get("accel_bonus", 0.3)
        )
        self.state.custom_state["max_qty"] = float(extras.get("max_qty", 80.0))
        self.state.custom_state["own_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["own_price_history"]
        history.append(float(market_data["price"]))
        # Keep bounded so long runs do not leak memory.
        if len(history) > 32:
            del history[:-32]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        history: List[float] = self.state.custom_state["own_price_history"]
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # Cold start: need at least two prices to compute a return.
        if len(history) < 2:
            return hold

        kappa = self.state.custom_state["kappa"]
        beta = self.state.custom_state["beta"]
        accel_bonus = self.state.custom_state["accel_bonus"]
        max_qty = self.state.custom_state["max_qty"]

        p_last = history[-1]
        p_prev = history[-2]
        if p_prev <= 0:
            return hold
        r = (p_last - p_prev) / p_prev

        if len(history) >= 3:
            p_prev2 = history[-3]
            accel = (p_last - p_prev) - (p_prev - p_prev2)
        else:
            accel = 0.0

        bid = max(0.01, p_last * (1.0 + kappa * r))
        raw_qty = beta * r * state.cash / bid + accel_bonus * accel
        clipped = max(-max_qty, min(max_qty, raw_qty))
        quantity = int(round(clipped))

        if quantity == 0:
            return hold
        if quantity > 0:
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=bid,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=float(-quantity),
            price=bid,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMAggressiveInvestor(CanonicalLLMPlayer):
    STRATEGY = "aggressive-investor"
    DEFAULT_SYS_PROMPT = """\
You are an aggressive positive-feedback investor. You ride momentum
hard: buy into rallies, sell into declines, and boost size when the
price acceleration confirms the trend. You bid above the market when
buying and below when selling to capture the move quickly. You do not
mean-revert on fundamentals.

Output format:
<analysis>state momentum direction, acceleration, and sizing.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Ride momentum: buy on positive returns, sell on negative, boost size
when acceleration confirms the trend.
"""


__all__ = ["RuleAggressiveInvestor", "LLMAggressiveInvestor"]
