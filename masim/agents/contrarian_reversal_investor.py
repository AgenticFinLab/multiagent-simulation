"""ContrarianReversalInvestor — bets against recent cumulative trends.

Theoretical basis: De Bondt & Thaler (1985); Jegadeesh (1990).

Decision rule:
    Maintain a ring of the last ``lookback_window + 1`` prices.
    cum_return = (price - price_lookback_ago) / price_lookback_ago
    If ``|cum_return| > entry_threshold`` (default 0.05), trade *against* it.

Parameters (read from ``extras``):
    * ``lookback_window``: int — how many rounds back to compare against
      (default 10).
    * ``entry_threshold``: float — cumulative return threshold (default 0.05).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleContrarianReversalInvestor(CanonicalRulePlayer):
    STRATEGY = "ContrarianReversalInvestor"
    DISPLAY_NAME = "Contrarian / Reversal Investor"
    SUMMARY = (
        "Bets against extended trends; sells after rallies, buys after "
        "drawdowns (De Bondt-Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback_window"] = int(
            extras.get("lookback_window", 10)
        )
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.05)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["recent_prices"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        recent = self.state.custom_state["recent_prices"]
        recent.append(float(market_data["price"]))
        lookback = self.state.custom_state["lookback_window"]
        if len(recent) > lookback + 1:
            self.state.custom_state["recent_prices"] = recent[-(lookback + 1):]

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        lookback = self.state.custom_state["lookback_window"]
        threshold = self.state.custom_state["entry_threshold"]
        base = self.state.custom_state["base_position_size"]
        recent = self.state.custom_state["recent_prices"]

        if len(recent) <= lookback:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        ref_price = recent[-(lookback + 1)]
        if ref_price <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        cum_return = (state.price - ref_price) / ref_price
        if abs(cum_return) <= threshold:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        quantity = min(base, abs(cum_return) * 400.0)
        # Contrarian: sell after rallies, buy after drops.
        action = "sell" if cum_return > 0 else "buy"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMContrarianReversalInvestor(CanonicalLLMPlayer):
    STRATEGY = "ContrarianReversalInvestor"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian investor. You believe sustained rallies and
sustained drops both invite reversal. You compare today's price to a
longer-window reference (e.g. ~10 rounds back). When the cumulative
move is large, you trade against it; otherwise you wait.

Output format:
<analysis>state the rough multi-round move and your reversal thesis</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, prev_price={prev_price:.2f}
(1-round return {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Cash={cash:.2f}, position={position:.2f}.
Lean against an extended move; otherwise hold.
"""


__all__ = ["RuleContrarianReversalInvestor", "LLMContrarianReversalInvestor"]
