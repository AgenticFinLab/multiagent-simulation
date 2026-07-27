"""rational-trader — Glosten-Milgrom / Shleifer rational informed trader.

Canonical implementation of the ``rational-trader`` archetype documented
in ``examples/AGENT_POOL/finance/rational-trader.md``. Trades contrarian
to observable deviation with quantity proportional to |deviation| and
risk aversion — the neoclassical benchmark agent.

Theoretical basis:
    Glosten & Milgrom (1985) — bid, ask and transaction prices with
    heterogeneously informed traders: rational informed trading drives
    price discovery.
    Shleifer (2000) — inefficient markets: CARA demand function linear
    in deviation, scaled by risk aversion.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| > activation_threshold``:
        raw_qty = floor(|dev| * risk_aversion * base_scale)
        qty     = min(raw_qty, max_order)
        direction = -sign(deviation)  (contrarian)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``risk_aversion``        : float — sizing coefficient (default 0.5).
    * ``activation_threshold`` : float — no-trade band (default 0.03).
    * ``max_order``            : float — per-tick order cap (default 500).
    * ``base_scale``           : float — deviation→qty scale (default 3000).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalTrader(CanonicalRulePlayer):
    STRATEGY = "rational-trader"
    DISPLAY_NAME = "Rational Trader"
    SUMMARY = (
        "Rational informed trader with linear demand in deviation "
        "(Glosten & Milgrom 1985; Shleifer 2000)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["risk_aversion"] = float(
            extras.get("risk_aversion", 0.5)
        )
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.03)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 500.0)
        )
        self.state.custom_state["base_scale"] = float(
            extras.get("base_scale", 3000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        theta = self.state.custom_state["activation_threshold"]
        gamma = self.state.custom_state["risk_aversion"]
        qmax = self.state.custom_state["max_order"]
        scale = self.state.custom_state["base_scale"]
        dev = state.deviation

        if abs(dev) <= theta:
            return hold

        raw_qty = math.floor(abs(dev) * gamma * scale)
        quantity = float(min(raw_qty, qmax))
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRationalTrader(CanonicalLLMPlayer):
    STRATEGY = "rational-trader"
    DEFAULT_SYS_PROMPT = """\
You are a fully rational informed trader (Glosten-Milgrom / Shleifer).
You know the fundamental value. When price sits above fundamental you
SELL; when it sits below you BUY. Your trade size is linear in the
mispricing magnitude, scaled by your risk aversion, and capped at a
per-tick maximum. You never chase momentum; you always trade the
contrarian direction.

Output format:
<analysis>state the deviation and your rational contrarian stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade rationally: buy below fundamental, sell above, hold within the band.
"""


__all__ = ["RuleRationalTrader", "LLMRationalTrader"]
