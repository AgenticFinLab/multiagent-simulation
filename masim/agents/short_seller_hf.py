"""short-seller-hf — Short-selling hedge fund with forced covering.

Canonical implementation of the ``short-seller-hf`` archetype documented in
``examples/AGENT_POOL/finance/short-seller-hf.md``. Institutional short
seller that mechanically covers a fraction of its remaining short whenever
the price-to-fundamental deviation exceeds a loss threshold — amplifying
the squeeze through forced buying.

Theoretical basis:
    Jones & Lamont (2002) — Short-sale constraints and stock returns.
    Diamond & Verrecchia (1987) — Constraints on short-selling and asset
        price adjustment.
    Boehmer, Jones & Zhang (2008) — Which shorts are informed?
    Lamont (2012) — Go down fighting: short sellers vs. firms.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    IF price <= 0 OR fundamental <= 0 OR NaN: hold.
    ELIF position >= 0: hold (deactivated once fully covered).
    ELIF deviation <= cover_threshold: hold.
    ELSE:
        raw_cover = int(|position| * cover_fraction)
        qty       = min(|position|, raw_cover, int(cash / price))
        action    = "buy"

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``cover_threshold`` : float in [0.05, 0.50] (default 0.05,
                             Jones & Lamont 2002).
    * ``cover_fraction``  : float in [0.10, 1.00] (default 0.50,
                             Boehmer et al. 2008).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleShortSellerHf(CanonicalRulePlayer):
    STRATEGY = "short-seller-hf"
    DISPLAY_NAME = "Short-Selling Hedge Fund"
    SUMMARY = (
        "Institutional short with forced staged covering — amplifies "
        "squeezes when deviation breaches loss tolerance "
        "(Jones & Lamont 2002; Boehmer et al. 2008)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["cover_threshold"] = float(
            extras.get("cover_threshold", 0.05)
        )
        self.state.custom_state["cover_fraction"] = float(
            extras.get("cover_fraction", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        # Input guards.
        if state.price <= 0 or math.isnan(state.price):
            return hold
        if math.isnan(state.fundamental) or state.fundamental <= 0:
            return hold
        # Deactivation: fully covered.
        if state.position >= 0:
            return hold
        # Deviation guard — recompute to be explicit even though state.deviation
        # is available; profile Step 2 reads deviation from (price, fundamental).
        deviation = (state.price - state.fundamental) / state.fundamental
        if math.isnan(deviation):
            return hold
        if deviation <= cs["cover_threshold"]:
            return hold

        abs_position = abs(state.position)
        raw_cover = int(abs_position * cs["cover_fraction"])
        max_affordable = int(state.cash / state.price) if state.price > 0 else 0
        qty = min(int(abs_position), raw_cover, max(0, max_affordable))
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMShortSellerHf(CanonicalLLMPlayer):
    STRATEGY = "short-seller-hf"
    DEFAULT_SYS_PROMPT = """\
You are a short-selling hedge fund holding a large pre-existing short
position. Prime-brokerage constraints force you to buy back a fraction of
your short whenever the market's deviation above fundamental exceeds
your loss threshold. You never initiate new shorts (never sell) and you
never add to the short. Once fully covered you are permanently inactive.

Output format:
<analysis>state the deviation vs threshold and how much of the short you cover.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Cover a fraction of the remaining short only when deviation breaches
the loss threshold. Never sell.
"""


__all__ = ["RuleShortSellerHf", "LLMShortSellerHf"]
