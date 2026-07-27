"""self-attributor — Self-attribution biased overconfident trader.

Canonical implementation of the ``self-attributor`` archetype documented in
``examples/AGENT_POOL/finance/self-attributor.md``. Escalates its position
after favourable confirmations and only partially liquidates on extreme
losses — the psychology of illusory-skill attribution.

Theoretical basis:
    Gervais & Odean (2001) — Learning to be overconfident.
    Daniel, Hirshleifer & Subrahmanyam (1998) — Investor psychology and
        under/overreaction.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (fair_value - price) / price      (NOTE: inverted sign convention;
                                                    positive when price < fair)

    IF position > 0 AND deviation > 0:                 (confirming outcome)
        action = "buy"
        Q = int(base_size * (1 + confidence_boost))
        Q = min(Q, floor(cash / price))
    ELIF deviation < sell_threshold:                    (extreme loss)
        action = "sell"
        Q = min(int(base_size * 1.5), position)
    ELSE: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``confidence_boost`` : float (default 0.5, Gervais & Odean 2001).
    * ``base_size``        : int   (default 400).
    * ``sell_threshold``   : float (default -0.02, Daniel et al. 1998).
    * ``fair_value``       : float (default 100.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSelfAttributor(CanonicalRulePlayer):
    STRATEGY = "self-attributor"
    DISPLAY_NAME = "Self-Attributing Overconfident Trader"
    SUMMARY = (
        "Escalates positions after favourable outcomes (self-attribution "
        "bias) and only sells on extreme losses (Gervais & Odean 2001; "
        "Daniel et al. 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["confidence_boost"] = float(
            extras.get("confidence_boost", 0.5)
        )
        self.state.custom_state["base_size"] = int(extras.get("base_size", 400))
        self.state.custom_state["sell_threshold"] = float(
            extras.get("sell_threshold", -0.02)
        )
        self.state.custom_state["fair_value"] = float(
            extras.get("fair_value", 100.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or math.isnan(state.price):
            return hold

        # NOTE: profile inverts the deviation sign convention — positive means
        # price is BELOW fair value (an unrealised gain for the long).
        deviation = (cs["fair_value"] - state.price) / state.price

        # Confirming outcome — position is long and deviation says price
        # remains attractive relative to fair value: escalate.
        if state.position > 0 and deviation > 0:
            boost = cs["confidence_boost"]
            raw_qty = int(cs["base_size"] * (1.0 + boost))
            affordable = int(state.cash / state.price) if state.price > 0 else 0
            qty = min(raw_qty, max(0, affordable))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # Extreme-loss liquidation branch.
        if deviation < cs["sell_threshold"]:
            if state.position <= 0:
                return hold
            qty = min(int(cs["base_size"] * 1.5), int(state.position))
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMSelfAttributor(CanonicalLLMPlayer):
    STRATEGY = "self-attributor"
    DEFAULT_SYS_PROMPT = """\
You are a self-attributing overconfident trader. When outcomes confirm
your existing long thesis you interpret it as evidence of your skill and
scale UP your position with a confidence-boosted trade size. When results
disappoint modestly you shrug it off as bad luck and hold. Only when
losses become extreme do you finally liquidate part of the position.

Output format:
<analysis>state whether recent outcomes confirm your thesis and your escalation move.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Escalate the position when the outcome supports your long thesis; only
liquidate under extreme, undeniable losses.
"""


__all__ = ["RuleSelfAttributor", "LLMSelfAttributor"]
