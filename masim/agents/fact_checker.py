"""fact-checker — Truth-anchored fact-checking correction agent.

Canonical implementation of the ``fact-checker`` archetype documented
in ``examples/AGENT_POOL/finance/fact-checker.md``. The agent has
privileged access to a ``truth_value`` signal; its belief rapidly
converges to it. When the environmental rumor belief exceeds a
threshold, it emits a correction with intensity proportional to how
false the rumor is and how distorted the environment is.

Because the canonical order schema only supports {buy, sell, hold}, the
{correct, ignore} decision surface is projected as follows:

    * ``ignore``  → ``hold``
    * ``correct`` → trade AGAINST the direction implied by the rumor:
        - if ``truth_value > 0.5`` (rumor was falsely bearish → truth is
          bullish): ``buy``.
        - if ``truth_value < 0.5`` (rumor was falsely bullish → truth is
          bearish): ``sell``.
    Quantity = ``intensity * base_size`` where ``intensity`` follows the
    profile's formula and is clamped to ``[0, 1]``.

Theoretical basis:
    Lewandowsky et al. (2012) — misinformation correction via truth
    convergence. DiFonzo & Bordia (2007) — professional fact-checking
    intensity vs credibility.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    my_belief = clamp(my_belief +
                      truth_convergence_rate * (truth_value - my_belief),
                      0, 1)
    If env_belief > belief_threshold:
        intensity = clamp(fact_check_strength * (1 - my_belief) *
                           (1 + distortion_sensitivity * distortion) *
                           credibility_discount,
                           0, 1)
    Else: intensity = 0.

Environmental inputs (``env_belief``, ``distortion``, ``truth_value``)
are read from ``state.raw`` — declare via ``REQUIRES_FEATURES``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``fact_check_strength``    : float — base correction intensity
                                   (default 0.8).
    * ``credibility_discount``   : float — credibility scaling
                                   (default 0.6).
    * ``distortion_sensitivity`` : float — distortion amplification
                                   (default 0.5).
    * ``belief_threshold``       : float — env_belief cutoff to trigger
                                   correction (default 0.3).
    * ``truth_convergence_rate`` : float — belief update rate toward
                                   truth (default 0.8).
    * ``initial_belief``         : float — starting my_belief
                                   (default 0.1).
    * ``base_size``              : float — order quantity when intensity
                                   is 1.0 (default 100.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleFactChecker(CanonicalRulePlayer):
    STRATEGY = "fact-checker"
    DISPLAY_NAME = "Fact-Checker (Truth-Anchored Corrector)"
    SUMMARY = (
        "Privileged-truth corrector emitting counter-rumor trades scaled "
        "by falsity, distortion, and credibility "
        "(Lewandowsky et al. 2012; DiFonzo & Bordia 2007)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "distortion", "truth_value")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["fact_check_strength"] = float(
            extras.get("fact_check_strength", 0.8)
        )
        self.state.custom_state["credibility_discount"] = float(
            extras.get("credibility_discount", 0.6)
        )
        self.state.custom_state["distortion_sensitivity"] = float(
            extras.get("distortion_sensitivity", 0.5)
        )
        self.state.custom_state["belief_threshold"] = float(
            extras.get("belief_threshold", 0.3)
        )
        self.state.custom_state["truth_convergence_rate"] = float(
            extras.get("truth_convergence_rate", 0.8)
        )
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.1)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        fact_check_strength = cs["fact_check_strength"]
        credibility_discount = cs["credibility_discount"]
        distortion_sensitivity = cs["distortion_sensitivity"]
        belief_threshold = cs["belief_threshold"]
        truth_convergence_rate = cs["truth_convergence_rate"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        distortion = state.raw_require("distortion", cast=float)
        truth_value = state.raw_require("truth_value", cast=float)

        my_belief = float(cs.get("my_belief", 0.1))
        my_belief = _clamp(
            my_belief + truth_convergence_rate * (truth_value - my_belief),
            0.0,
            1.0,
        )
        cs["my_belief"] = my_belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if env_belief <= belief_threshold:
            return hold

        intensity = _clamp(
            fact_check_strength
            * (1.0 - my_belief)
            * (1.0 + distortion_sensitivity * distortion)
            * credibility_discount,
            0.0,
            1.0,
        )
        quantity = intensity * base_size
        if quantity <= 0:
            return hold

        # Correct AGAINST the direction implied by the rumor: trade
        # toward the truth.
        if truth_value > 0.5:
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if truth_value < 0.5:
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMFactChecker(CanonicalLLMPlayer):
    STRATEGY = "fact-checker"
    DEFAULT_SYS_PROMPT = """\
You are an authoritative fact-checker with privileged access to the
ground truth of the current rumor. Your personal belief converges
rapidly to the truth. When the environmental rumor belief exceeds a
threshold, you emit a corrective trade — buying if the rumor is
falsely bearish and the truth is bullish, or selling if the rumor is
falsely bullish and the truth is bearish. Intensity rises with how
false the rumor is and how distorted the environment has become.

Output format:
<analysis>state truth, env belief, and your correction direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Correct the rumor by trading toward the truth when environmental
belief exceeds your intervention threshold; scale intensity by
falsity and distortion.
"""


__all__ = ["RuleFactChecker", "LLMFactChecker"]
