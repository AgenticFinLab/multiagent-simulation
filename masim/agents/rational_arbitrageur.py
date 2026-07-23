"""rational-arbitrageur — Rational arbitrageur with short-selling capacity.

Canonical implementation of the ``rational-arbitrageur`` archetype
documented in ``examples/AGENT_POOL/finance/rational-arbitrageur.md``.
Unlike a naive mean-reverter, this agent can go net short when the
asset is meaningfully overvalued and cover shorts when the deviation
compresses back.

Theoretical basis:
    Shleifer & Vishny (1997) — limits to arbitrage: capital constraints
    on rational arbitrageurs.
    Miller (1977) — short-sale constraints and asset prices.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    dev = (price - fundamental) / fundamental

    If ``dev > theta_short``:
        sell = min(base_position_size, dev * sizing_scale)
        capped by ``max_short_position - |position|`` when position < 0.
    If ``dev < theta_cover`` AND position < 0:
        buy (cover) = min(|position|, base_position_size).
    Otherwise: hold.

Note on shorting: base ``_finalize_order`` clips sells to
``max(state.position, 0.0)``. This archetype documents its short intent
in the profile; in scenarios that permit shorting, the scenario-specific
finaliser will let it through. When run under the standard finaliser the
sell will simply be clipped to available position, which is a safe
degradation (agent still acts consistently in long-only scenarios).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_short``          : float — activation for short (default 0.05).
    * ``theta_cover``          : float — activation for cover (default 0.01).
    * ``sizing_scale``         : float — dev→qty conversion (default 3000).
    * ``base_position_size``   : float — per-tick order cap (default 200).
    * ``max_short_position``   : float — |short| position cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalArbitrageur(CanonicalRulePlayer):
    STRATEGY = "rational-arbitrageur"
    DISPLAY_NAME = "Rational Arbitrageur"
    SUMMARY = (
        "Rational trader who short-sells overvalued assets and covers as "
        "deviation compresses (Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_short"] = float(
            extras.get("theta_short", 0.05)
        )
        self.state.custom_state["theta_cover"] = float(
            extras.get("theta_cover", 0.01)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 3000.0)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 200.0)
        )
        self.state.custom_state["max_short_position"] = float(
            extras.get("max_short_position", 500.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        theta_s = self.state.custom_state["theta_short"]
        theta_c = self.state.custom_state["theta_cover"]
        scale = self.state.custom_state["sizing_scale"]
        base = self.state.custom_state["base_position_size"]
        max_short = self.state.custom_state["max_short_position"]
        dev = state.deviation

        if dev > theta_s:
            desired = min(base, dev * scale)
            # Cap on how much more short we can add.
            room = max_short - max(-state.position, 0.0)
            quantity = min(desired, max(room, 0.0)) if state.position < 0 else desired
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev < theta_c and state.position < 0:
            quantity = min(abs(state.position), base)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRationalArbitrageur(CanonicalLLMPlayer):
    STRATEGY = "rational-arbitrageur"
    DEFAULT_SYS_PROMPT = """\
You are a rational arbitrageur with short-selling capacity. When the
asset is meaningfully overpriced you SELL SHORT to press the trade
against fundamentals; when the mispricing compresses, you cover your
short. You are patient, size positions by mispricing magnitude, and
respect a hard cap on how short you will go.

Output format:
<analysis>state deviation, current short exposure, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Short overvalued assets; cover short when the deviation compresses.
"""


__all__ = ["RuleRationalArbitrageur", "LLMRationalArbitrageur"]
