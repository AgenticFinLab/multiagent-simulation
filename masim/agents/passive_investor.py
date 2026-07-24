"""passive-investor — Periodic fixed-target rebalancer.

Canonical implementation of the ``passive-investor`` archetype documented
in ``examples/AGENT_POOL/finance/passive-investor.md``. A patient
buy-and-hold investor with a fixed target allocation. Only trades on
rebalancing rounds and only moves a fraction of the position gap toward
target, clipped by a per-event maximum.

Theoretical basis:
    Garleanu & Pedersen (2013) — dynamic trading with predictable returns
    and transaction costs (partial-adjustment policy).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``round % rebalance_frequency != 0``: hold.
    Else:
        gap          = target_position - position
        raw_quantity = gap * adjustment_rate
        quantity     = clip(raw_quantity, -max_quantity, +max_quantity)
        If quantity > 0: buy quantity.
        Elif quantity < 0: sell abs(quantity).
        Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rebalance_frequency`` : int > 0 — ticks between rebalances
                                  (default 20).
    * ``target_position``     : float — fixed target allocation
                                  (default 30.0).
    * ``adjustment_rate``     : float in [0,1] — gap fraction per rebalance
                                  (default 0.2).
    * ``max_quantity``        : float — per-rebalance cap (default 10.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePassiveInvestor(CanonicalRulePlayer):
    STRATEGY = "passive-investor"
    DISPLAY_NAME = "Periodic Fixed-Target Rebalancer"
    SUMMARY = (
        "Rebalances toward a fixed target only on periodic rounds; moves a "
        "fraction of the gap per event (Garleanu & Pedersen 2013)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["rebalance_frequency"] = int(
            extras.get("rebalance_frequency", 20)
        )
        self.state.custom_state["target_position"] = float(
            extras.get("target_position", 30.0)
        )
        self.state.custom_state["adjustment_rate"] = float(
            extras.get("adjustment_rate", 0.2)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 10.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        freq = self.state.custom_state["rebalance_frequency"]
        target = self.state.custom_state["target_position"]
        rate = self.state.custom_state["adjustment_rate"]
        max_qty = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if freq <= 0 or state.round % freq != 0:
            return hold

        gap = target - state.position
        raw_quantity = gap * rate
        # Clip to [-max_qty, +max_qty].
        quantity = max(-max_qty, min(max_qty, raw_quantity))
        if quantity > 0:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if quantity < 0:
            return InvestorOrder.sell(
                quantity=abs(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPassiveInvestor(CanonicalLLMPlayer):
    STRATEGY = "passive-investor"
    DEFAULT_SYS_PROMPT = """\
You are a patient buy-and-hold investor with a fixed target position.
You only rebalance on scheduled rounds — never in between. On each
rebalancing round, you close a fraction of the gap between your target
and your current position, clipped by a per-event cap. You have no
opinions on price, momentum, or fundamentals.

Output format:
<analysis>state whether this is a rebalancing round and, if so, the gap you are closing.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}. Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Rebalance passively: on scheduled rounds, close a fraction of the
target-vs-position gap (clipped); otherwise hold.
"""


__all__ = ["RulePassiveInvestor", "LLMPassiveInvestor"]
