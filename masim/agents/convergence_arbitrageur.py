"""convergence-arbitrageur — LTCM-style leveraged relative-value trader.

Canonical implementation of the ``convergence-arbitrageur`` archetype
documented in ``masim/agents/defines/finance/convergence-arbitrageur.md``.
Deploys extreme leverage against spreads that exceed a minimum entry
band — buys discounts, sells premiums — sizing the order to leveraged
capacity capped at max_position.

Theoretical basis:
    Shleifer & Vishny (1997) — the limits of arbitrage.
    Jorion (2000) — risk-management lessons from Long-Term Capital
    Management.
    Lowenstein (2000) — When Genius Failed.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    dev = (price - fundamental) / fundamental
    IF |dev| <= entry_spread: HOLD
    ELIF dev < -entry_spread:
        leveraged_cash = cash * leverage
        qty = min(int(leveraged_cash * |dev| / price), max_position,
                  int(leveraged_cash / price))
        BUY qty (converge to fundamental — buy discount)
    ELIF dev >  entry_spread:
        leveraged_cash = cash * leverage
        qty = min(int(leveraged_cash * |dev| / price), max_position,
                  position)
        SELL qty (converge to fundamental — sell premium)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``entry_spread`` : float > 0 — |deviation| trigger (default 0.03).
    * ``leverage``     : int   > 0 — capital multiplier (default 15).
    * ``max_position`` : int   > 0 — position cap in shares
                          (default 5000).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleConvergenceArbitrageur(CanonicalRulePlayer):
    STRATEGY = "convergence-arbitrageur"
    DISPLAY_NAME = "LTCM-Style Convergence Arbitrageur"
    SUMMARY = (
        "Leveraged relative-value trader — buys discounts, sells "
        "premiums with high leverage (Shleifer & Vishny 1997; "
        "Jorion 2000)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["entry_spread"] = float(
            extras.get("entry_spread", 0.03)
        )
        self.state.custom_state["leverage"] = float(extras.get("leverage", 15))
        self.state.custom_state["max_position"] = int(
            extras.get("max_position", 5000)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        theta = self.state.custom_state["entry_spread"]
        leverage = self.state.custom_state["leverage"]
        max_pos = self.state.custom_state["max_position"]

        dev = state.deviation
        if abs(dev) <= theta:
            return hold

        leveraged_cash = max(state.cash, 0.0) * leverage
        raw_qty = int(leveraged_cash * abs(dev) / state.price)
        qty = min(raw_qty, max_pos)

        if dev < 0:
            # Buy discount — cap by leveraged capacity in shares.
            capacity = int(leveraged_cash / state.price)
            qty = min(qty, capacity)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # Sell premium — cap by current position.
        qty = min(qty, int(max(state.position, 0.0)))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMConvergenceArbitrageur(CanonicalLLMPlayer):
    STRATEGY = "convergence-arbitrageur"
    DEFAULT_SYS_PROMPT = """\
You are an LTCM-style convergence arbitrageur. You buy discounts and
sell premiums with high leverage whenever the spread exceeds a
minimum entry band. You size the order to leveraged capacity, capped
at a hard position limit. You never trade with the deviation
(Shleifer & Vishny 1997; Jorion 2000).

Output format:
<analysis>state the spread, direction of convergence, and leveraged sizing.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade to converge to fundamental when |deviation| exceeds entry_spread:
buy discounts, sell premiums, sized to leveraged capacity capped at
max_position; hold when the spread is too narrow.
"""


__all__ = ["RuleConvergenceArbitrageur", "LLMConvergenceArbitrageur"]
