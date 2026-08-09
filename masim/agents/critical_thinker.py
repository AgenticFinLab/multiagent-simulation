"""critical-thinker — Contrarian critical thinker resisting the crowd.

Canonical implementation of the ``critical-thinker`` archetype documented
in ``masim/agents/defines/finance/critical-thinker.md``. Trades against the
market consensus when the consensus diverges materially from the agent's
private fundamental estimate.

Theoretical basis:
    Surowiecki (2004) — wisdom-of-crowds failures under correlated errors;
    contrarian value discipline.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    divergence = consensus_signal - fundamental_value

    (Threshold is expressed as a fraction of fundamental_value, per the
    worked example: "8.0 > 5.0 (threshold met at 0.05 * 100)".)

    scaled_theta = divergence_threshold * fundamental_value

    If divergence >  scaled_theta:
        q = min(position, conviction_size * divergence / scaled_theta *
                 divergence_scale)                                → sell
    Elif divergence < -scaled_theta:
        q = min(cash / price,
                 conviction_size * |divergence| / scaled_theta *
                 divergence_scale)                                → buy
    Else: hold.

``consensus_signal`` is read from ``state.raw`` when available; otherwise
it falls back to the observed market ``price`` (the market consensus).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``divergence_threshold`` : float — minimum |divergence|/fundamental
                                 to trigger a trade (default 0.05).
    * ``conviction_size``      : float — base contrarian order size
                                 (default 500.0).
    * ``max_position``         : float — position cap (default 10000.0).
    * ``divergence_scale``     : float — multiplier for divergence sizing
                                 (default 1.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCriticalThinker(CanonicalRulePlayer):
    STRATEGY = "critical-thinker"
    DISPLAY_NAME = "Contrarian Critical Thinker"
    SUMMARY = (
        "Contrarian trader resisting consensus when it diverges from a "
        "private fundamental estimate (Surowiecki 2004)."
    )
    REQUIRES_FEATURES: tuple = ("consensus_signal",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["divergence_threshold"] = float(
            extras.get("divergence_threshold", 0.05)
        )
        self.state.custom_state["conviction_size"] = float(
            extras.get("conviction_size", 500.0)
        )
        self.state.custom_state["max_position"] = float(
            extras.get("max_position", 10000.0)
        )
        self.state.custom_state["divergence_scale"] = float(
            extras.get("divergence_scale", 1.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental <= 0 or state.price <= 0:
            return hold

        cs = self.state.custom_state
        theta = cs["divergence_threshold"]
        conviction = cs["conviction_size"]
        max_pos = cs["max_position"]
        div_scale = cs["divergence_scale"]

        consensus = state.raw_require("consensus_signal", cast=float)
        divergence = consensus - state.fundamental
        scaled_theta = theta * state.fundamental
        if scaled_theta <= 0:
            return hold

        if divergence > scaled_theta:
            raw_q = conviction * divergence / scaled_theta * div_scale
            quantity = min(state.position, raw_q)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if divergence < -scaled_theta:
            budget = state.cash / state.price
            capacity = max(0.0, max_pos - state.position)
            raw_q = conviction * abs(divergence) / scaled_theta * div_scale
            quantity = min(budget, capacity, raw_q)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCriticalThinker(CanonicalLLMPlayer):
    STRATEGY = "critical-thinker"
    DEFAULT_SYS_PROMPT = """\
You are a critical thinker who resists market consensus when it strays
too far from your own fundamental estimate. You are independent,
analytical, and comfortable taking positions opposite to the crowd —
buying when the crowd is bearish below fair value, selling when the
crowd is bullish above fair value. You size positions proportional to
the size of the divergence, not the strength of the noise around you.

Output format:
<analysis>compare consensus to fundamental and explain your contrarian call.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Take the contrarian side when consensus diverges from fundamental beyond
your threshold; scale conviction with the size of the divergence.
"""


__all__ = ["RuleCriticalThinker", "LLMCriticalThinker"]
