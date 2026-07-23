"""gain-frame-follower — Kahneman-Tversky framing-driven trend follower.

Canonical implementation of the ``gain-frame-follower`` archetype documented
in ``examples/AGENT_POOL/finance/gain-frame-follower.md``. Reacts to how
the current mispricing is framed: buys in the gain frame, sells in the
loss frame, and stays out when deviation is sub-threshold.

Theoretical basis:
    Kahneman & Tversky (1979) — Prospect theory: an analysis of decision
    under risk.
    Tversky & Kahneman (1981) — The framing of decisions and the
    psychology of choice.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``|deviation| <= gain_threshold``: hold.
    Elif ``deviation > 0`` (gain frame): buy
        ``min(max_quantity, int(deviation * framing_scale), int(cash/price))``.
    Elif ``deviation < 0`` (loss frame): sell
        ``min(max_quantity, int(|deviation| * framing_scale), max(position,0))``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gain_threshold`` : float — activation gate (default 0.02).
    * ``framing_scale``  : float — deviation→qty factor (default 5000.0).
    * ``max_quantity``   : int — per-tick cap (default 800).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleGainFrameFollower(CanonicalRulePlayer):
    STRATEGY = "gain-frame-follower"
    DISPLAY_NAME = "Gain-Frame Follower"
    SUMMARY = (
        "Buys in the gain frame and sells in the loss frame "
        "(Kahneman & Tversky 1979; Tversky & Kahneman 1981)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["gain_threshold"] = float(extras.get("gain_threshold", 0.02))
        cs["framing_scale"] = float(extras.get("framing_scale", 5000.0))
        cs["max_quantity"] = int(extras.get("max_quantity", 800))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["gain_threshold"]
        scale = cs["framing_scale"]
        cap = cs["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or state.price <= 0:
            return hold
        abs_dev = abs(state.deviation)
        if abs_dev <= threshold:
            return hold
        raw_qty = int(abs_dev * scale)
        if raw_qty <= 0:
            return hold

        if state.deviation > 0:
            qty = min(cap, raw_qty, int(state.cash / state.price))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        qty = min(cap, raw_qty, int(max(state.position, 0)))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMGainFrameFollower(CanonicalLLMPlayer):
    STRATEGY = "gain-frame-follower"
    DEFAULT_SYS_PROMPT = """\
You are a framing-driven trader. When the market is framed as being in
gain territory (price above fundamental) you buy to chase the winner;
when framed as a loss (price below fundamental) you sell to cut the
loss. Framing effects only activate once the deviation is meaningful.

Output format:
<analysis>state whether the frame is a gain or a loss and your response.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Chase gains, cut losses, hold when deviation is small.
"""


__all__ = ["RuleGainFrameFollower", "LLMGainFrameFollower"]
