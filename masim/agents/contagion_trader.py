"""contagion-trader — Cross-signal contagion seller (sell-only).

Canonical implementation of the ``contagion-trader`` archetype
documented in ``masim/agents/defines/finance/contagion-trader.md``.
Combines a deviation signal and a return signal into a scalar
contagion index; sells a fixed fraction of position when the signal
plunges below threshold — regional risk-off herding.

Theoretical basis:
    Kaminsky & Reinhart (1999) — the twin crises: banking and
    balance-of-payments problems; common-lender contagion channels.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    r_t = (price - prev_price) / prev_price
    s_t = w_dev * deviation + w_ret * r_t
    IF s_t < theta_contagion:
        SELL min(position, phi_sell * position)
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``w_dev``           : float > 0 — deviation weight (default 0.60).
    * ``w_ret``           : float > 0 — return weight    (default 0.40).
    * ``theta_contagion`` : float < 0 — signal trigger   (default -0.025).
    * ``phi_sell``        : float in [0, 1] — fraction of position
                             liquidated (default 0.50).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContagionTrader(CanonicalRulePlayer):
    STRATEGY = "contagion-trader"
    DISPLAY_NAME = "Cross-Signal Contagion Seller"
    SUMMARY = (
        "Sells a fixed fraction of position when the combined "
        "deviation+return signal crosses the contagion threshold "
        "(Kaminsky & Reinhart 1999)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["w_dev"] = float(extras.get("w_dev", 0.60))
        self.state.custom_state["w_ret"] = float(extras.get("w_ret", 0.40))
        self.state.custom_state["theta_contagion"] = float(
            extras.get("theta_contagion", -0.025)
        )
        self.state.custom_state["phi_sell"] = float(extras.get("phi_sell", 0.50))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.prev_price <= 0:
            return hold

        w_dev = self.state.custom_state["w_dev"]
        w_ret = self.state.custom_state["w_ret"]
        theta = self.state.custom_state["theta_contagion"]
        phi = self.state.custom_state["phi_sell"]

        r_t = (state.price - state.prev_price) / state.prev_price
        s_t = w_dev * state.deviation + w_ret * r_t
        if s_t >= theta:
            return hold

        pos = max(state.position, 0.0)
        if pos <= 0:
            return hold
        qty = min(pos, phi * pos)
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMContagionTrader(CanonicalLLMPlayer):
    STRATEGY = "contagion-trader"
    DEFAULT_SYS_PROMPT = """\
You are a contagion-sensitive trader. You combine the deviation from
fundamental with the last-tick return into a single risk-off signal;
when the signal plunges below your threshold you dump a fixed fraction
of your position. You never add exposure
(Kaminsky & Reinhart 1999).

Output format:
<analysis>state the combined signal and whether it crosses your contagion threshold.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Compute the contagion signal from deviation and return; dump a fixed
fraction of position if it clears the threshold, otherwise hold.
"""


__all__ = ["RuleContagionTrader", "LLMContagionTrader"]
