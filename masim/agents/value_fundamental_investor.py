"""ValueFundamentalInvestor — gradually learns fundamental via exponential smoothing.

Theoretical basis: Barberis, Shleifer & Vishny (1998); Graham & Dodd (1934).

Decision rule:
    Maintain a belief that updates each round:
        belief(t) = (1 - learning_rate) * belief(t-1) + learning_rate * fundamental
    deviation = (price - belief) / belief
    If ``|deviation| > threshold`` (default 0.02), trade toward belief.

Parameters (read from ``extras``):
    * ``learning_rate``: float, [0, 1] — exponential-smoothing step (default 0.05).
    * ``threshold``: float — deviation threshold to act (default 0.02).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleValueFundamentalInvestor(CanonicalRulePlayer):
    STRATEGY = "ValueFundamentalInvestor"
    DISPLAY_NAME = "Value / Fundamental Investor"
    SUMMARY = (
        "Slow-learning fundamental trader; updates belief gradually "
        "(Barberis-Shleifer-Vishny 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["learning_rate"] = float(
            extras.get("learning_rate", 0.05)
        )
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 25.0)
        )
        self.state.custom_state["belief"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("belief") is None:
            # Start the belief biased toward the first observed price.
            self.state.custom_state["belief"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        lr = self.state.custom_state["learning_rate"]
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]

        belief = self.state.custom_state.get("belief") or state.price
        belief = (1.0 - lr) * belief + lr * state.fundamental
        self.state.custom_state["belief"] = belief

        if belief <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}
        dev = (state.price - belief) / belief
        if abs(dev) <= threshold:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        quantity = min(base, abs(dev) * 1000.0)
        action = "sell" if dev > 0 else "buy"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMValueFundamentalInvestor(CanonicalLLMPlayer):
    STRATEGY = "ValueFundamentalInvestor"
    DEFAULT_SYS_PROMPT = """\
You are a long-horizon value investor. You update your private belief
about fair value slowly toward the published fundamental — you do not
flip overnight. When market price is materially above your slow-moving
belief, you sell; when it is well below, you buy.

Output format:
<analysis>state your belief direction and gap to price</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Cash={cash:.2f}, position={position:.2f}.
Lean toward your slow-updating belief; trade only on a meaningful gap.
"""


__all__ = ["RuleValueFundamentalInvestor", "LLMValueFundamentalInvestor"]
