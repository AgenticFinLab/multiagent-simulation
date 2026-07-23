"""momentum-chaser — Two-sided velocity chaser.

Canonical implementation of the ``momentum-chaser`` archetype documented
in ``examples/AGENT_POOL/finance/momentum-chaser.md``. Trades both sides
of the market proportional to a lookback-window velocity signal.

Theoretical basis:
    Jegadeesh & Titman (1993) — cross-sectional momentum.
    Moskowitz, Ooi & Pedersen (2012) — time-series momentum.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain a rolling price_series of length lookback+1 via on_market_data.

    velocity = (price - price_series[-lookback-1]) / price_series[-lookback-1]

    If ``|velocity| <= entry_threshold``: hold.
    Else:
        raw_qty = sign(velocity) * min(|velocity| * position_multiplier,
                                        magnitude_cap)
        qty     = |raw_qty|, clamped by cash/price (buy) or position (sell).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback_window``      : int   — momentum lookback (default 5).
    * ``entry_threshold``      : float — |velocity| trigger (default 0.001).
    * ``position_multiplier``  : float — |velocity|→qty factor
                                  (default 2000.0).
    * ``magnitude_cap``        : float — per-round cap (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumChaser(CanonicalRulePlayer):
    STRATEGY = "momentum-chaser"
    DISPLAY_NAME = "Two-Sided Velocity Chaser"
    SUMMARY = (
        "Trades both sides proportional to lookback-window velocity "
        "(Jegadeesh-Titman 1993; Moskowitz et al. 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback_window"] = int(
            extras.get("lookback_window", 5)
        )
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.001)
        )
        self.state.custom_state["position_multiplier"] = float(
            extras.get("position_multiplier", 2000.0)
        )
        self.state.custom_state["magnitude_cap"] = float(
            extras.get("magnitude_cap", 1000.0)
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
        lookback = self.state.custom_state.get("lookback_window", 5)
        max_len = lookback + 1
        if len(series) > max_len:
            del series[: len(series) - max_len]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lookback = self.state.custom_state["lookback_window"]
        threshold = self.state.custom_state["entry_threshold"]
        mult = self.state.custom_state["position_multiplier"]
        cap = self.state.custom_state["magnitude_cap"]
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

        velocity = (state.price - anchor) / anchor
        if abs(velocity) <= threshold:
            return hold

        raw_magnitude = min(abs(velocity) * mult, cap)
        qty = float(raw_magnitude)
        if qty <= 0:
            return hold
        factory = InvestorOrder.buy if velocity > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMomentumChaser(CanonicalLLMPlayer):
    STRATEGY = "momentum-chaser"
    DEFAULT_SYS_PROMPT = """\
You are a two-sided velocity chaser. You look at a short lookback window
and read the sign and magnitude of the price change: strong up-velocity
means buy hard, strong down-velocity means sell hard, tiny velocity means
sit out. Your size scales with |velocity| up to a hard cap.

Output format:
<analysis>state the observed velocity and your resulting stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a velocity chaser: buy on strong up-velocity, sell on strong
down-velocity, hold when velocity is tiny.
"""


__all__ = ["RuleMomentumChaser", "LLMMomentumChaser"]
