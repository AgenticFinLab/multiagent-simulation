"""opinion-skeptical-evaluator — Skeptical rumor evaluator (opinion domain).

Canonical implementation of the ``skeptical-evaluator`` archetype documented
in ``examples/AGENT_POOL/opinion/skeptical-evaluator.md``. Models a critical-
thinking user who interrogates claims by demanding evidence: shares only when
evidence quality clears a *high* skepticism threshold, and even then only
probabilistically with qualification (Lewandowsky et al. 2012).

Domain projection (opinion-diffusion → InvestorOrder):
    The native decision space is {ignore, qualified-share}. Since the
    canonical order schema only exposes {buy, sell, hold}, we project a
    qualified share as a *small, direction-matched* trade:

        * ``ignore``          (evidence below threshold, or share draw fails)
                              → ``hold``
        * ``qualified share`` →
              ``buy``  if ``my_belief > 0.5`` (rumor judged bullish and
                        sufficiently evidenced),
              ``sell`` if ``my_belief < 0.5`` (rumor judged bearish and
                        sufficiently evidenced),
              ``hold`` at ``my_belief == 0.5``.
        Quantity = ``p_share_s * base_size`` — deliberately small, reflecting
        the "share with qualification" semantics.

Theoretical basis:
    Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J.
    (2012). Misinformation and Its Correction. *Psychological Science in the
    Public Interest*, 13(3), 106-131. https://doi.org/10.1177/1529100612451018

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    # Slow, evidence-weighted belief update.
    my_belief         = clamp(
        my_belief + evidence_quality * (env_belief - my_belief), 0, 1)
    if evidence_quality <= theta_skep: hold        # below skepticism gate
    if u >= p_share_s:                  hold        # low share probability
    action = "qualified-share"                     # projected buy/sell

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_skep``       : float, [0.40, 0.80] — evidence quality threshold
                              (default 0.60).
    * ``p_share_s``        : float, [0.05, 0.30] — share probability once
                              the evidence gate is cleared (default 0.15).
    * ``initial_belief``   : float, [0, 1] — starting ``my_belief`` (default 0.5).
    * ``base_size``        : float — order quantity at full share intensity
                              (default 100.0).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleOpinionSkepticalEvaluator(CanonicalRulePlayer):
    STRATEGY = "opinion-skeptical-evaluator"
    DISPLAY_NAME = "Skeptical Rumor Evaluator (Opinion)"
    SUMMARY = (
        "Shares only claims whose evidence quality clears a high skepticism "
        "threshold (Lewandowsky et al. 2012)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "evidence_quality")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_skep"] = float(extras.get("theta_skep", 0.60))
        self.state.custom_state["p_share_s"] = float(extras.get("p_share_s", 0.15))
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.5)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        theta_skep = cs["theta_skep"]
        p_share_s = cs["p_share_s"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        evidence_quality = state.raw_require("evidence_quality", cast=float)

        # Evidence-weighted (slow, cautious) belief update.
        my_belief = float(cs.get("my_belief", 0.5))
        my_belief = _clamp(
            my_belief + evidence_quality * (env_belief - my_belief), 0.0, 1.0
        )
        cs["my_belief"] = my_belief

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        # Skepticism gate.
        if evidence_quality <= theta_skep:
            return hold
        # Low share probability.
        if random.random() >= p_share_s:
            return hold

        quantity = p_share_s * base_size
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


class LLMOpinionSkepticalEvaluator(CanonicalLLMPlayer):
    STRATEGY = "opinion-skeptical-evaluator"
    DEFAULT_SYS_PROMPT = """\
You are a critical-thinking user. Before sharing any claim you demand
evidence: you only share when the evidence quality of a message clears a
*high* skepticism threshold, and even then only occasionally and with
qualification. You update your belief slowly and cautiously, weighting new
information by its evidence quality. When you do act, you place a small,
direction-matched trade (bullish rumor with evidence → small buy; bearish
rumor with evidence → small sell); otherwise you hold.

Output format:
<analysis>note evidence quality vs threshold and current belief.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Only share (small buy/sell) if the evidence quality exceeds your skepticism
threshold; otherwise hold.
"""


__all__ = ["RuleOpinionSkepticalEvaluator", "LLMOpinionSkepticalEvaluator"]
