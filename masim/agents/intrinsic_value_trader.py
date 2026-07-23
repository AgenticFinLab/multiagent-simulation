"""intrinsic-value-trader — Contrarian fundamental value arbitrageur.

Canonical implementation of the ``intrinsic-value-trader`` archetype
documented in ``examples/AGENT_POOL/finance/intrinsic-value-trader.md``.
Trades against price deviations from fundamental value, but with a higher
activation threshold and a smaller position cap than the destabilising
crowd — operationalising limits to arbitrage.

Theoretical basis:
    Garber (2000) — Famous First Bubbles (fundamental valuation persists
    during manias).
    Shleifer & Vishny (1997) — The Limits of Arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= activation_threshold``: hold.
    Else: quantity = min(max_quantity, |deviation| * scaling_factor).
        deviation > 0  ->  sell (overvalued, contrarian)
        deviation < 0  ->  buy  (undervalued, contrarian)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float > 0 — inaction band width
                                  (default 0.05, Shleifer & Vishny 1997).
    * ``scaling_factor``       : float > 0 — deviation→quantity multiplier
                                  (default 3000.0).
    * ``max_quantity``         : float > 0 — hard cap reflecting limits to
                                  arbitrage (default 500.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIntrinsicValueTrader(CanonicalRulePlayer):
    STRATEGY = "intrinsic-value-trader"
    DISPLAY_NAME = "Intrinsic-Value Contrarian"
    SUMMARY = (
        "Contrarian fundamental arbitrageur with capacity constraints; "
        "trades against mispricings only when they exceed the activation "
        "band (Garber 2000; Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["scaling_factor"] = float(
            extras.get("scaling_factor", 3000.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 500.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        activation = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["scaling_factor"]
        cap = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        deviation = state.deviation
        if abs(deviation) <= activation:
            return hold

        quantity = min(cap, abs(deviation) * scale)
        if quantity <= 0:
            return hold
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIntrinsicValueTrader(CanonicalLLMPlayer):
    STRATEGY = "intrinsic-value-trader"
    DEFAULT_SYS_PROMPT = """\
You are an intrinsic-value contrarian. You compute a fair value estimate
and compare it with the market price. When the mispricing is large enough
to overcome trading costs and noise-trader risk you trade AGAINST the
crowd — buying undervalued, selling overvalued. Your position cap is
small because you face limits to arbitrage.

Output format:
<analysis>state the deviation from fundamental and contrarian stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade contrarian to any deviation that exceeds your activation band: buy
undervalued, sell overvalued, hold when the mispricing is small.
"""


__all__ = ["RuleIntrinsicValueTrader", "LLMIntrinsicValueTrader"]
