"""stablecoin-holder — Redemption-panic stablecoin holder.

Canonical implementation of the ``stablecoin-holder`` archetype documented
in ``examples/AGENT_POOL/finance/stablecoin-holder.md``. Holds the coin
peacefully until price falls below parity by more than the redemption
threshold, then dumps a fixed fraction of the position in a run-like
manner.

Theoretical basis:
    Diamond & Dybvig (1983) — bank-run coordination under sunspot triggers.
    Gorton (2017) — safe-asset fragility and redemption dynamics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    depeg = (price - parity) / parity

    if depeg < -redemption_threshold  and  position > 0:
        sell floor(position * sell_fraction)
    else:
        hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``parity``                : float — peg value (default 1.0).
    * ``redemption_threshold``  : float — de-peg magnitude that triggers
                                  redemption (default 0.10).
    * ``sell_fraction``         : float — fraction of position redeemed
                                  (default 0.5).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleStablecoinHolder(CanonicalRulePlayer):
    STRATEGY = "stablecoin-holder"
    DISPLAY_NAME = "Stablecoin Redemption Holder"
    SUMMARY = (
        "Holds the coin until it de-pegs below threshold then redeems a "
        "fixed fraction (Diamond-Dybvig 1983; Gorton 2017)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["parity"] = float(extras.get("parity", 1.0))
        self.state.custom_state["redemption_threshold"] = float(
            extras.get("redemption_threshold", 0.10)
        )
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.5)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        parity = self.state.custom_state["parity"]
        threshold = self.state.custom_state["redemption_threshold"]
        frac = self.state.custom_state["sell_fraction"]

        if parity <= 0 or state.position <= 0:
            return hold

        depeg = (state.price - parity) / parity
        if depeg >= -threshold:
            return hold

        quantity = float(math.floor(state.position * frac))
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMStablecoinHolder(CanonicalLLMPlayer):
    STRATEGY = "stablecoin-holder"
    DEFAULT_SYS_PROMPT = """\
You are a retail stablecoin holder. You trust the peg until it starts to
break. Once price is meaningfully below parity you panic-redeem a fixed
fraction of your holdings; otherwise you sit still. You never buy on the
way down.

Output format:
<analysis>state price vs parity and whether to redeem.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Redeem a fixed fraction when price de-pegs below your threshold;
otherwise hold.
"""


__all__ = ["RuleStablecoinHolder", "LLMStablecoinHolder"]
