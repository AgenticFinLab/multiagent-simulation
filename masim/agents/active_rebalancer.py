"""active-rebalancer — Contrarian portfolio rebalancer driven by deviation.

Canonical implementation of the ``active-rebalancer`` archetype documented in
``examples/AGENT_POOL/finance/active-rebalancer.md``.

Theoretical basis:
    Markowitz (1952) — mean-variance rebalancing; systematic contrarian
    rebalancing to target weights (Perold & Sharpe 1988).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``|deviation| > rebalance_threshold``:
        quantity = position_size * |deviation| / rebalance_threshold
        deviation > 0  ->  sell   (overweight leg -> trim)
        deviation < 0  ->  buy    (underweight leg -> add)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rebalance_threshold`` : float — deviation cut-off (default 0.05).
    * ``position_size``       : float — base order size (default 350.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleActiveRebalancer(CanonicalRulePlayer):
    STRATEGY = "active-rebalancer"
    DISPLAY_NAME = "Active Portfolio Rebalancer"
    SUMMARY = (
        "Contrarian rebalancer that trims overweight legs and adds to "
        "underweight legs when deviation crosses the rebalance band "
        "(Markowitz 1952; Perold & Sharpe 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["rebalance_threshold"] = float(
            extras.get("rebalance_threshold", 0.05)
        )
        self.state.custom_state["position_size"] = float(
            extras.get("position_size", 350.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["rebalance_threshold"]
        base = self.state.custom_state["position_size"]

        if abs(deviation) <= threshold or threshold <= 0:
            return hold

        quantity = base * abs(deviation) / threshold
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMActiveRebalancer(CanonicalLLMPlayer):
    STRATEGY = "active-rebalancer"
    DEFAULT_SYS_PROMPT = """\
You are an active portfolio rebalancer following Markowitz mean-variance
discipline. You maintain a target allocation and trade contrarian to
mispricing: trim overweight positions when prices rise above fundamental
value and add to underweight positions when prices fall below. Sizing
scales with how far deviation exceeds your rebalance threshold.

Output format:
<analysis>compare deviation to rebalance threshold and state direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Rebalance contrarian: sell if overvalued past the band, buy if
undervalued past the band, hold inside.
"""


__all__ = ["RuleActiveRebalancer", "LLMActiveRebalancer"]
