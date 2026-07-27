"""program-trader — Program-trading feedback seller (Brady-style).

Canonical implementation of the ``program-trader`` archetype
documented in ``examples/AGENT_POOL/finance/program-trader.md``.
Amplifies price moves via mechanical, deviation-triggered sell (and
optional buy) programs — the mechanism the Brady Commission (1988)
implicated in Black Monday.

Theoretical basis:
    Brady Commission (1988) — Report on the October 1987 market break.
    Duffie (2010) — presidential address on slow-moving capital and
    fire-sale externalities.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``deviation < -theta_prog`` AND position > 0:
        sell = min(position, base_size * (1 + phi * |dev| * 10)).
    If ``deviation > theta_prog`` AND cash > 0:
        buy  = min(cash/price, base_size * (1 + phi * |dev| * 10)).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``theta_prog`` : float — activation deviation (default 0.01).
    * ``phi``        : float — deviation-to-size sensitivity (default 1.20).
    * ``base_size``  : float — baseline order size (default 60.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleProgramTrader(CanonicalRulePlayer):
    STRATEGY = "program-trader"
    DISPLAY_NAME = "Program Trader"
    SUMMARY = (
        "Mechanical deviation-triggered program trader; amplifies moves "
        "(Brady Commission 1988; Duffie 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["theta_prog"] = float(
            extras.get("theta_prog", 0.01)
        )
        self.state.custom_state["phi"] = float(extras.get("phi", 1.20))
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 60.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold

        theta = self.state.custom_state["theta_prog"]
        phi = self.state.custom_state["phi"]
        base = self.state.custom_state["base_size"]
        dev = state.deviation

        if dev < -theta and state.position > 0:
            size = base * (1.0 + phi * abs(dev) * 10.0)
            quantity = min(state.position, size)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev > theta and state.cash > 0:
            size = base * (1.0 + phi * abs(dev) * 10.0)
            affordable = state.cash / state.price
            quantity = min(affordable, size)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMProgramTrader(CanonicalLLMPlayer):
    STRATEGY = "program-trader"
    DEFAULT_SYS_PROMPT = """\
You run a program-trading book. Your logic is mechanical: when the market
deviation crosses your trigger you fire a block trade in the SAME
direction as the move (sell into declines, buy into rallies) with size
scaled by the deviation. You never fight the tape — you accelerate it.

Output format:
<analysis>state the deviation and your program trigger.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Execute the program: sell into declines, buy into rallies.
"""


__all__ = ["RuleProgramTrader", "LLMProgramTrader"]
