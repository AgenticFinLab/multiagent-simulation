"""commitment-escalator — Sunk-cost escalation of commitment (buy-only).

Canonical implementation of the ``commitment-escalator`` archetype
documented in ``examples/AGENT_POOL/finance/commitment-escalator.md``.
Doubles down in losses (larger orders when deviation is more negative)
and adds modestly in gains — the classic escalation-of-commitment /
sunk-cost fallacy.

Theoretical basis:
    Staw (1976) — knee-deep in the big muddy: study of escalating
    commitment.
    Arkes & Blumer (1985) — the psychology of sunk cost.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    dev = (price - fundamental) / fundamental
    IF dev < -escalation_threshold:                # loss regime
        qty = escalation_size * |dev| / escalation_threshold
        BUY qty
    ELIF dev >  escalation_threshold:              # gain regime
        qty = escalation_size * 0.5 * dev / escalation_threshold
        BUY qty                                    # never sells
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``escalation_threshold`` : float > 0 — deviation trigger
                                  (default 0.05).
    * ``escalation_size``      : float > 0 — base commit size
                                  (default 400.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCommitmentEscalator(CanonicalRulePlayer):
    STRATEGY = "commitment-escalator"
    DISPLAY_NAME = "Sunk-Cost Commitment Escalator"
    SUMMARY = (
        "Doubles down in losses and adds modestly in gains — "
        "escalation of commitment (Staw 1976; Arkes & Blumer 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["escalation_threshold"] = float(
            extras.get("escalation_threshold", 0.05)
        )
        self.state.custom_state["escalation_size"] = float(
            extras.get("escalation_size", 400.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        theta = self.state.custom_state["escalation_threshold"]
        size = self.state.custom_state["escalation_size"]
        if theta <= 0:
            return hold
        dev = state.deviation

        if dev < -theta:
            qty = size * abs(dev) / theta
        elif dev > theta:
            qty = size * 0.5 * dev / theta
        else:
            return hold
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMCommitmentEscalator(CanonicalLLMPlayer):
    STRATEGY = "commitment-escalator"
    DEFAULT_SYS_PROMPT = """\
You escalate commitment. In losses (price below fundamental) you buy
aggressively — the deeper the loss, the larger the add. In gains you
add modestly. You NEVER sell — cutting losses would be an admission of
having been wrong (Staw 1976; Arkes & Blumer 1985).

Output format:
<analysis>state whether you are in a loss or gain regime and how big you commit.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy larger when deviation is deeply negative, buy modestly when
deviation is positive past the threshold, hold otherwise. Never sell.
"""


__all__ = ["RuleCommitmentEscalator", "LLMCommitmentEscalator"]
