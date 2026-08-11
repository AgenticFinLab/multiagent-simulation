"""passive-bystander — Rationally inattentive stabiliser.

Canonical implementation of the ``passive-bystander`` archetype documented
in ``masim/agents/defines/finance/passive-bystander.md``. A rationally
inattentive investor who only acts on gross deviations from fundamental —
buying extreme underpricings and selling extreme overpricings at a fixed
rebalance size.

Theoretical basis:
    Sims (2003) — rational inattention.
    Gabaix (2014) — sparse maxima and inattention.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``deviation < -inaction_threshold`` AND cash > 0:
        buy — quantity = ``min(cash / price, rebalance_size)``.
    Elif ``deviation > inaction_threshold`` AND position > 0:
        sell — quantity = ``min(position, rebalance_size)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``inaction_threshold`` : float — deviation cut-off (default 0.15).
    * ``rebalance_size``     : float — fixed order size (default 200.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePassiveBystander(CanonicalRulePlayer):
    STRATEGY = "passive-bystander"
    DISPLAY_NAME = "Rationally Inattentive Bystander"
    SUMMARY = (
        "Only acts on gross deviations from fundamental — extreme "
        "underpricings buy, extreme overpricings sell "
        "(Sims 2003; Gabaix 2014)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["inaction_threshold"] = float(
            extras.get("inaction_threshold", 0.15)
        )
        self.state.custom_state["rebalance_size"] = float(
            extras.get("rebalance_size", 200.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["inaction_threshold"]
        rebalance = self.state.custom_state["rebalance_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        if deviation < -threshold and state.cash > 0 and state.price > 0:
            quantity = min(state.cash / state.price, rebalance)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation > threshold and state.position > 0:
            quantity = min(state.position, rebalance)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPassiveBystander(CanonicalLLMPlayer):
    STRATEGY = "passive-bystander"
    DEFAULT_SYS_PROMPT = """\
You are a rationally inattentive bystander. Paying attention and
executing trades is costly, so most of the time you do nothing. Only a
gross deviation from fundamental — well past routine noise — is enough
to justify a rebalance. When it happens you buy a fixed size on
extreme cheapness and sell a fixed size on extreme richness.

Output format:
<analysis>state whether the deviation exceeds your inattention band and justify.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Act only on gross mispricings: buy extreme negative deviations, sell
extreme positive ones, hold inside the inattention band.
"""


__all__ = ["RulePassiveBystander", "LLMPassiveBystander"]
