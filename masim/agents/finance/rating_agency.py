"""rating-agency — Overconfident rating agency (perceived-fundamental bias).

Canonical implementation of the ``rating-agency`` archetype documented
in ``masim/agents/defines/finance/rating-agency.md``. The agent behaves
as if the true fundamental is inflated above the published fundamental
(overrating bias) and buys whenever the market price is meaningfully
below its inflated fair value. Buy-only.

Theoretical basis:
    Bolton, Freixas & Shapiro (2012) — the credit-ratings game and
    ratings inflation.
    Griffin & Tang (2012) — did subjective adjustments drive over-optimistic
    CDO ratings?

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    perceived_fundamental = fundamental * (1 + overrating_bias)
    threshold             = perceived_fundamental * 0.95

    If ``price < threshold`` AND cash > 0:
        buy = min(max_buy, int(cash / price))  at market price.
    Otherwise: hold.  (Never sells.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``overrating_bias`` : float — fractional inflation of perceived
                             fair value (default 0.20, Bolton et al. 2012).
    * ``max_buy``         : float — per-tick order cap (default 300).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRatingAgency(CanonicalRulePlayer):
    STRATEGY = "rating-agency"
    DISPLAY_NAME = "Rating Agency"
    SUMMARY = (
        "Overconfident rater who inflates perceived fair value and buys "
        "anything trading below it (Bolton et al. 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["overrating_bias"] = float(
            extras.get("overrating_bias", 0.20)
        )
        self.state.custom_state["max_buy"] = float(extras.get("max_buy", 300.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        bias = self.state.custom_state["overrating_bias"]
        max_buy = self.state.custom_state["max_buy"]

        perceived = state.fundamental * (1.0 + bias)
        threshold = perceived * 0.95

        if state.price < threshold and state.cash > 0:
            affordable = state.cash / state.price
            quantity = min(max_buy, float(int(affordable)))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRatingAgency(CanonicalLLMPlayer):
    STRATEGY = "rating-agency"
    DEFAULT_SYS_PROMPT = """\
You are a rating agency that systematically over-rates the asset — you
believe the intrinsic value is meaningfully above the published
fundamental. Whenever the market price sits below your inflated
perceived fair value with a comfortable safety margin, you buy. You
never sell; you only accumulate.

Output format:
<analysis>state perceived fair value, price gap, and stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), published-fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy when price is comfortably below your inflated perceived fair value;
otherwise hold. Never sell.
"""


__all__ = ["RuleRatingAgency", "LLMRatingAgency"]
