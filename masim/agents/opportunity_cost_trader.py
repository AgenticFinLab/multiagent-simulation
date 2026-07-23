"""opportunity-cost-trader — Institutional contrarian reallocator.

Canonical implementation of the ``opportunity-cost-trader`` archetype
documented in ``examples/AGENT_POOL/finance/opportunity-cost-trader.md``.
A contrarian reallocator that waits for a relatively large mispricing
before reallocating capital: sells when the asset is meaningfully
overvalued (high opportunity cost of holding), buys when meaningfully
undervalued.

Theoretical basis:
    Chen, Hong & Stein (2002) — institutional reallocation on expected-return
    differentials.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= realloc_threshold``: hold.
    Elif ``deviation > realloc_threshold``: sell (overvalued).
    Elif ``deviation < -realloc_threshold``: buy (undervalued).

    Quantity = ``position_size * |deviation| / realloc_threshold``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``realloc_threshold`` : float — reallocation trigger (default 0.08).
    * ``position_size``     : float — base reallocation size (default 300.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleOpportunityCostTrader(CanonicalRulePlayer):
    STRATEGY = "opportunity-cost-trader"
    DISPLAY_NAME = "Opportunity-Cost Contrarian Reallocator"
    SUMMARY = (
        "Contrarian institutional reallocator: sells meaningfully overvalued "
        "assets, buys meaningfully undervalued ones (Chen, Hong & Stein 2002)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["realloc_threshold"] = float(
            extras.get("realloc_threshold", 0.08)
        )
        self.state.custom_state["position_size"] = float(
            extras.get("position_size", 300.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["realloc_threshold"]
        base = self.state.custom_state["position_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold or threshold <= 0:
            return hold

        quantity = base * abs(deviation) / threshold
        if quantity <= 0:
            return hold
        # Contrarian: sell when overvalued (deviation > 0), buy when undervalued.
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMOpportunityCostTrader(CanonicalLLMPlayer):
    STRATEGY = "opportunity-cost-trader"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian institutional reallocator focused on opportunity
cost. You only move when the mispricing is large enough to justify the
switching cost. When the asset is meaningfully overvalued, holding it
has high opportunity cost — you sell. When it is meaningfully
undervalued, missing it has high opportunity cost — you buy. Small
mispricings are not worth acting on.

Output format:
<analysis>state the deviation and whether the opportunity cost justifies action.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Reallocate contrarian: sell into large positive deviations, buy into
large negative ones, hold when the opportunity cost is below threshold.
"""


__all__ = ["RuleOpportunityCostTrader", "LLMOpportunityCostTrader"]
