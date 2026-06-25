"""MomentumTrendTrader — follows recent price trends.

Theoretical basis: Jegadeesh & Titman (1993); Moskowitz, Ooi & Pedersen (2012).

Decision rule:
    return_pct = (price - prev_price) / prev_price
    If ``|return_pct| > entry_threshold`` (default 0.02), trade in the
    direction of the move with ``quantity = min(base_position_size, |return_pct| * 1000)``.

Parameters (read from ``extras``):
    * ``entry_threshold``: float — minimum return magnitude to trigger entry
      (default 0.02).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleMomentumTrendTrader(CanonicalRulePlayer):
    STRATEGY = "MomentumTrendTrader"
    DISPLAY_NAME = "Momentum / Trend Trader"
    SUMMARY = (
        "Follows recent price moves; buys rising prices, sells falling ones "
        "(Jegadeesh-Titman 1993)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.02)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        threshold = self.state.custom_state["entry_threshold"]
        base = self.state.custom_state["base_position_size"]

        if abs(state.price_change) <= threshold:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        quantity = min(base, abs(state.price_change) * 1000.0)
        action = "buy" if state.price_change > 0 else "sell"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMMomentumTrendTrader(CanonicalLLMPlayer):
    STRATEGY = "MomentumTrendTrader"
    DEFAULT_SYS_PROMPT = """\
You are a momentum trader. You believe trends persist in the short term.
When the most recent return is positive and meaningful, you buy; when it
is negative and meaningful, you sell. Small moves are noise — hold.

Output format:
<analysis>state the recent return and whether it crosses your threshold</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, prev_price={prev_price:.2f}
(return {price_change:+.2%}), fundamental={fundamental:.2f}.
Cash={cash:.2f}, position={position:.2f}.
If the recent return is large enough, ride it; otherwise hold.
"""


__all__ = ["RuleMomentumTrendTrader", "LLMMomentumTrendTrader"]
