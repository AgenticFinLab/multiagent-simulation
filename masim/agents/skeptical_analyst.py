"""skeptical-analyst — Contrarian value-scepticism trader.

Canonical implementation of the ``skeptical-analyst`` archetype documented
in ``examples/AGENT_POOL/finance/skeptical-analyst.md``. Fades price-vs-
fundamental deviations by buying undervaluation and selling overvaluation
once the gap exceeds a scepticism threshold.

Theoretical basis:
    Grossman & Stiglitz (1980) — informed traders exploit mispricings.
    Shleifer & Vishny (1997) — limits to arbitrage on large deviations.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    if |deviation| > sceptic_threshold:
        deviation > 0  -> sell (fade over-valuation)
        deviation < 0  -> buy  (fade under-valuation)
    quantity = min(max_order, |deviation| * quantity_scale)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``sceptic_threshold`` : float — activation deviation
                              (default 0.05).
    * ``quantity_scale``    : float — |dev|→quantity multiplier
                              (default 3000.0).
    * ``max_order``         : float — order-size cap per round
                              (default 500.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSkepticalAnalyst(CanonicalRulePlayer):
    STRATEGY = "skeptical-analyst"
    DISPLAY_NAME = "Skeptical Analyst"
    SUMMARY = (
        "Fades large price-vs-fundamental deviations from a sceptical "
        "prior (Grossman-Stiglitz 1980; Shleifer-Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["sceptic_threshold"] = float(
            extras.get("sceptic_threshold", 0.05)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["max_order"] = float(extras.get("max_order", 500.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["sceptic_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        cap = self.state.custom_state["max_order"]

        deviation = state.deviation
        if abs(deviation) <= threshold:
            return hold

        quantity = min(cap, abs(deviation) * scale)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSkepticalAnalyst(CanonicalLLMPlayer):
    STRATEGY = "skeptical-analyst"
    DEFAULT_SYS_PROMPT = """\
You are a sceptical fundamental analyst. You distrust extreme
price-vs-fundamental gaps: when the market flies above fundamental you
lean into selling, when it collapses below fundamental you lean into
buying, sized by how large the gap is.

Output format:
<analysis>call the direction of the mispricing and your fade stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Fade large deviations: sell when price is well above fundamental, buy
when well below, hold otherwise.
"""


__all__ = ["RuleSkepticalAnalyst", "LLMSkepticalAnalyst"]
