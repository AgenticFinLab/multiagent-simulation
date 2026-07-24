"""mental-accountant — Mental-accounting per-bucket trader.

Canonical implementation of the ``mental-accountant`` archetype documented
in ``examples/AGENT_POOL/finance/mental-accountant.md``. Splits its
position into multiple mental accounts and evaluates each with prospect-
theoretic asymmetric gain/loss thresholds, sizing sell orders per bucket
rather than the whole book.

Theoretical basis:
    Thaler (1985, 1999) — mental accounting.
    Kahneman & Tversky (1979) — asymmetric gains/losses (lambda≈2.25).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    entry_price      = first observed price (seeded via on_market_data)
    per_account_pos  = position / num_accounts
    pnl_pct          = (price - entry_price) / entry_price

    If ``pnl_pct > gain_threshold`` and per-account > 0:
        sell floor(per_account_pos * sell_fraction_gain) — take profit.
    Elif ``pnl_pct < -(base_loss * loss_aversion_lambda)`` and per-account > 0:
        sell floor(per_account_pos * sell_fraction_loss) — reluctant cut.
    Otherwise: hold. Sell-only agent.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``num_accounts``            : int   — number of mental accounts
                                     (default 3).
    * ``loss_aversion_lambda``    : float — lambda (default 2.25).
    * ``base_loss_threshold``     : float — base loss cut-off (default 0.05).
    * ``gain_threshold``          : float — gain cut-off (default 0.05).
    * ``sell_fraction_gain``      : float — fraction of a bucket sold
                                     on gain trigger (default 0.70).
    * ``sell_fraction_loss``      : float — fraction of a bucket sold
                                     on loss trigger (default 0.20).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMentalAccountant(CanonicalRulePlayer):
    STRATEGY = "mental-accountant"
    DISPLAY_NAME = "Mental-Accounting Bucket Trader"
    SUMMARY = (
        "Evaluates each mental bucket with asymmetric loss-aversion "
        "thresholds (Thaler 1985/1999; Kahneman-Tversky 1979)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["num_accounts"] = int(
            extras.get("num_accounts", 3)
        )
        self.state.custom_state["loss_aversion_lambda"] = float(
            extras.get("loss_aversion_lambda", 2.25)
        )
        self.state.custom_state["base_loss_threshold"] = float(
            extras.get("base_loss_threshold", 0.05)
        )
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.05)
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
        num_accounts = max(1, self.state.custom_state["num_accounts"])
        lam = self.state.custom_state["loss_aversion_lambda"]
        base_loss = self.state.custom_state["base_loss_threshold"]
        gain_th = self.state.custom_state["gain_threshold"]
        sfg = self.state.custom_state["sell_fraction_gain"]
        sfl = self.state.custom_state["sell_fraction_loss"]
        entry = self.state.custom_state.get("entry_price") or state.price

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if entry <= 0 or state.position <= 0:
            return hold

        per_account = state.position / num_accounts
        if per_account <= 0:
            return hold

        pnl_pct = (state.price - entry) / entry
        loss_th = base_loss * lam

        if pnl_pct > gain_th:
            qty = math.floor(per_account * sfg)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if pnl_pct < -loss_th:
            qty = math.floor(per_account * sfl)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMMentalAccountant(CanonicalLLMPlayer):
    STRATEGY = "mental-accountant"
    DEFAULT_SYS_PROMPT = """\
You are a mental accountant. You mentally split your holdings into
multiple independent accounts and evaluate each one against your entry
price using prospect-theory asymmetric thresholds. On each round you may
choose to close a slice of one bucket at a gain (proportional) or
reluctantly trim a small slice at a large loss. You never buy.

Output format:
<analysis>state your per-bucket PnL and which bucket action fires.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a mental accountant: trim per-bucket on gains, reluctantly
sell a small bucket slice on large losses, else hold.
"""


__all__ = ["RuleMentalAccountant", "LLMMentalAccountant"]
