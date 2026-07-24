"""streak-reversal-trader — Pro-cyclical gambler's-fallacy trader.

Canonical implementation of the ``streak-reversal-trader`` archetype
documented in ``examples/AGENT_POOL/finance/streak-reversal-trader.md``.
The profile's §Core Behavioral Mechanism is pro-cyclical: the agent
misperceives a persistent price-vs-fundamental deviation as a streak and
trades **with** that direction (see Tversky & Kahneman 1971; Rabin 2002).

Theoretical basis:
    Tversky & Kahneman (1971) — belief in the law of small numbers.
    Rabin (2002) — misperception of streaks and the gambler's fallacy.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    if |deviation| > activation_threshold:
        qty = min(max_order, int(|deviation| * quantity_scale))
        deviation > 0  -> buy  (chase overshoot)   [pro-cyclical]
        deviation < 0  -> sell (chase undershoot)
        then clamp by cash / position
    else:
        hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — activation |dev| (default 0.02).
    * ``quantity_scale``       : float — |dev|→quantity multiplier
                                 (default 5000.0).
    * ``max_order``            : float — order-size cap (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleStreakReversalTrader(CanonicalRulePlayer):
    STRATEGY = "streak-reversal-trader"
    DISPLAY_NAME = "Streak-Reversal Trader"
    SUMMARY = (
        "Misperceives persistent deviation as a streak and trades with "
        "the streak's direction (Tversky-Kahneman 1971; Rabin 2002)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 800.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        activation = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        cap = self.state.custom_state["max_order"]

        deviation = state.deviation
        if abs(deviation) <= activation:
            return hold

        raw_qty = min(cap, float(int(abs(deviation) * scale)))
        if raw_qty <= 0:
            return hold

        if deviation > 0:
            affordable = int(state.cash / state.price) if state.price > 0 else 0
            quantity = float(min(int(raw_qty), max(0, affordable)))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        else:
            quantity = float(min(int(raw_qty), max(0, int(state.position))))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )


class LLMStreakReversalTrader(CanonicalLLMPlayer):
    STRATEGY = "streak-reversal-trader"
    DEFAULT_SYS_PROMPT = """\
You are a gambler's-fallacy trader who confuses persistent price-vs-
fundamental deviations for a "streak" and — perversely — trades **with**
that streak: you buy the overshoot and sell the undershoot, sized by
how large the deviation currently is.

Output format:
<analysis>state the perceived streak direction and length.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade with the sign of the deviation whenever it exceeds your
activation threshold; otherwise hold.
"""


__all__ = ["RuleStreakReversalTrader", "LLMStreakReversalTrader"]
