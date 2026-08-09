"""depositor — Bank-run depositor with social influence.

Canonical implementation of the ``depositor`` archetype documented in
``masim/agents/defines/finance/depositor.md``. The depositor's effective
withdrawal threshold falls under stress (peer influence), triggering an
aggressive one-shot withdrawal (``sell``) up to a size cap.

Theoretical basis:
    Diamond & Dybvig (1983) — bank-run coordination-failure.
    Iyer & Puri (2012) — social-network amplification of runs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation           = (price - fundamental) / fundamental
    stress_proxy        = max(0, -deviation)
    effective_threshold = withdrawal_threshold *
                          (1 - social_influence * stress_proxy)

    If deviation < -effective_threshold and position > 0:
        q = min(max_withdraw, position)                → sell
    Else: hold. (Never buys.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``withdrawal_threshold`` : float — base deviation triggering
                                 withdrawal (default 0.10).
    * ``social_influence``     : float in [0, 1) — sensitivity to peer-
                                 withdrawal proxy (default 0.30).
    * ``max_withdraw``         : float — per-tick withdrawal cap
                                 (default 1000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDepositor(CanonicalRulePlayer):
    STRATEGY = "depositor"
    DISPLAY_NAME = "Bank-Run Depositor"
    SUMMARY = (
        "Threshold-triggered depositor with peer-driven threshold lowering "
        "(Diamond & Dybvig 1983; Iyer & Puri 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["withdrawal_threshold"] = float(
            extras.get("withdrawal_threshold", 0.10)
        )
        self.state.custom_state["social_influence"] = float(
            extras.get("social_influence", 0.30)
        )
        self.state.custom_state["max_withdraw"] = float(
            extras.get("max_withdraw", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.position <= 0:
            return hold

        cs = self.state.custom_state
        withdrawal_threshold = cs["withdrawal_threshold"]
        social_influence = cs["social_influence"]
        max_withdraw = cs["max_withdraw"]

        stress_proxy = max(0.0, -state.deviation)
        effective_threshold = withdrawal_threshold * (
            1.0 - social_influence * stress_proxy
        )

        if state.deviation < -effective_threshold:
            quantity = min(max_withdraw, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMDepositor(CanonicalLLMPlayer):
    STRATEGY = "depositor"
    DEFAULT_SYS_PROMPT = """\
You are a bank depositor with an uninsured claim. You are not a trader:
your only decision is whether to withdraw. As the market price falls
below the fundamental, you feel more pressure to run; peer-withdrawal
pressure amplifies your fear and lowers the threshold at which you act.
You never buy — only withdraw or hold.

Output format:
<analysis>state deviation and effective threshold.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Withdraw (sell) at the per-tick cap when the price fall exceeds your
peer-adjusted withdrawal threshold; otherwise hold.
"""


__all__ = ["RuleDepositor", "LLMDepositor"]
