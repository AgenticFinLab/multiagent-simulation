"""distorting-relayer — Serial-distortion rumor relayer.

Canonical implementation of the ``distorting-relayer`` archetype
documented in ``examples/AGENT_POOL/finance/distorting-relayer.md``. The
agent updates a personal belief in a rumor via credulity + sharpening
(distortion) + leveling (regression to neutral), then relays with
intensity proportional to belief strength.

Because the canonical order schema only supports {buy, sell, hold}, the
{spread, ignore} decision surface is projected as follows:

    * ``ignore`` → ``hold``
    * ``spread`` → ``buy``  if ``my_belief > 0.5`` (bullish rumor bias),
                  ``sell`` if ``my_belief < 0.5`` (bearish rumor bias),
                  ``hold`` at ``my_belief == 0.5``.
    Quantity = ``intensity * base_size`` where ``intensity`` is the
    profile-defined relay intensity clamped to ``[0, 1]``.

Theoretical basis:
    Allport & Postman (1947); Bartlett (1932) — sharpening / leveling in
    serial reproduction. Buckner (1965) — rumor transmission thresholds.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gap        = env_belief - my_belief
    my_belief  = clamp(my_belief + credulity * gap +
                        sharpening_factor * distortion -
                        leveling_factor * (my_belief - 0.5)**2, 0, 1)
    intensity  = clamp(my_belief * relay_eagerness, 0, 1)
    action     = "spread" if my_belief > relay_threshold else "ignore"

Environmental inputs (``env_belief``, ``distortion``) are read from
``state.raw`` with safe defaults (0.0) — the mechanism degenerates to
a pure inertial belief update when absent.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``credulity``          : float — base env→me adoption rate
                               (default 0.6).
    * ``relay_eagerness``    : float — belief→intensity multiplier
                               (default 0.8).
    * ``sharpening_factor``  : float — distortion amplification rate
                               (default 0.4).
    * ``leveling_factor``    : float — regression-to-neutral rate
                               (default 0.1).
    * ``relay_threshold``    : float — minimum belief to relay
                               (default 0.25).
    * ``initial_belief``     : float — starting ``my_belief`` (default 0.3).
    * ``base_size``          : float — max order quantity when relaying
                               at intensity 1.0 (default 100.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleDistortingRelayer(CanonicalRulePlayer):
    STRATEGY = "distorting-relayer"
    DISPLAY_NAME = "Serial-Distortion Rumor Relayer"
    SUMMARY = (
        "Sharpens and levels rumor beliefs, then relays with belief-"
        "proportional intensity (Allport & Postman 1947; Bartlett 1932)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "distortion")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["credulity"] = float(extras.get("credulity", 0.6))
        self.state.custom_state["relay_eagerness"] = float(
            extras.get("relay_eagerness", 0.8)
        )
        self.state.custom_state["sharpening_factor"] = float(
            extras.get("sharpening_factor", 0.4)
        )
        self.state.custom_state["leveling_factor"] = float(
            extras.get("leveling_factor", 0.1)
        )
        self.state.custom_state["relay_threshold"] = float(
            extras.get("relay_threshold", 0.25)
        )
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.3)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        credulity = cs["credulity"]
        relay_eagerness = cs["relay_eagerness"]
        sharpening_factor = cs["sharpening_factor"]
        leveling_factor = cs["leveling_factor"]
        relay_threshold = cs["relay_threshold"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        distortion = state.raw_require("distortion", cast=float)

        my_belief = float(cs.get("my_belief", 0.3))
        gap = env_belief - my_belief
        my_belief = _clamp(
            my_belief
            + credulity * gap
            + sharpening_factor * distortion
            - leveling_factor * (my_belief - 0.5) ** 2,
            0.0,
            1.0,
        )
        cs["my_belief"] = my_belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if my_belief <= relay_threshold:
            return hold

        intensity = _clamp(my_belief * relay_eagerness, 0.0, 1.0)
        quantity = intensity * base_size
        if quantity <= 0:
            return hold

        if my_belief > 0.5:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if my_belief < 0.5:
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMDistortingRelayer(CanonicalLLMPlayer):
    STRATEGY = "distorting-relayer"
    DEFAULT_SYS_PROMPT = """\
You are a distorting rumor relayer. You have no independent access to
the truth. You adopt the environment's rumor belief with high credulity,
amplify it further when the environment is already distorted, and lose a
little detail each round (mild regression to a neutral 0.5). When your
belief exceeds a low relay threshold you act on it — buying if you now
believe the rumor is bullish, selling if bearish — with intensity
proportional to your belief strength.

Output format:
<analysis>state current belief and intended relay intensity.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Relay the ambient rumor: pick a direction based on your current belief
and size the trade with intensity proportional to belief strength.
"""


__all__ = ["RuleDistortingRelayer", "LLMDistortingRelayer"]
