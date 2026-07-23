"""opportunistic-trader — Follower speculator amplifying visible attacks.

Canonical implementation of the ``opportunistic-trader`` archetype
documented in ``examples/AGENT_POOL/finance/opportunistic-trader.md``. A
fringe speculator that waits for the price to visibly deviate from
fundamental before trading, then piles in *with* the deviation direction,
amplifying rather than correcting the mispricing.

Theoretical basis:
    Obstfeld (1996) — second-generation currency-crisis coordination.
    Corsetti, Pesenti & Roubini (2004) — herding among fringe speculators.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= follow_threshold``: hold.
    Elif ``deviation > follow_threshold``: buy — amplify upward pressure.
    Elif ``deviation < -follow_threshold``: sell — amplify downward pressure.

    Quantity = ``min(max_quantity, int(|deviation| * scaling_factor))``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``follow_threshold`` : float — visibility threshold (default 0.02).
    * ``scaling_factor``   : float — deviation→quantity factor
                              (default 5000.0).
    * ``max_quantity``     : float — per-tick order cap (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleOpportunisticTrader(CanonicalRulePlayer):
    STRATEGY = "opportunistic-trader"
    DISPLAY_NAME = "Opportunistic Follower Speculator"
    SUMMARY = (
        "Waits for a visible price attack and piles in with the deviation "
        "direction, amplifying rather than correcting "
        "(Obstfeld 1996; Corsetti et al. 2004)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["follow_threshold"] = float(
            extras.get("follow_threshold", 0.02)
        )
        self.state.custom_state["scaling_factor"] = float(
            extras.get("scaling_factor", 5000.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 800.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["follow_threshold"]
        scaling = self.state.custom_state["scaling_factor"]
        max_qty = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        quantity = min(max_qty, float(int(abs(deviation) * scaling)))
        if quantity <= 0:
            return hold
        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMOpportunisticTrader(CanonicalLLMPlayer):
    STRATEGY = "opportunistic-trader"
    DEFAULT_SYS_PROMPT = """\
You are an opportunistic follower speculator. You wait on the sidelines
until you see clear, visible price pressure — a meaningful deviation
from fundamental. Once the move is visible, you join it: you buy into
upward pressure and sell into downward pressure. You never lead, never
fight the deviation, and stand aside when the market is quiet.

Output format:
<analysis>describe the visible deviation and your follow-on decision.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Amplify visible pressure: buy positive deviations, sell negative ones,
hold inside the visibility band.
"""


__all__ = ["RuleOpportunisticTrader", "LLMOpportunisticTrader"]
