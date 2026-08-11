"""loss-averse-investor — Prospect-theory loss-averse investor.

Canonical implementation of the ``loss-averse-investor`` archetype
documented in ``masim/agents/defines/finance/loss-averse-investor.md``.
Uses the Kahneman-Tversky lambda parameter to set an asymmetric loss
tolerance around an entry price.

Theoretical basis:
    Kahneman & Tversky (1979) — Prospect Theory value function with
    loss-aversion coefficient lambda ≈ 2.25.
    Benartzi & Thaler (1995) — myopic loss aversion.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    entry_price = first observed price (seeded via on_market_data)
    pnl_pct     = (price - entry_price) / entry_price
    loss_th     = base_loss_threshold * loss_aversion_lambda

    If ``pnl_pct > sell_gain_threshold`` and ``position > 0``:
        sell floor(position * 0.7) — take profit.
    Elif ``pnl_pct < -loss_th`` and ``position > 0``:
        sell floor(position * 0.2) — reluctant loss cut.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``loss_aversion_lambda``  : float — Kahneman-Tversky lambda
                                   (default 2.25).
    * ``base_loss_threshold``   : float — base loss cut-off before
                                   lambda scaling (default 0.05).
    * ``sell_gain_threshold``   : float — gain cut-off (default 0.05).
    * ``sell_fraction_gain``    : float — fraction of position sold on
                                   gain trigger (default 0.70).
    * ``sell_fraction_loss``    : float — fraction of position sold on
                                   loss trigger (default 0.20).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLossAverseInvestor(CanonicalRulePlayer):
    STRATEGY = "loss-averse-investor"
    DISPLAY_NAME = "Prospect-Theory Loss-Averse Investor"
    SUMMARY = (
        "Uses Kahneman-Tversky lambda≈2.25 to scale an asymmetric loss "
        "tolerance around entry (Kahneman-Tversky 1979; Benartzi-Thaler 1995)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["loss_aversion_lambda"] = float(
            extras.get("loss_aversion_lambda", 2.25)
        )
        self.state.custom_state["base_loss_threshold"] = float(
            extras.get("base_loss_threshold", 0.05)
        )
        self.state.custom_state["sell_gain_threshold"] = float(
            extras.get("sell_gain_threshold", 0.05)
        )
        self.state.custom_state["sell_fraction_gain"] = float(
            extras.get("sell_fraction_gain", 0.70)
        )
        self.state.custom_state["sell_fraction_loss"] = float(
            extras.get("sell_fraction_loss", 0.20)
        )
        self.state.custom_state["entry_price"] = extras.get("entry_price")

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("entry_price") in (None, 0, 0.0):
            price = market_data.get("price")
            if price is not None and float(price) > 0:
                self.state.custom_state["entry_price"] = float(price)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lam = self.state.custom_state["loss_aversion_lambda"]
        base_loss = self.state.custom_state["base_loss_threshold"]
        gain_th = self.state.custom_state["sell_gain_threshold"]
        sfg = self.state.custom_state["sell_fraction_gain"]
        sfl = self.state.custom_state["sell_fraction_loss"]
        entry = self.state.custom_state.get("entry_price") or state.price

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if entry <= 0 or state.position <= 0:
            return hold

        pnl_pct = (state.price - entry) / entry
        loss_th = base_loss * lam

        if pnl_pct > gain_th:
            qty = math.floor(state.position * sfg)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if pnl_pct < -loss_th:
            qty = math.floor(state.position * sfl)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLossAverseInvestor(CanonicalLLMPlayer):
    STRATEGY = "loss-averse-investor"
    DEFAULT_SYS_PROMPT = """\
You are a prospect-theory loss-averse investor. You anchor your reference
point to your entry price and feel losses about lambda≈2.25 times more
intensely than gains of equal magnitude. You take modest profits
proportionally and only cut losses reluctantly (a smaller fraction of your
holdings) once the loss becomes intolerable.

Output format:
<analysis>state your entry price, current PnL, and which side of the
kinked value function you are on.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide with prospect-theory loss aversion: take gains proportionally,
cut losses reluctantly, hold inside your tolerance.
"""


__all__ = ["RuleLossAverseInvestor", "LLMLossAverseInvestor"]
