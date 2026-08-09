"""leveraged-fund — Target-leverage rebalancing fund.

Canonical implementation of the ``leveraged-fund`` archetype documented in
``masim/agents/defines/finance/leveraged-fund.md``. Continuously rebalances
its exposure toward a target-leverage ratio subject to a hard leverage
ceiling — a mechanical balance-sheet optimiser that inadvertently amplifies
market cycles.

Theoretical basis:
    Adrian & Shin (2010) — Procyclical leverage of financial intermediaries.
    Geanakoplos (2010) — Leverage cycle and margin ceilings.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    equity           = cash + position * price
    actual_leverage  = (position * price) / equity              [guard: eq>0]
    target_position  = target_leverage * equity / price

    If ``actual_leverage > max_leverage`` and ``position > 0``:
        sell min(position, (position * price - max_leverage * equity) / price)
    Elif ``actual_leverage > target_leverage + rebalance_band``:
        sell min(position, position - target_position)
    Elif ``actual_leverage < target_leverage - rebalance_band``:
        buy  min(cash / price, target_position - position)
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_leverage``  : float > 0 (default 5.0, Adrian & Shin 2010).
    * ``rebalance_band``   : float > 0 (default 0.10).
    * ``max_leverage``     : float > target (default 15.0, Geanakoplos 2010).
    * ``equity_floor``     : float > 0 (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedFund(CanonicalRulePlayer):
    STRATEGY = "leveraged-fund"
    DISPLAY_NAME = "Target-Leverage Rebalancing Fund"
    SUMMARY = (
        "Mechanically rebalances exposure to a target leverage ratio; "
        "force-delevers above the ceiling (Adrian & Shin 2010; "
        "Geanakoplos 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_leverage"] = float(
            extras.get("target_leverage", 5.0)
        )
        self.state.custom_state["rebalance_band"] = float(
            extras.get("rebalance_band", 0.10)
        )
        self.state.custom_state["max_leverage"] = float(
            extras.get("max_leverage", 15.0)
        )
        self.state.custom_state["equity_floor"] = float(
            extras.get("equity_floor", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target_lev = self.state.custom_state["target_leverage"]
        band = self.state.custom_state["rebalance_band"]
        max_lev = self.state.custom_state["max_leverage"]
        floor = self.state.custom_state["equity_floor"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        equity = state.cash + state.position * state.price
        if equity <= floor:
            return hold
        actual_lev = (state.position * state.price) / equity
        target_pos = target_lev * equity / state.price

        # 1) Hard ceiling breach — forced deleverage.
        if actual_lev > max_lev and state.position > 0:
            over = (state.position * state.price - max_lev * equity) / state.price
            qty = min(state.position, max(over, 0.0))
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # 2) Above target + band → trim.
        if actual_lev > target_lev + band and state.position > 0:
            qty = min(state.position, state.position - target_pos)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # 3) Below target − band → add.
        if actual_lev < target_lev - band:
            qty = min(state.cash / state.price, target_pos - state.position)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        return hold


class LLMLeveragedFund(CanonicalLLMPlayer):
    STRATEGY = "leveraged-fund"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged fund. Your mandate targets a fixed leverage ratio;
you continuously rebalance toward it, subject to a hard ceiling that
triggers a mechanical deleverage. You do not consider fundamentals or
momentum — only balance-sheet arithmetic.

Output format:
<analysis>report actual vs target leverage and the required rebalance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
change {price_change:+.2%}. Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Rebalance toward target leverage: sell if above target + band or ceiling
is breached, buy if below target − band, otherwise hold.
"""


__all__ = ["RuleLeveragedFund", "LLMLeveragedFund"]
