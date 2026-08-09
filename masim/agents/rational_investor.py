"""rational-investor — Target-allocation rational rebalancer.

Canonical implementation of the ``rational-investor`` archetype
documented in ``masim/agents/defines/finance/rational-investor.md``.
The agent holds a target risky-asset allocation and rebalances when
the actual allocation drifts outside the rebalance band, moving a
fraction of the gap per tick.

Theoretical basis:
    Merton (1969, 1971) — optimal lifetime consumption and portfolio
    choice under CRRA utility.
    Markowitz (1952) — mean-variance portfolio selection.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    wealth        = position * price + cash
    current_alloc = position * price / wealth
    gap           = current_alloc - target_allocation

    If ``|gap| > rebalance_threshold``:
        trade_value = rebalance_speed * gap * wealth
        if gap > 0: sell trade_value / price
        else:        buy  |trade_value| / price
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_allocation``   : float — target risky share (default 0.50).
    * ``rebalance_threshold`` : float — no-trade band (default 0.10).
    * ``rebalance_speed``     : float — fraction of gap closed per tick
                                 (default 0.50).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalInvestor(CanonicalRulePlayer):
    STRATEGY = "rational-investor"
    DISPLAY_NAME = "Rational Investor"
    SUMMARY = (
        "Target-allocation Merton/Markowitz rebalancer; trades a fraction "
        "of the wealth gap per tick (Merton 1969; Markowitz 1952)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_allocation"] = float(
            extras.get("target_allocation", 0.50)
        )
        self.state.custom_state["rebalance_threshold"] = float(
            extras.get("rebalance_threshold", 0.10)
        )
        self.state.custom_state["rebalance_speed"] = float(
            extras.get("rebalance_speed", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        target = self.state.custom_state["target_allocation"]
        band = self.state.custom_state["rebalance_threshold"]
        speed = self.state.custom_state["rebalance_speed"]

        wealth = state.position * state.price + state.cash
        if wealth <= 0:
            return hold
        current_alloc = state.position * state.price / wealth
        gap = current_alloc - target

        if abs(gap) <= band:
            return hold

        trade_value = speed * gap * wealth
        quantity = abs(trade_value) / state.price
        if quantity <= 0:
            return hold

        if gap > 0:
            # Over-allocated to risky asset → sell.
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        else:
            # Under-allocated → buy.
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )


class LLMRationalInvestor(CanonicalLLMPlayer):
    STRATEGY = "rational-investor"
    DEFAULT_SYS_PROMPT = """\
You are a rational long-term investor. You maintain a target allocation
between the risky asset and cash. Whenever your actual allocation drifts
outside a small band, you rebalance PARTIALLY (a fraction of the gap per
tick), not all at once. You don't chase moves; you correct them
mechanically to hit your target.

Output format:
<analysis>state target vs current allocation and your rebalance stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance toward your target allocation whenever the actual allocation
strays outside the band.
"""


__all__ = ["RuleRationalInvestor", "LLMRationalInvestor"]
