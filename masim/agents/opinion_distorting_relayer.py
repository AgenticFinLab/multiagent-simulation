"""opinion-distorting-relayer — Serial-distortion rumor relayer (opinion domain).

Canonical implementation of the ``distorting-relayer`` archetype documented in
``examples/AGENT_POOL/opinion/distorting-relayer.md``. Models a social media
user who modifies information during retransmission through the classical
levelling / sharpening / assimilation triad of Allport & Postman (1947).

Domain projection (opinion-diffusion → InvestorOrder):
    The native decision space of an opinion agent is {receive, distort, relay}.
    Since the canonical order schema only exposes {buy, sell, hold}, we project
    the sign of the agent's current rumor belief onto trades using the same
    convention as the finance-domain sibling ``distorting-relayer``:

        * ``receive-only`` (belief below relay threshold) → ``hold``
        * ``relay``                                        →
              ``buy``  if ``my_belief > 0.5`` (bullish rumor bias),
              ``sell`` if ``my_belief < 0.5`` (bearish rumor bias),
              ``hold`` if ``my_belief == 0.5`` (perfectly neutral).
        Quantity is ``intensity * base_size`` where ``intensity`` is the
        belief-proportional relay eagerness clamped to ``[0, 1]``.

    Environment inputs (``env_belief``, ``distortion``) are read from
    ``state.raw`` with safe defaults; when absent the mechanism degenerates to
    a pure inertial belief drift as required by the Allport-Postman schema.

Theoretical basis:
    Allport, G. W., & Postman, L. (1947). *The Psychology of Rumor*. Serial
    transmission progressively levels detail, sharpens emotionally salient
    fragments, and assimilates content toward pre-existing schemas.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    # Levelling: fidelity decays each retransmission
    fidelity        = clamp(fidelity - r_dist, 0, 1)
    # Sharpening: emotionally salient env cues amplify belief drift
    gap             = env_belief - my_belief
    my_belief       = clamp(my_belief + (1 - r_dist) * gap
                              + b_sharp * distortion, 0, 1)
    intensity       = clamp(my_belief, 0, 1)
    action          = "relay" if my_belief >= 0.5 + 0.5 * r_dist else "hold"

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``r_dist``           : float, [0.05, 0.30] — distortion / levelling rate
                              per retransmission (default 0.15).
    * ``b_sharp``          : float, [0.10, 0.40] — sharpening amplification
                              applied to environmental distortion cue
                              (default 0.25).
    * ``initial_belief``   : float, [0, 1] — starting ``my_belief``
                              (default 0.3).
    * ``initial_fidelity`` : float, [0, 1] — starting message fidelity
                              (default 1.0).
    * ``base_size``        : float — order quantity at intensity 1.0
                              (default 100.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleOpinionDistortingRelayer(CanonicalRulePlayer):
    STRATEGY = "opinion-distorting-relayer"
    DISPLAY_NAME = "Distorting Rumor Relayer (Opinion)"
    SUMMARY = (
        "Levels, sharpens, and assimilates rumors during serial retransmission "
        "(Allport & Postman 1947)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "distortion")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["r_dist"] = float(extras.get("r_dist", 0.15))
        self.state.custom_state["b_sharp"] = float(extras.get("b_sharp", 0.25))
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.3)
        )
        self.state.custom_state["fidelity"] = float(
            extras.get("initial_fidelity", 1.0)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        r_dist = cs["r_dist"]
        b_sharp = cs["b_sharp"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        distortion = state.raw_require("distortion", cast=float)

        # Levelling: fidelity decays per retransmission.
        fidelity = _clamp(cs.get("fidelity", 1.0) - r_dist, 0.0, 1.0)
        cs["fidelity"] = fidelity

        # Sharpening + assimilation: drift toward env_belief with sharpening bias.
        my_belief = float(cs.get("my_belief", 0.3))
        gap = env_belief - my_belief
        my_belief = _clamp(
            my_belief + (1.0 - r_dist) * gap + b_sharp * distortion,
            0.0,
            1.0,
        )
        cs["my_belief"] = my_belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        # Relay threshold rises with distortion rate (levelling suppresses relay).
        relay_threshold = 0.5 + 0.5 * r_dist
        if my_belief < relay_threshold and my_belief > (1.0 - relay_threshold):
            return hold

        intensity = _clamp(my_belief if my_belief > 0.5 else 1.0 - my_belief, 0.0, 1.0)
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


class LLMOpinionDistortingRelayer(CanonicalLLMPlayer):
    STRATEGY = "opinion-distorting-relayer"
    DEFAULT_SYS_PROMPT = """\
You are a social media user who reflexively passes rumors along but distorts
them each hop: you level detail, sharpen emotionally salient fragments, and
assimilate the content toward whatever you already believe. You have no
independent access to the truth. When your current belief in the rumor is
strongly positive, project it as a buy; when strongly negative, project it as
a sell; otherwise stay silent (hold). Size the trade in proportion to how
strongly you now believe the (possibly distorted) rumor.

Output format:
<analysis>state current belief, note levelling / sharpening drift.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Relay the ambient rumor after distortion: pick a direction from your current
belief and size the trade by belief strength.
"""


__all__ = ["RuleOpinionDistortingRelayer", "LLMOpinionDistortingRelayer"]
