"""carry-trader — Leveraged carry trader with crash-risk unwind.

Canonical implementation of the ``carry-trader`` archetype documented in
``examples/AGENT_POOL/finance/carry-trader.md``. Accumulates a levered
long position while the funding-currency proxy trades below fundamental
and abruptly unwinds when it appreciates past threshold — the classic
carry-crash asymmetry.

Theoretical basis:
    Brunnermeier, Nagel & Pedersen (2009) — carry trades and currency
    crashes; leverage and funding-liquidity spirals amplify unwind
    volumes.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    q_buy  = min(cash / price, leverage * carry_size)   if deviation < -theta
    q_sell = min(position,     leverage * carry_size)   if deviation >  theta
    q      = 0                                           otherwise

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``unwind_threshold`` : float > 0 — |deviation| trigger (default 0.02).
    * ``leverage``         : float > 0 — position multiplier (default 5.0).
    * ``carry_size``       : float > 0 — base carry units (default 800.0).
    * ``deviation_scale``  : float > 0 — deviation sizing scale
                              (default 5000.0; retained for parity with
                              §Parameters even though the profile's
                              closed-form formula does not consume it).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCarryTrader(CanonicalRulePlayer):
    STRATEGY = "carry-trader"
    DISPLAY_NAME = "Leveraged Carry Trader"
    SUMMARY = (
        "Accumulates leveraged carry while deviation is negative and "
        "unwinds abruptly when it turns positive "
        "(Brunnermeier, Nagel & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["unwind_threshold"] = float(
            extras.get("unwind_threshold", 0.02)
        )
        self.state.custom_state["leverage"] = float(extras.get("leverage", 5.0))
        self.state.custom_state["carry_size"] = float(extras.get("carry_size", 800.0))
        self.state.custom_state["deviation_scale"] = float(
            extras.get("deviation_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        theta = self.state.custom_state["unwind_threshold"]
        leverage = self.state.custom_state["leverage"]
        carry_size = self.state.custom_state["carry_size"]
        dev = state.deviation

        max_carry = leverage * carry_size
        if dev < -theta:
            quantity = min(state.cash / state.price, max_carry)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev > theta:
            quantity = min(max(state.position, 0.0), max_carry)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCarryTrader(CanonicalLLMPlayer):
    STRATEGY = "carry-trader"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged carry trader. You accumulate a large long position
funded with leverage while the market trades below fundamental (positive
carry regime), and you unwind that position abruptly once the market
appreciates past the unwind threshold — the classic carry-crash
asymmetry (Brunnermeier, Nagel & Pedersen 2009).

Output format:
<analysis>state the deviation sign vs the unwind threshold and whether you are accumulating or unwinding.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Accumulate a leveraged long if deviation is sufficiently negative,
unwind if it turns sufficiently positive, otherwise hold.
"""


__all__ = ["RuleCarryTrader", "LLMCarryTrader"]
