"""distressed-buyer — Deep-discount distressed-debt buyer.

Canonical implementation of the ``distressed-buyer`` archetype documented
in ``examples/AGENT_POOL/finance/distressed-buyer.md``. When the price
discount from fundamental exceeds a threshold, the agent gradually
deploys cash at a fixed fraction per round up to a per-round share cap.
Never sells.

Theoretical basis:
    Griffin & Xu (2009) — activation of distressed capital.
    Bernanke (2015) — gradual deployment of stabilising liquidity.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If deviation < -discount_threshold and cash >= price:
        buy_qty = min(max_buy, floor(cash * cash_deployment_fraction /
                                     price))
        (floor guard: at least 1 when raw min is 0 but cash >= price)
        Emit buy.
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``discount_threshold``       : float — magnitude of negative
                                     deviation to activate (default 0.20).
    * ``cash_deployment_fraction`` : float in (0, 1] — cash fraction
                                     per active round (default 0.30).
    * ``max_buy``                  : int > 0 — per-round share cap
                                     (default 1000).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDistressedBuyer(CanonicalRulePlayer):
    STRATEGY = "distressed-buyer"
    DISPLAY_NAME = "Distressed-Asset Buyer (Dry-Powder Deployer)"
    SUMMARY = (
        "Deploys dry powder into deep discounts from fundamental "
        "(Griffin & Xu 2009; Bernanke 2015)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["discount_threshold"] = float(
            extras.get("discount_threshold", 0.20)
        )
        self.state.custom_state["cash_deployment_fraction"] = float(
            extras.get("cash_deployment_fraction", 0.30)
        )
        self.state.custom_state["max_buy"] = float(extras.get("max_buy", 1000))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0 or state.cash < state.price:
            return hold

        cs = self.state.custom_state
        discount_threshold = cs["discount_threshold"]
        fraction = cs["cash_deployment_fraction"]
        max_buy = cs["max_buy"]

        if state.deviation >= -discount_threshold:
            return hold

        raw_qty = math.floor(state.cash * fraction / state.price)
        buy_qty = min(max_buy, float(raw_qty))
        # Floor guard per profile: when raw min is 0 but activation
        # condition is met and cash suffices, deploy at least one unit.
        if buy_qty <= 0:
            buy_qty = 1.0
        return InvestorOrder.buy(
            quantity=buy_qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMDistressedBuyer(CanonicalLLMPlayer):
    STRATEGY = "distressed-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a distressed-debt / vulture buyer with a long-horizon mandate.
You do nothing until the price is at a deep discount to fundamental.
Once that threshold triggers, you deploy a fixed fraction of your
remaining dry powder each round, capped at a per-round share limit.
You do NOT sell — you accumulate and wait for recovery.

Output format:
<analysis>state discount depth and whether activation triggers.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
If discount is deep enough, deploy a fixed fraction of cash into a buy
capped at the per-round share limit; otherwise hold.
"""


__all__ = ["RuleDistressedBuyer", "LLMDistressedBuyer"]
