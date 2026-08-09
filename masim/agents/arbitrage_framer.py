"""arbitrage-framer — Rational-framing arbitrageur.

Canonical implementation of the ``arbitrage-framer`` archetype documented in
``masim/agents/defines/finance/arbitrage-framer.md``.

Theoretical basis:
    Tversky & Kahneman (1981) — framing effects; the "rational framing"
    subset that reframes losses/gains symmetrically and trades to
    fundamental value (Shleifer & Vishny 1997 limits-to-arbitrage baseline).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``|deviation| > rational_threshold``:
        raw_qty = int(|deviation| * rational_scale)
        qty     = min(rational_cap, raw_qty)
        deviation > 0 -> sell   (overvalued)
        deviation < 0 -> buy    (undervalued)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rational_threshold`` : float — trigger threshold (default 0.05).
    * ``rational_scale``     : float — deviation -> quantity gain
                                (default 3000.0).
    * ``rational_cap``       : int  — per-tick quantity cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleArbitrageFramer(CanonicalRulePlayer):
    STRATEGY = "arbitrage-framer"
    DISPLAY_NAME = "Rational Frame Arbitrageur"
    SUMMARY = (
        "Framing-invariant arbitrageur trading contrarian to the "
        "broadcast deviation (Tversky & Kahneman 1981; Shleifer & Vishny "
        "1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["rational_threshold"] = float(
            extras.get("rational_threshold", 0.05)
        )
        self.state.custom_state["rational_scale"] = float(
            extras.get("rational_scale", 3000.0)
        )
        self.state.custom_state["rational_cap"] = int(
            extras.get("rational_cap", 500)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["rational_threshold"]
        if abs(deviation) <= threshold:
            return hold

        scale = self.state.custom_state["rational_scale"]
        cap = self.state.custom_state["rational_cap"]
        raw_qty = int(abs(deviation) * scale)
        quantity = min(cap, raw_qty)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMArbitrageFramer(CanonicalLLMPlayer):
    STRATEGY = "arbitrage-framer"
    DEFAULT_SYS_PROMPT = """\
You are a framing-invariant rational arbitrageur. You ignore how gains
and losses are presented and trade purely against mispricing: buy when
price is below fundamental, sell when above, hold within a small
noise band. Sizes scale linearly with deviation, capped per tick.

Output format:
<analysis>state deviation vs threshold and rational direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade contrarian to deviation: buy if underpriced, sell if overpriced,
hold otherwise; scale by |deviation|.
"""


__all__ = ["RuleArbitrageFramer", "LLMArbitrageFramer"]
