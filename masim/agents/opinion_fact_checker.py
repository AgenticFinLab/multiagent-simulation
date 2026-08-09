"""opinion-fact-checker — Authoritative fact-checker (opinion domain).

Canonical implementation of the ``fact-checker`` archetype documented in
``masim/agents/defines/opinion/fact-checker.md``. Models a professional
fact-checking organisation that monitors ambient population belief in a
rumor and broadcasts a verified correction whenever belief deviates from the
truth beyond a threshold (Lewandowsky et al. 2012; Ecker et al. 2022).

Domain projection (opinion-diffusion → InvestorOrder):
    The native decision space of a fact-checker is {monitor, broadcast-correction}.
    Since the canonical order schema only exposes {buy, sell, hold}, we
    project a correction into a *counter-directional* trade against the
    prevailing rumor:

        * ``monitor`` (population belief within tolerance)     → ``hold``
        * ``broadcast correction against a bullish rumor``     → ``sell``
        * ``broadcast correction against a bearish rumor``     → ``buy``
        Quantity = ``correction_reach * base_size`` where
        ``correction_reach = r_corr * (1 - d_corr)`` follows the profile's
        `effective_correction = (1 - decay_factor)` formulation.

    Environment inputs (``env_belief``, ``truth``) are read from ``state.raw``
    with safe defaults (env_belief=0.5 neutral, truth=0.5 neutral); when both
    are neutral the correction magnitude collapses to zero and the agent
    holds.

Theoretical basis:
    Lewandowsky, S., Ecker, U. K. H., Seifert, C. M., Schwarz, N., & Cook, J.
    (2012). Misinformation and Its Correction. *Psychological Science in the
    Public Interest*, 13(3), 106-131. https://doi.org/10.1177/1529100612451018
    Ecker, U. K. H. et al. (2022). *Nature Reviews Psychology*, 1, 13-29.
    https://doi.org/10.1038/s44159-021-00006-y

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation           = env_belief - truth
    if |deviation| < correction_threshold: hold
    effective_correction = 1 - d_corr           # continued-influence residue
    correction_reach     = r_corr * effective_correction
    action               = "sell" if deviation > 0 else "buy"
    quantity             = correction_reach * base_size

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``r_corr``               : float, [0.10, 0.50] — broadcast reach /
                                  effort per round (default 0.25).
    * ``d_corr``                : float, [0.50, 0.90] — continued-influence
                                  decay factor of a correction (default 0.70).
    * ``correction_threshold``  : float — |env_belief - truth| gate that
                                  triggers a broadcast (default 0.1).
    * ``base_size``             : float — order quantity at reach 1.0
                                  (default 100.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleOpinionFactChecker(CanonicalRulePlayer):
    STRATEGY = "opinion-fact-checker"
    DISPLAY_NAME = "Authoritative Fact-Checker (Opinion)"
    SUMMARY = (
        "Broadcasts verified corrections that counteract rumor exposure "
        "(Lewandowsky et al. 2012; Ecker et al. 2022)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief", "truth")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["r_corr"] = float(extras.get("r_corr", 0.25))
        self.state.custom_state["d_corr"] = float(extras.get("d_corr", 0.70))
        self.state.custom_state["correction_threshold"] = float(
            extras.get("correction_threshold", 0.1)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 100.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        r_corr = cs["r_corr"]
        d_corr = cs["d_corr"]
        correction_threshold = cs["correction_threshold"]
        base_size = cs["base_size"]

        env_belief = state.raw_require("env_belief", cast=float)
        truth = state.raw_require("truth", cast=float)

        deviation = env_belief - truth

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if abs(deviation) < correction_threshold:
            return hold

        # Continued-influence residue: only (1 - d_corr) of a correction sticks.
        effective_correction = _clamp(1.0 - d_corr, 0.0, 1.0)
        correction_reach = _clamp(r_corr * effective_correction, 0.0, 1.0)
        # Scale by deviation magnitude so a small gap yields a small counter-order.
        quantity = correction_reach * base_size * _clamp(abs(deviation), 0.0, 1.0)
        if quantity <= 0:
            return hold

        # Counter-directional trade: correct a bullish rumor by selling.
        if deviation > 0:
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMOpinionFactChecker(CanonicalLLMPlayer):
    STRATEGY = "opinion-fact-checker"
    DEFAULT_SYS_PROMPT = """\
You are a professional fact-checking organisation. You monitor ambient
population belief in a rumor against the verified truth. When the population
belief deviates from truth beyond your correction threshold, you broadcast a
verified correction against the prevailing rumor. Because of the continued-
influence effect, corrections only partially undo prior exposure. In the
projected trading contract this means: if the crowd's rumor is bullish, you
sell to counteract it; if bearish, you buy to counteract it; otherwise hold.
Never amplify a rumor.

Output format:
<analysis>state population belief vs truth and correction reach.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If the ambient rumor deviates from truth beyond your threshold, broadcast a
counter-directional correction; otherwise hold.
"""


__all__ = ["RuleOpinionFactChecker", "LLMOpinionFactChecker"]
