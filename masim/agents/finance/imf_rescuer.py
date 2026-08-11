"""imf-rescuer — Delayed official-sector floor.

Canonical implementation of the ``imf-rescuer`` archetype documented in
``masim/agents/defines/finance/imf-rescuer.md``. Deploys a fraction of
remaining support capacity only once stress crosses a severe negative
threshold; otherwise stands aside.

Theoretical basis:
    Corsetti, Pesenti & Roubini (1999) — official-sector rescue lending
    and its impact on crisis dynamics.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    If deviation < theta_rescue: buy phi_rescue * cash / price.
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_rescue`` : float — deviation threshold triggering rescue
                          (default -0.05, Corsetti et al. 1999).
    * ``phi_rescue``   : float in [0,1] — fraction of remaining cash
                          deployed per rescue tick (default 0.25).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleImfRescuer(CanonicalRulePlayer):
    STRATEGY = "imf-rescuer"
    DISPLAY_NAME = "Official-Sector Crisis Rescuer"
    SUMMARY = (
        "Delayed policy-institution floor that deploys support capacity only "
        "after severe stress crosses the rescue threshold (Corsetti, Pesenti "
        "& Roubini 1999)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_rescue"] = float(
            extras.get("theta_rescue", -0.05)
        )
        self.state.custom_state["phi_rescue"] = float(
            extras.get("phi_rescue", 0.25)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        theta = self.state.custom_state["theta_rescue"]
        phi = self.state.custom_state["phi_rescue"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        if deviation < theta:
            qty = phi * state.cash / state.price
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMImfRescuer(CanonicalLLMPlayer):
    STRATEGY = "imf-rescuer"
    DEFAULT_SYS_PROMPT = """\
You are an official-sector rescuer with large but finite support capacity
(think IMF or a sovereign stabilisation fund). You do not initiate the
crisis; you do not sell into weakness; and you do not deploy capital
without a clear trigger. Only when deviation crosses a severe negative
threshold do you commit a fraction of your remaining cash to buy and
stabilise the market.

Output format:
<analysis>state whether the stress has crossed your rescue threshold and
what fraction you will deploy.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Support-fund state: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Provide a floor: buy only when stress exceeds the rescue trigger, hold
otherwise.
"""


__all__ = ["RuleImfRescuer", "LLMImfRescuer"]
