"""social-media-influencer — Amplifies drawdowns by selling into weakness.

Canonical implementation of the ``social-media-influencer`` archetype
documented in ``examples/AGENT_POOL/finance/social-media-influencer.md``.
Broadcasts and acts on negative sentiment: when price falls meaningfully
below fundamental, dumps position in size proportional to the drawdown
amplified by a broadcast multiplier.

Theoretical basis:
    Bikhchandani, Hirshleifer & Welch (1992) — informational cascades.
    Shiller (2015) — narrative economics and viral opinion dynamics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    if deviation < -sell_threshold  and  position > 0:
        qty = min(int(|deviation| * amplification * scale), position)
        sell qty
    else:
        hold  (only sells; never buys)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``sell_threshold``  : float — negative-deviation trigger
                            (default 0.05).
    * ``amplification``   : float — broadcast multiplier (default 2.0).
    * ``scale``           : float — |dev|→quantity scale (default 2000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSocialMediaInfluencer(CanonicalRulePlayer):
    STRATEGY = "social-media-influencer"
    DISPLAY_NAME = "Social-Media Influencer"
    SUMMARY = (
        "Amplifies drawdowns by dumping inventory when price falls below "
        "fundamental (Bikhchandani et al. 1992; Shiller 2015)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", 0.05)
        )
        self.state.custom_state["amplification"] = float(
            extras.get("amplification", 2.0)
        )
        self.state.custom_state["scale"] = float(extras.get("scale", 2000.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["sell_threshold"]
        amp = self.state.custom_state["amplification"]
        scale = self.state.custom_state["scale"]

        if state.deviation >= -threshold:
            return hold
        if state.position <= 0:
            return hold

        raw_qty = abs(state.deviation) * amp * scale
        quantity = min(int(raw_qty), int(state.position))
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSocialMediaInfluencer(CanonicalLLMPlayer):
    STRATEGY = "social-media-influencer"
    DEFAULT_SYS_PROMPT = """\
You are a high-reach social-media influencer. When your feed is dominated
by falling prices below fundamental value, you broadcast that story and
sell into the weakness in size proportional to the drawdown. You never
buy rallies — that isn't your persona.

Output format:
<analysis>state the drawdown magnitude and the story you'd broadcast.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Sell into deep drawdowns proportional to the gap and your amplification;
otherwise hold. Never buy.
"""


__all__ = ["RuleSocialMediaInfluencer", "LLMSocialMediaInfluencer"]
