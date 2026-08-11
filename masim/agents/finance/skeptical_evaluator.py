"""skeptical-evaluator — Truth-anchored corrective node for rumour scenarios.

Canonical implementation of the ``skeptical-evaluator`` archetype
documented in ``masim/agents/defines/finance/skeptical-evaluator.md``.
Reads the environmental rumour-belief signal and emits corrective
selling pressure proportional to the agent's confidence that the rumour
is false; otherwise ignores the environment.

Theoretical basis:
    Ecker et al. (2022) — truth-anchoring and epistemic vigilance.
    Lewandowsky et al. (2012) — debunking and correction of misinformation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    # Pre-decision belief update:
    my_belief <- clamp(my_belief +
                       skepticism * (truth_anchor - my_belief) +
                       (1 - skepticism) * 0.1 * (env_belief - my_belief),
                       0, 1)

    # Decision:
    if env_belief > belief_threshold:
        intensity = clamp((1 - my_belief) * correction_eagerness, 0, 1)
        action    = "correct"  → sell (corrective pressure against rumour)
    else:
        intensity = 0
        action    = "ignore"   → hold

    The trading framework only supports buy/sell/hold, so "correct" is
    mapped to a sell of ``intensity * correction_qty_scale`` units.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``skepticism``            : float — truth-anchor pull (default 0.7).
    * ``correction_eagerness``  : float — intensity multiplier
                                  (default 0.8).
    * ``belief_threshold``      : float — env_belief trigger
                                  (default 0.4).
    * ``truth_anchor``          : float — prior belief (default 0.1).
    * ``initial_belief``        : float — starting my_belief
                                  (default 0.1).
    * ``correction_qty_scale``  : float — intensity→quantity scale
                                  (default 100.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class RuleSkepticalEvaluator(CanonicalRulePlayer):
    STRATEGY = "skeptical-evaluator"
    DISPLAY_NAME = "Skeptical Rumour Evaluator"
    SUMMARY = (
        "Anchors belief to prior truth and emits corrective pressure "
        "when environmental rumour belief exceeds threshold "
        "(Ecker 2022; Lewandowsky 2012)."
    )
    # Reads env_belief (and optional distortion) from state.raw.
    REQUIRES_FEATURES: tuple = ("env_belief",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["skepticism"] = float(
            extras.get("skepticism", 0.7)
        )
        self.state.custom_state["correction_eagerness"] = float(
            extras.get("correction_eagerness", 0.8)
        )
        self.state.custom_state["belief_threshold"] = float(
            extras.get("belief_threshold", 0.4)
        )
        self.state.custom_state["truth_anchor"] = float(
            extras.get("truth_anchor", 0.1)
        )
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.1)
        )
        self.state.custom_state["correction_qty_scale"] = float(
            extras.get("correction_qty_scale", 100.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        env_belief = state.raw_require("env_belief", cast=float)

        skepticism = self.state.custom_state["skepticism"]
        eagerness = self.state.custom_state["correction_eagerness"]
        threshold = self.state.custom_state["belief_threshold"]
        anchor = self.state.custom_state["truth_anchor"]
        my_belief = self.state.custom_state["my_belief"]
        qty_scale = self.state.custom_state["correction_qty_scale"]

        # Pre-decision belief update (truth anchoring).
        new_belief = (
            my_belief
            + skepticism * (anchor - my_belief)
            + (1.0 - skepticism) * 0.1 * (env_belief - my_belief)
        )
        my_belief = _clamp(new_belief, 0.0, 1.0)
        self.state.custom_state["my_belief"] = my_belief

        # Action decision.
        if env_belief <= threshold:
            return hold

        intensity = _clamp((1.0 - my_belief) * eagerness, 0.0, 1.0)
        quantity = intensity * qty_scale
        if quantity <= 0:
            return hold

        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSkepticalEvaluator(CanonicalLLMPlayer):
    STRATEGY = "skeptical-evaluator"
    DEFAULT_SYS_PROMPT = """\
You are an analytical, high-CRT participant who serves as a corrective
node against rumours. You keep your own belief anchored close to the
prior truth and only push back — with intensity proportional to your
disagreement — when the environment's rumour belief is high enough.

Output format:
<analysis>state env_belief vs threshold and your corrective intensity.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
When the environment's rumour belief crosses your threshold, emit
corrective (sell) pressure proportional to your confidence the rumour
is false; otherwise hold.
"""


__all__ = ["RuleSkepticalEvaluator", "LLMSkepticalEvaluator"]
