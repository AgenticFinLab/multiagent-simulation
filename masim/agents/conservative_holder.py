"""conservative-holder — Value-discount patient buyer (buy-only).

Canonical implementation of the ``conservative-holder`` archetype
documented in ``examples/AGENT_POOL/finance/conservative-holder.md``.
Buys a small base position when the discount to fundamental exceeds a
generous threshold and never sells — a patient value-holder.

Theoretical basis:
    Graham & Dodd (1934) — security analysis; margin of safety.
    Malkiel & Xu (2004) — market frictions and value-vs-growth returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    discount = (fundamental - price) / price
    IF discount > buy_threshold AND cash > 0:
        BUY min(base_position_size, cash / price)
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``buy_threshold``        : float > 0 — discount trigger
                                   (default 0.05).
    * ``base_position_size``   : float > 0 — nominal buy size
                                   (default 100.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleConservativeHolder(CanonicalRulePlayer):
    STRATEGY = "conservative-holder"
    DISPLAY_NAME = "Patient Value Holder"
    SUMMARY = (
        "Buys a small base position at generous discounts and never "
        "sells — Graham-Dodd margin of safety."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["buy_threshold"] = float(
            extras.get("buy_threshold", 0.05)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 100.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        threshold = self.state.custom_state["buy_threshold"]
        base = self.state.custom_state["base_position_size"]

        discount = (state.fundamental - state.price) / state.price
        if discount <= threshold:
            return hold
        if state.cash <= 0:
            return hold
        qty = min(base, state.cash / state.price)
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMConservativeHolder(CanonicalLLMPlayer):
    STRATEGY = "conservative-holder"
    DEFAULT_SYS_PROMPT = """\
You are a patient value-holder. You add a small position only when the
market trades at a comfortable discount to fundamental, and you never
sell. Your horizon is very long and your sizing is conservative.

Output format:
<analysis>state the current discount and whether it clears your margin of safety.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy a small base position when the discount to fundamental clears your
threshold; otherwise hold. Never sell.
"""


__all__ = ["RuleConservativeHolder", "LLMConservativeHolder"]
