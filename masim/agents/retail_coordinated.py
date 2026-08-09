"""retail-coordinated — Coordinated retail cohort buyer.

Canonical implementation of the ``retail-coordinated`` archetype documented
in ``masim/agents/defines/finance/retail-coordinated.md``. Deploys a fixed
fraction of available cash into buys as long as a cash-abundance threshold
is met. Never sells.

Theoretical basis:
    Barber et al. (2022) — Retail order flow in the GameStop episode.
    SEC Staff Report (2021) — Coordinated retail behaviour.
    Lyocsa et al. (2022) — YOLO trading and social-media coordination.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``price <= 0`` or NaN: hold.
    Elif ``cash > price * cash_threshold_multiplier``:
        raw_qty  = int(cash * buy_pressure / price)
        quantity = min(raw_qty, max_buy)
        action   = "buy"
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``buy_pressure``              : float in [0.10, 0.50] — fraction of
                                       cash deployed per round (default 0.12).
    * ``max_buy``                   : int > 0 — cap on shares per order
                                       (default 500).
    * ``cash_threshold_multiplier`` : int > 0 — activation multiplier
                                       (default 50).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRetailCoordinated(CanonicalRulePlayer):
    STRATEGY = "retail-coordinated"
    DISPLAY_NAME = "Coordinated Retail Buyer"
    SUMMARY = (
        "Coordinated retail cohort — deploys a fixed cash fraction on every "
        "activation round; never sells (Barber et al. 2022; SEC 2021)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["buy_pressure"] = float(
            extras.get("buy_pressure", 0.12)
        )
        self.state.custom_state["max_buy"] = int(extras.get("max_buy", 500))
        self.state.custom_state["cash_threshold_multiplier"] = int(
            extras.get("cash_threshold_multiplier", 50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        pressure = self.state.custom_state["buy_pressure"]
        max_buy = self.state.custom_state["max_buy"]
        mult = self.state.custom_state["cash_threshold_multiplier"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or math.isnan(state.price):
            return hold
        if state.cash <= state.price * mult:
            return hold

        raw_qty = int(state.cash * pressure / state.price)
        quantity = min(raw_qty, max_buy)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRetailCoordinated(CanonicalLLMPlayer):
    STRATEGY = "retail-coordinated"
    DEFAULT_SYS_PROMPT = """\
You are a coordinated retail investor participating in a social-media-driven
buying campaign (think WSB during the GameStop squeeze). You buy every
round that you still have meaningful cash on hand, deploying a fixed
fraction of your remaining balance. You never sell — diamond hands is the
entire strategy — and you are indifferent to fundamental valuation.

Output format:
<analysis>state your remaining cash and the size of your next buy.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy a fixed fraction of your cash if the balance is still meaningful.
Never sell — diamond hands regardless of price or fundamental.
"""


__all__ = ["RuleRetailCoordinated", "LLMRetailCoordinated"]
