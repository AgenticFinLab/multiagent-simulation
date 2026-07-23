"""frame-invariant-trader — Rational contrarian on mispricing.

Canonical implementation of the ``frame-invariant-trader`` archetype
documented in ``examples/AGENT_POOL/finance/frame-invariant-trader.md``.
Frames deviation objectively — buys undervaluation and sells overvaluation
above a mispricing threshold; ignores gain/loss framing effects.

Theoretical basis:
    Shleifer & Vishny (1997) — The limits of arbitrage.
    Levin, Schneider & Gaeth (1998) — All frames are not created equal.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``|deviation| <= rational_threshold``: hold.
    Elif ``deviation < 0`` (undervalued): buy
        ``min(rational_cap, int(|deviation| * rational_scale), int(cash/price))``.
    Elif ``deviation > 0`` (overvalued): sell
        ``min(rational_cap, int(|deviation| * rational_scale), max(position, 0))``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rational_threshold`` : float — mispricing gate (default 0.05).
    * ``rational_scale``     : float — deviation→quantity factor (default 3000).
    * ``rational_cap``       : int — absolute order cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFrameInvariantTrader(CanonicalRulePlayer):
    STRATEGY = "frame-invariant-trader"
    DISPLAY_NAME = "Frame-Invariant Trader"
    SUMMARY = (
        "Rational contrarian who trades on objective mispricing regardless "
        "of framing (Shleifer & Vishny 1997; Levin et al. 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["rational_threshold"] = float(extras.get("rational_threshold", 0.05))
        cs["rational_scale"] = float(extras.get("rational_scale", 3000.0))
        cs["rational_cap"] = int(extras.get("rational_cap", 500))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["rational_threshold"]
        scale = cs["rational_scale"]
        cap = cs["rational_cap"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        abs_dev = abs(state.deviation)
        if abs_dev <= threshold or state.price <= 0:
            return hold
        raw_qty = int(abs_dev * scale)
        if raw_qty <= 0:
            return hold

        if state.deviation < 0:
            qty = min(cap, raw_qty, int(state.cash / state.price))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # deviation > 0
        qty = min(cap, raw_qty, int(max(state.position, 0)))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMFrameInvariantTrader(CanonicalLLMPlayer):
    STRATEGY = "frame-invariant-trader"
    DEFAULT_SYS_PROMPT = """\
You are a rational, frame-invariant trader. You evaluate mispricing
objectively: when price is meaningfully below fundamental you buy;
when meaningfully above you sell. You do not react to gain/loss framing
or narrative — only to the size of the deviation.

Output format:
<analysis>state the objective mispricing and your contrarian action.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy when undervalued, sell when overvalued, hold otherwise.
"""


__all__ = ["RuleFrameInvariantTrader", "LLMFrameInvariantTrader"]
