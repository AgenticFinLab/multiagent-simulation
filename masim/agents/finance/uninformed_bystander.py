"""uninformed-bystander — Passive stochastic background trader.

Canonical implementation of the ``uninformed-bystander`` archetype
documented in ``masim/agents/defines/finance/uninformed-bystander.md``.
The bystander is a rumor-audience archetype ported into the trading
setting: it mostly holds, occasionally participates through a two-gate
stochastic engagement rule, and when it does act, it trades weakly in
the direction of an internal belief that drifts toward an environmental
belief signal.

Theoretical basis:
    Shibutani (1966) — Passive audience theory (Improvised News).
    Latane & Darley (1970) — Bystander effect / diffusion of responsibility.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    env_belief = state.raw["env_belief"] if present, else a normalised
                 sentiment proxy derived from ``price_change`` and mapped
                 to [0, 1] (0.5 = neutral).

    Pre-decision belief update:
        my_belief <- clamp(my_belief + belief_drift_rate *
                           (env_belief - my_belief), 0, 1)

    Draw ``r1``, ``r2`` ~ Uniform(0, 1).
    If ``r1 < engagement_probability`` AND
       ``r2 < spread_probability``:
        intensity = clamp(my_belief * intensity_scaling, 0, 1)
        direction = buy if my_belief > 0.5 else sell (neutral: hold)
        quantity  = base_position_size * intensity
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``engagement_probability`` : float — chance of engaging (default 0.3).
    * ``spread_probability``     : float — chance of acting when engaged
                                    (default 0.5).
    * ``belief_drift_rate``      : float — belief drift rate (default 0.1).
    * ``intensity_scaling``      : float — intensity discount (default 0.5).
    * ``initial_belief``         : float — starting belief (default 0.1).
    * ``base_position_size``     : float — order-size cap when acting
                                    (default 10.0).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleUninformedBystander(CanonicalRulePlayer):
    STRATEGY = "uninformed-bystander"
    DISPLAY_NAME = "Uninformed Passive Bystander"
    SUMMARY = (
        "Passive stochastic background trader with weak belief drift and "
        "two-gate engagement (Shibutani 1966; Latane & Darley 1970)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["engagement_probability"] = float(
            extras.get("engagement_probability", 0.3)
        )
        self.state.custom_state["spread_probability"] = float(
            extras.get("spread_probability", 0.5)
        )
        self.state.custom_state["belief_drift_rate"] = float(
            extras.get("belief_drift_rate", 0.1)
        )
        self.state.custom_state["intensity_scaling"] = float(
            extras.get("intensity_scaling", 0.5)
        )
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.1)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 10.0)
        )

    def _env_belief(self, state: StandardMarketState) -> float:
        # Prefer an explicit env_belief broadcast when present. Otherwise
        # derive a bounded sentiment proxy from price_change (a rise
        # implies bullish ambient belief, a decline bearish); if that is
        # also unavailable, return the neutral 0.5. Kept in [0, 1].
        #
        # ``env_belief`` is intentionally *not* in REQUIRES_FEATURES: the
        # profile documents it as a soft-optional signal that the
        # bystander only *prefers* when available (a rumor-market
        # coordinator supplies it; a stock-only scenario will not). The
        # sentinel default of NaN routes through the price_change fallback
        # branch. Using raw_optional() (rather than bare .get) makes the
        # optional intent explicit at code-review time.
        raw = state.raw_optional("env_belief", default=None, cast=float)
        if raw is not None:
            belief = raw
        else:
            change = state.price_change
            # Squash: ±10% price change maps to ±0.5 around 0.5.
            belief = 0.5 + 5.0 * change
        if belief < 0.0:
            belief = 0.0
        elif belief > 1.0:
            belief = 1.0
        return belief

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        drift = self.state.custom_state["belief_drift_rate"]
        env_belief = self._env_belief(state)
        my_belief = self.state.custom_state["my_belief"]
        my_belief = my_belief + drift * (env_belief - my_belief)
        if my_belief < 0.0:
            my_belief = 0.0
        elif my_belief > 1.0:
            my_belief = 1.0
        self.state.custom_state["my_belief"] = my_belief

        engage_p = self.state.custom_state["engagement_probability"]
        spread_p = self.state.custom_state["spread_probability"]
        r1 = random.random()
        r2 = random.random()
        engaged = r1 < engage_p
        if not engaged or r2 >= spread_p:
            return hold

        scaling = self.state.custom_state["intensity_scaling"]
        intensity = my_belief * scaling
        if intensity < 0.0:
            intensity = 0.0
        elif intensity > 1.0:
            intensity = 1.0

        base = self.state.custom_state["base_position_size"]
        quantity = base * intensity
        if quantity <= 0:
            return hold

        # Direction from the internal belief: above-neutral belief leans
        # bullish, below-neutral bearish, exactly-neutral holds.
        if my_belief > 0.5:
            factory = InvestorOrder.buy
        elif my_belief < 0.5:
            factory = InvestorOrder.sell
        else:
            return hold
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMUninformedBystander(CanonicalLLMPlayer):
    STRATEGY = "uninformed-bystander"
    DEFAULT_SYS_PROMPT = """\
You are an uninformed passive bystander. You do not follow markets
closely and you rarely trade; most rounds you simply hold. Occasionally,
almost by accident, you engage and place a small, weak-conviction
order that follows whatever ambient sentiment you have picked up. You
never fact-check and you never take large positions.

Output format:
<analysis>brief reasoning (1-2 sentences) on engagement and mood.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Mostly hold. Only occasionally, place a small trade in the direction of
whatever weak ambient sentiment you feel.
"""


__all__ = ["RuleUninformedBystander", "LLMUninformedBystander"]
