"""hedged-fund — Convergence-arbitrage hedge fund with drawdown deleveraging.

Canonical implementation of the ``hedged-fund`` archetype documented in
``masim/agents/defines/finance/hedged-fund.md``. Enters when a valuation
spread widens beyond the entry threshold, exits on spread collapse, and
force-deleverages when drawdown exceeds the limit.

Theoretical basis:
    Shleifer & Vishny (1997) — The limits of arbitrage.
    Chevalier & Ellison (1997) — Risk taking by mutual funds as a
    response to incentives.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``drawdown >= max_drawdown``: sell ``deleverage_fraction * position``
        (forced deleveraging takes priority).
    Elif ``valuation_spread > entry_threshold``: buy
        ``min(cash / price, spread_size * valuation_spread)``.
    Elif ``valuation_spread < -exit_threshold`` and position > 0: sell
        ``min(position, spread_size * |valuation_spread|)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``max_drawdown``       : float — deleverage trigger (default 0.15).
    * ``entry_threshold``    : float — entry gate (default 0.08).
    * ``exit_threshold``     : float — exit gate (default 0.03,
                              inferred from worked example).
    * ``spread_size``        : float — per-spread scaling (default 600.0).
    * ``deleverage_fraction``: float — forced-sell fraction (default 0.4).

Scenario-specific inputs (via ``state.raw``, declared through
``REQUIRES_FEATURES``): ``valuation_spread``, ``drawdown``.
``valuation_spread`` falls back to ``state.deviation`` when not
broadcast; ``drawdown`` falls back to 0.0.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHedgedFund(CanonicalRulePlayer):
    STRATEGY = "hedged-fund"
    DISPLAY_NAME = "Hedge Fund (Convergence Arbitrage)"
    SUMMARY = (
        "Convergence arbitrageur with forced deleveraging on drawdown "
        "(Shleifer & Vishny 1997; Chevalier & Ellison 1997)."
    )
    REQUIRES_FEATURES: tuple = ("valuation_spread", "drawdown")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["max_drawdown"] = float(extras.get("max_drawdown", 0.15))
        cs["entry_threshold"] = float(extras.get("entry_threshold", 0.08))
        cs["exit_threshold"] = float(extras.get("exit_threshold", 0.03))
        cs["spread_size"] = float(extras.get("spread_size", 600.0))
        cs["deleverage_fraction"] = float(extras.get("deleverage_fraction", 0.4))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        max_dd = cs["max_drawdown"]
        entry = cs["entry_threshold"]
        exit_th = cs["exit_threshold"]
        spread_size = cs["spread_size"]
        delev_frac = cs["deleverage_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        drawdown = state.raw_require("drawdown", cast=float)
        valuation_spread = state.raw_require("valuation_spread", cast=float)

        # Forced deleveraging dominates.
        if drawdown >= max_dd and state.position > 0:
            quantity = delev_frac * state.position
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if valuation_spread > entry:
            quantity = min(state.cash / state.price, spread_size * valuation_spread)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if valuation_spread < -exit_th and state.position > 0:
            quantity = min(state.position, spread_size * abs(valuation_spread))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMHedgedFund(CanonicalLLMPlayer):
    STRATEGY = "hedged-fund"
    DEFAULT_SYS_PROMPT = """\
You are a convergence-arbitrage hedge fund. You take positions when a
valuation spread widens beyond your entry threshold and unwind when
the spread collapses. If your drawdown breaches the maximum, you are
forced to deleverage a fraction of your position regardless of the
opportunity — capital preservation dominates.

Output format:
<analysis>state the spread, drawdown, and any forced action.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Enter on widening spreads, exit on collapse, deleverage on drawdown.
"""


__all__ = ["RuleHedgedFund", "LLMHedgedFund"]
