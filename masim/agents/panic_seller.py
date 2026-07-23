"""panic-seller — Panic-selling loss-averse investor.

Canonical implementation of the ``panic-seller`` archetype documented in
``examples/AGENT_POOL/finance/panic-seller.md``. Never buys. Fully
liquidates when cumulative P&L (versus entry price) breaches a loss
threshold; otherwise sells a fraction of position when a single-tick
return breaches a crash trigger.

Theoretical basis:
    Kahneman & Tversky (1979) — loss aversion around a reference point.
    Shiller (1984) — panic contagion.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    pnl_pct      = (price - entry_price) / entry_price
    price_return = (price - prev_price) / prev_price

    If ``pnl_pct < -loss_threshold`` AND position > 0:
        sell — quantity = position (full liquidation).
    Elif ``price_return < crash_trigger`` AND position > 0:
        sell — quantity = position * panic_sell_fraction.
    Otherwise: hold.

``entry_price`` is fixed at the first observed price.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``loss_threshold``      : float — cumulative-loss trigger (default 0.10).
    * ``crash_trigger``       : float — single-tick crash trigger
                                 (default -0.05).
    * ``panic_sell_fraction`` : float in [0,1] — fraction sold on crash
                                 (default 0.5).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePanicSeller(CanonicalRulePlayer):
    STRATEGY = "panic-seller"
    DISPLAY_NAME = "Panic Seller (Loss-Averse Liquidator)"
    SUMMARY = (
        "Never buys; fully liquidates on cumulative-loss breach and dumps a "
        "fraction of position on single-tick crashes "
        "(Kahneman & Tversky 1979; Shiller 1984)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["loss_threshold"] = float(
            extras.get("loss_threshold", 0.10)
        )
        self.state.custom_state["crash_trigger"] = float(
            extras.get("crash_trigger", -0.05)
        )
        self.state.custom_state["panic_sell_fraction"] = float(
            extras.get("panic_sell_fraction", 0.5)
        )
        self.state.custom_state["entry_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Fix entry_price at the first observed price.
        if self.state.custom_state.get("entry_price") is None:
            self.state.custom_state["entry_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        loss_th = self.state.custom_state["loss_threshold"]
        crash_th = self.state.custom_state["crash_trigger"]
        panic_fraction = self.state.custom_state["panic_sell_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        entry_price = self.state.custom_state.get("entry_price") or state.price
        if state.position <= 0 or entry_price <= 0:
            return hold

        pnl_pct = (state.price - entry_price) / entry_price
        if pnl_pct < -loss_th:
            quantity = max(state.position, 0.0)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if state.prev_price and state.prev_price > 0:
            price_return = (state.price - state.prev_price) / state.prev_price
            if price_return < crash_th:
                quantity = max(state.position, 0.0) * panic_fraction
                if quantity <= 0:
                    return hold
                return InvestorOrder.sell(
                    quantity=quantity,
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )
        return hold


class LLMPanicSeller(CanonicalLLMPlayer):
    STRATEGY = "panic-seller"
    DEFAULT_SYS_PROMPT = """\
You are a panic-selling loss-averse investor. You bought at an entry
price and never buy again. If your cumulative loss versus that entry
price exceeds your pain threshold, you liquidate the entire position
immediately. If the single-tick return crashes hard, you dump a large
fraction of what remains. In every other circumstance you hold.

Output format:
<analysis>state your entry price, current P&L, and whether a trigger has fired.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide as a panic seller: full liquidation on cumulative-loss breach,
partial dump on crash, hold otherwise. Never buy.
"""


__all__ = ["RulePanicSeller", "LLMPanicSeller"]
