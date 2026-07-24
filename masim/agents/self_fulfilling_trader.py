"""self-fulfilling-trader — Soros-style reflexive self-fulfilling attacker.

Canonical implementation of the ``self-fulfilling-trader`` archetype
documented in ``examples/AGENT_POOL/finance/self-fulfilling-trader.md``.
Attacks a vulnerable target when the environment's vulnerability signal
exceeds a conviction threshold, and reinforces its conviction when price
moves align with its side; retreats otherwise.

Theoretical basis:
    Soros (1987) — The Alchemy of Finance (reflexivity).
    Merton (1948) — Self-fulfilling prophecy.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    conviction  ∈ [-1, +1]   (own state; updated round-to-round)
    vulnerability_index      (from state.raw)

    IF vulnerability_index > conviction_threshold:
        # Direction of attack: short by default (conviction < 0 means short).
        If conviction has never been set, initialise conviction = -1
        (attacker shorts the vulnerable target).
        q = min(resource_cap, aggression_multiplier * base_size * |conviction|)
        action = "sell" if conviction < 0 else "buy"

    Post-move update:
        aligned_price_change = -conviction * price_change
            (positive when price moves in the attacker's favour)
        IF aligned_price_change < -retreat_threshold:
            conviction *= decay_rate                    (adverse move → decay)
        ELSE:
            conviction = clamp(conviction + feedback_gain * aligned_price_change, -1, 1)

Scenario-specific fields (see ``REQUIRES_FEATURES``):
    * ``vulnerability_index`` : float in [0, 1] — target vulnerability.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``conviction_threshold``   : float (default 0.50).
    * ``aggression_multiplier``  : float (default 3.0).
    * ``base_size``              : float (default 500.0).
    * ``feedback_gain``          : float (default 1.0).
    * ``retreat_threshold``      : float (default 0.03).
    * ``decay_rate``             : float (default 0.50).
    * ``initial_conviction``     : float (default -1.0) — sign selects side.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSelfFulfillingTrader(CanonicalRulePlayer):
    STRATEGY = "self-fulfilling-trader"
    DISPLAY_NAME = "Reflexive Self-Fulfilling Attacker"
    SUMMARY = (
        "Soros-style reflexive attacker — sizes with conviction against "
        "vulnerable targets and updates conviction from realised price "
        "moves (Soros 1987; Merton 1948)."
    )
    REQUIRES_FEATURES: tuple = ("vulnerability_index",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["conviction_threshold"] = float(
            extras.get("conviction_threshold", 0.50)
        )
        self.state.custom_state["aggression_multiplier"] = float(
            extras.get("aggression_multiplier", 3.0)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 500.0)
        )
        self.state.custom_state["feedback_gain"] = float(
            extras.get("feedback_gain", 1.0)
        )
        self.state.custom_state["retreat_threshold"] = float(
            extras.get("retreat_threshold", 0.03)
        )
        self.state.custom_state["decay_rate"] = float(
            extras.get("decay_rate", 0.50)
        )
        initial = float(extras.get("initial_conviction", -1.0))
        if initial > 1.0:
            initial = 1.0
        elif initial < -1.0:
            initial = -1.0
        self.state.custom_state["conviction"] = initial

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        vulnerability = state.raw_require("vulnerability_index", cast=float)
        if math.isnan(vulnerability):
            return hold

        conviction = cs["conviction"]

        # Post-move conviction update — uses the tick-return already in state.
        aligned_price_change = -conviction * state.price_change
        if aligned_price_change < -cs["retreat_threshold"]:
            conviction *= cs["decay_rate"]
        else:
            conviction = conviction + cs["feedback_gain"] * aligned_price_change
        if conviction > 1.0:
            conviction = 1.0
        elif conviction < -1.0:
            conviction = -1.0
        cs["conviction"] = conviction

        if vulnerability <= cs["conviction_threshold"]:
            return hold
        if conviction == 0.0:
            return hold

        qty = cs["aggression_multiplier"] * cs["base_size"] * abs(conviction)
        if qty <= 0:
            return hold
        if conviction < 0:
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.buy(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSelfFulfillingTrader(CanonicalLLMPlayer):
    STRATEGY = "self-fulfilling-trader"
    DEFAULT_SYS_PROMPT = """\
You are a reflexive, Soros-style speculator attacking vulnerable targets.
When the target's fundamental vulnerability rises above your conviction
threshold you take an aggressive directional position (short when your
conviction is negative, long when positive). Every price move that
confirms your side reinforces your conviction and enlarges your next bet;
every adverse move erodes your conviction sharply and forces retreat.

Output format:
<analysis>state the vulnerability level, your conviction, and your posture.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Attack aggressively when the target is vulnerable and your conviction
strong; retreat quickly when the market moves against you.
"""


__all__ = ["RuleSelfFulfillingTrader", "LLMSelfFulfillingTrader"]
