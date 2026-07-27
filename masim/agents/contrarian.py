"""contrarian — Simple deviation-contrarian trader.

Canonical implementation of the ``contrarian`` archetype documented in
``examples/AGENT_POOL/finance/contrarian.md``. Trades opposite the
deviation once it exceeds a scaled threshold — a small, deterministic
mean-reverter.

Theoretical basis:
    De Bondt & Thaler (1985) — long-term overreaction and mean
    reversion.
    Lakonishok, Shleifer & Vishny (1994) — contrarian investment,
    extrapolation and risk.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    threshold = contrarian_threshold * 0.05
    IF |deviation| > threshold:
        qty = min(max_order, int(|deviation| * sizing_scale))
        direction = -sign(deviation)
        (deviation > 0 → SELL, deviation < 0 → BUY)
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``contrarian_threshold`` : float > 0 — threshold-scale multiplier
                                   (default 0.4).
    * ``max_order``            : int > 0 — per-round order cap
                                   (default 400).
    * ``threshold_base``       : float > 0 — base threshold before scaling
                                   (default 0.05).
    * ``sizing_scale``         : float > 0 — |deviation| → qty multiplier
                                   (default 2000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContrarian(CanonicalRulePlayer):
    STRATEGY = "contrarian"
    DISPLAY_NAME = "Deviation Contrarian"
    SUMMARY = (
        "Trades opposite to deviation once it exceeds threshold — "
        "long-horizon mean reversion (De Bondt & Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["contrarian_threshold"] = float(
            extras.get("contrarian_threshold", 0.4)
        )
        self.state.custom_state["max_order"] = int(extras.get("max_order", 400))
        self.state.custom_state["threshold_base"] = float(
            extras.get("threshold_base", 0.05)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 2000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        c_th = self.state.custom_state["contrarian_threshold"]
        base = self.state.custom_state["threshold_base"]
        cap = self.state.custom_state["max_order"]
        sizing = self.state.custom_state["sizing_scale"]

        threshold = c_th * base
        dev = state.deviation
        if abs(dev) <= threshold:
            return hold

        qty = min(cap, int(abs(dev) * sizing))
        if qty <= 0:
            return hold
        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMContrarian(CanonicalLLMPlayer):
    STRATEGY = "contrarian"
    DEFAULT_SYS_PROMPT = """\
You are a contrarian. When the market has moved sufficiently away from
fundamental you trade against the deviation — selling into premium,
buying into discount. Your positions are modest and disciplined
(De Bondt & Thaler 1985).

Output format:
<analysis>state the deviation and your contrarian direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade opposite to the sign of deviation when |deviation| exceeds your
threshold; otherwise hold.
"""


__all__ = ["RuleContrarian", "LLMContrarian"]
