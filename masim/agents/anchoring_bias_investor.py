"""AnchoringBiasInvestor — anchors to first observed price, adjusts insufficiently.

Theoretical basis: Tversky & Kahneman (1974); Northcraft & Neale (1987);
Campbell & Sharpe (2009).

Decision rule:
    On the first market broadcast, fix ``anchor_price = price``.
    Each round, compute
        adjusted_target = anchor_price + (fundamental - anchor_price) * adjustment_factor
        perceived_dev   = (price - adjusted_target) / adjusted_target
    If ``|perceived_dev| > entry_threshold`` (default 0.03), trade in the
    corrective direction with ``quantity = min(base_position_size, |perceived_dev| * 1000)``.

Parameters (read from ``extras``):
    * ``adjustment_factor``: float, [0, 1] — fraction of distance to fundamental
      that the agent's anchor "moves toward" each round (default 0.3).
    * ``entry_threshold``: float — perceived-deviation threshold to act
      (default 0.03).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleAnchoringBiasInvestor(CanonicalRulePlayer):
    STRATEGY = "AnchoringBiasInvestor"
    DISPLAY_NAME = "Anchoring-Bias Investor"
    SUMMARY = (
        "Anchors to the first observed price; adjusts insufficiently toward "
        "fundamental (Tversky-Kahneman 1974)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["adjustment_factor"] = float(
            extras.get("adjustment_factor", 0.3)
        )
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.03)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["anchor_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("anchor_price") is None:
            self.state.custom_state["anchor_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        anchor = self.state.custom_state.get("anchor_price") or state.price
        adj = self.state.custom_state["adjustment_factor"]
        threshold = self.state.custom_state["entry_threshold"]
        base = self.state.custom_state["base_position_size"]

        adjusted_target = anchor + (state.fundamental - anchor) * adj
        if adjusted_target <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}
        perceived_dev = (state.price - adjusted_target) / adjusted_target

        if abs(perceived_dev) <= threshold:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        quantity = min(base, abs(perceived_dev) * 1000.0)
        action = "buy" if perceived_dev < 0 else "sell"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMAnchoringBiasInvestor(CanonicalLLMPlayer):
    STRATEGY = "AnchoringBiasInvestor"
    DEFAULT_SYS_PROMPT = """\
You are an anchoring-bias investor. The first price you ever observed
feels like the "right" price; you only partially adjust toward the
published fundamental, never fully. When current price seems far from
your anchored expectation, you trade against the perceived deviation;
otherwise you hold.

Output format:
<analysis>state your current anchor and how price compares</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Cash={cash:.2f}, position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide based on your anchored expectation: buy if price is far below
your anchor-adjusted target, sell if far above, otherwise hold.
"""


__all__ = ["RuleAnchoringBiasInvestor", "LLMAnchoringBiasInvestor"]
