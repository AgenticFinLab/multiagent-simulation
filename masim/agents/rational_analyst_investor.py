"""RationalAnalystInvestor — Bayesian benchmark; trades only on mispricing.

Theoretical basis: Muth (1961) — Rational Expectations; Fama (1970) — EMH.

Decision rule:
    deviation = (price - fundamental) / fundamental  (from market broadcast)
    If ``|deviation| > threshold`` (default 0.02), trade toward fundamental
    with ``quantity = min(base_position_size, |deviation| * 1000)``.

Parameters (read from ``extras``):
    * ``threshold``: float — deviation magnitude needed to act (default 0.02).
    * ``base_position_size``: float — cap on order size.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleRationalAnalystInvestor(CanonicalRulePlayer):
    STRATEGY = "RationalAnalystInvestor"
    DISPLAY_NAME = "Rational / Analyst Investor"
    SUMMARY = (
        "Bayesian benchmark; trades only when price departs from fundamental "
        "(Muth 1961)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 25.0)
        )

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]

        if abs(state.deviation) <= threshold:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        quantity = min(base, abs(state.deviation) * 1000.0)
        # Price above fundamental → sell; below → buy.
        action = "sell" if state.deviation > 0 else "buy"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMRationalAnalystInvestor(CanonicalLLMPlayer):
    STRATEGY = "RationalAnalystInvestor"
    DEFAULT_SYS_PROMPT = """\
You are a rational analyst with no behavioral biases. You compare the
market price to the published fundamental value. If the deviation is
small, the market is efficient — hold. If the deviation is large,
trade toward fundamental: sell if price is above, buy if below.

Output format:
<analysis>state deviation and whether it warrants trading</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Cash={cash:.2f}, position={position:.2f}.
Trade only when deviation is meaningful; otherwise hold.
"""


__all__ = ["RuleRationalAnalystInvestor", "LLMRationalAnalystInvestor"]
