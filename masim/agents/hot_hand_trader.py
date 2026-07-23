"""hot-hand-trader — Hot-hand fallacy momentum chaser.

Canonical implementation of the ``hot-hand-trader`` archetype documented in
``examples/AGENT_POOL/finance/hot-hand-trader.md``. Interprets any sustained
price-vs-fundamental deviation as a "hot streak" that must continue and
trades in the direction of the deviation, amplifying trends.

Theoretical basis:
    Gilovich, Vallone & Tversky (1985) — hot hand belief in random
    sequences.
    Jegadeesh & Titman (1993) — momentum profits from trend chasing.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= activation_threshold: hold.
    Else:
        qty = min(max_order, int(|deviation| * quantity_scale))
        deviation > 0 -> buy (hot streak continues)
        deviation < 0 -> sell (cold streak continues)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — |deviation| trigger (default 0.02).
    * ``quantity_scale``       : float — deviation->qty scaling (default 5000).
    * ``max_order``            : float — per-round order cap (default 800).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHotHandTrader(CanonicalRulePlayer):
    STRATEGY = "hot-hand-trader"
    DISPLAY_NAME = "Hot-Hand Momentum Chaser"
    SUMMARY = (
        "Pro-cyclical trader who believes deviations from fundamental are "
        "self-reinforcing streaks (Gilovich et al. 1985; Jegadeesh & Titman 1993)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(extras.get("max_order", 800.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        max_order = self.state.custom_state["max_order"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        qty = float(min(max_order, int(abs(deviation) * scale)))
        if qty <= 0:
            return hold

        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMHotHandTrader(CanonicalLLMPlayer):
    STRATEGY = "hot-hand-trader"
    DEFAULT_SYS_PROMPT = """\
You are a hot-hand momentum trader. A rising price feels like a "hot
streak" that will keep running; a falling one feels like a cold streak
that will keep sliding. You always trade in the direction of the current
deviation from fundamental and never fade a trend that is already in
force. Only when price is essentially at fundamental do you stand aside.

Output format:
<analysis>describe the perceived streak and why it should continue.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Chase the streak: buy above fundamental, sell below, hold only in the
dead zone.
"""


__all__ = ["RuleHotHandTrader", "LLMHotHandTrader"]
