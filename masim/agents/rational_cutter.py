"""rational-cutter — Rational contrarian cutter.

Canonical implementation of the ``rational-cutter`` archetype
documented in ``examples/AGENT_POOL/finance/rational-cutter.md``. The
agent trades contrarian to observed deviations with quantity scaling
linearly with |dev| / cut_threshold once the threshold is breached.

Theoretical basis:
    Grossman & Miller (1988) — liquidity providers cut against price
    dislocations for a risk premium.
    Nagel (2012) — evaporating liquidity: contrarian trades earn expected
    returns proportional to the size of the dislocation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``|deviation| > cut_threshold``:
        qty = position_size * |dev| / cut_threshold
        direction = -sign(deviation)  (contrarian)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``cut_threshold`` : float — activation deviation (default 0.05).
    * ``position_size`` : float — base sizing (default 350).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalCutter(CanonicalRulePlayer):
    STRATEGY = "rational-cutter"
    DISPLAY_NAME = "Rational Cutter"
    SUMMARY = (
        "Cuts against price dislocations, size proportional to |deviation| "
        "(Grossman & Miller 1988; Nagel 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["cut_threshold"] = float(
            extras.get("cut_threshold", 0.05)
        )
        self.state.custom_state["position_size"] = float(
            extras.get("position_size", 350.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        threshold = self.state.custom_state["cut_threshold"]
        base = self.state.custom_state["position_size"]
        dev = state.deviation

        if abs(dev) <= threshold or threshold <= 0:
            return hold

        quantity = base * abs(dev) / threshold
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRationalCutter(CanonicalLLMPlayer):
    STRATEGY = "rational-cutter"
    DEFAULT_SYS_PROMPT = """\
You are a rational contrarian who cuts into dislocations. The bigger the
gap between price and fundamental, the more aggressively you trade in
the OPPOSITE direction: sell when price is above fundamental, buy when
below. Inside a narrow neutral band you stay flat.

Output format:
<analysis>state the deviation and your contrarian stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Cut against deviation: sell above fair value, buy below, hold inside band.
"""


__all__ = ["RuleRationalCutter", "LLMRationalCutter"]
