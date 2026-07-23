"""social-proof-follower — Herding trader who follows the crowd's direction.

Canonical implementation of the ``social-proof-follower`` archetype
documented in ``examples/AGENT_POOL/finance/social-proof-follower.md``.
Uses the sign of price-fundamental deviation as a proxy for the crowd's
direction and trades with it, amplifying whichever side is winning.

Theoretical basis:
    Bikhchandani, Hirshleifer & Welch (1992) — informational cascades.
    Cialdini (2001) — social proof principle in decision making.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    if |deviation| > threshold:
        deviation > 0  -> buy  (join the up-crowd)
        deviation < 0  -> sell (join the down-crowd)
    quantity = min(max_order, |deviation| * scale)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``threshold`` : float — activation deviation (default 0.02).
    * ``scale``     : float — |dev|→quantity multiplier (default 5000.0).
    * ``max_order`` : float — order-size cap (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSocialProofFollower(CanonicalRulePlayer):
    STRATEGY = "social-proof-follower"
    DISPLAY_NAME = "Social-Proof Follower"
    SUMMARY = (
        "Herds with the crowd's directional bias implied by the sign of "
        "price-vs-fundamental deviation (Bikhchandani et al. 1992; "
        "Cialdini 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["scale"] = float(extras.get("scale", 5000.0))
        self.state.custom_state["max_order"] = float(extras.get("max_order", 800.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["threshold"]
        scale = self.state.custom_state["scale"]
        cap = self.state.custom_state["max_order"]

        deviation = state.deviation
        if abs(deviation) <= threshold:
            return hold

        quantity = min(cap, abs(deviation) * scale)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSocialProofFollower(CanonicalLLMPlayer):
    STRATEGY = "social-proof-follower"
    DEFAULT_SYS_PROMPT = """\
You are a social-proof-driven trader. You read the crowd's mood off the
price-vs-fundamental gap: a sustained overshoot means the crowd is
buying — you buy; a sustained undershoot means the crowd is selling —
you sell. You never fight the herd.

Output format:
<analysis>state which side the crowd is on and your follow-the-crowd size.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy with the crowd on positive deviations, sell with the crowd on
negative deviations, hold when the market is flat.
"""


__all__ = ["RuleSocialProofFollower", "LLMSocialProofFollower"]
