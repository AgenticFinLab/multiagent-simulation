"""media-influenced-trader — Social-amplified sentiment trader.

Canonical implementation of the ``media-influenced-trader`` archetype
documented in ``examples/AGENT_POOL/finance/media-influenced-trader.md``.
Weights the observed mispricing by a media sensitivity and social
amplification factor, then trades against a dead-band-corrected
"sentiment gap".

Theoretical basis:
    Tetlock (2007) — news-sentiment and stock returns.
    Da, Engelberg & Gao (2011) — investor attention (Google search).
    Baker & Wurgler (2006) — sentiment and the cross-section of returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    m = media_weight * deviation * social_amplification

    If ``|m| <= theta_m``: hold.
    Else:
        qty = min(max_order, |m| * quantity_scale)
        emit buy if m > 0 else sell.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``media_weight``          : float — sensitivity to media signal
                                   (default 0.80).
    * ``social_amplification``  : float — herding multiplier (default 1.50).
    * ``theta_m``               : float — dead-band on |m| (default 0.03).
    * ``quantity_scale``        : float — |m|→qty factor (default 5000.0).
    * ``max_order``             : float — per-round order cap (default 300.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMediaInfluencedTrader(CanonicalRulePlayer):
    STRATEGY = "media-influenced-trader"
    DISPLAY_NAME = "Media / Social-Amplified Trader"
    SUMMARY = (
        "Trades on a socially-amplified media sentiment gap "
        "(Tetlock 2007; Da-Engelberg-Gao 2011; Baker-Wurgler 2006)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["media_weight"] = float(
            extras.get("media_weight", 0.80)
        )
        self.state.custom_state["social_amplification"] = float(
            extras.get("social_amplification", 1.50)
        )
        self.state.custom_state["theta_m"] = float(
            extras.get("theta_m", 0.03)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 300.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        mw = self.state.custom_state["media_weight"]
        amp = self.state.custom_state["social_amplification"]
        theta = self.state.custom_state["theta_m"]
        scale = self.state.custom_state["quantity_scale"]
        max_order = self.state.custom_state["max_order"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if deviation != deviation or math.isnan(deviation):
            return hold

        m = mw * deviation * amp
        if abs(m) <= theta:
            return hold

        qty = float(min(max_order, abs(m) * scale))
        if qty <= 0:
            return hold
        factory = InvestorOrder.buy if m > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMediaInfluencedTrader(CanonicalLLMPlayer):
    STRATEGY = "media-influenced-trader"
    DEFAULT_SYS_PROMPT = """\
You are a trader whose beliefs are shaped by the prevailing media
narrative and the crowd's amplification of it. Your effective signal is
the price-vs-fundamental deviation scaled by how much you trust the media
narrative and how strong the social herding feels. When the amplified
signal is inside a small dead band you sit out; otherwise you lean in.

Output format:
<analysis>state the amplified sentiment signal and your resulting stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide via media-amplified sentiment: hold inside the dead band, else
lean in the direction of the amplified signal.
"""


__all__ = ["RuleMediaInfluencedTrader", "LLMMediaInfluencedTrader"]
