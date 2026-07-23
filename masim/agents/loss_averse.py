"""loss-averse — Loss-averse disposition trader.

Canonical implementation of the ``loss-averse`` archetype documented in
``examples/AGENT_POOL/finance/loss-averse.md``. Reacts asymmetrically to
paper gains vs paper losses around a self-tracked cost basis: cuts big
on losses, takes small profits on modest gains.

Theoretical basis:
    Kahneman & Tversky (1979) — Prospect Theory, kinked value function
    around a reference point.
    Shefrin & Statman (1985); Odean (1998) — the disposition effect.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    cost_basis = first observed price (seeded via on_market_data).
    gain_pct   = (price - cost_basis) / cost_basis

    If ``gain_pct < -loss_threshold`` and ``position > 0``:
        sell ``sell_fraction_loss * position`` — capitulate.
    Elif ``gain_pct > gain_threshold`` and ``position > 0``:
        sell ``sell_fraction_gain * position`` — take small profit.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``loss_threshold``       : float — loss cut-off (default 0.03).
    * ``gain_threshold``       : float — gain cut-off (default 0.01).
    * ``sell_fraction_loss``   : float — fraction of position sold on
                                  loss trigger (default 0.80).
    * ``sell_fraction_gain``   : float — fraction of position sold on
                                  gain trigger (default 0.50).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLossAverse(CanonicalRulePlayer):
    STRATEGY = "loss-averse"
    DISPLAY_NAME = "Loss-Averse Disposition Trader"
    SUMMARY = (
        "Sells big on losses, takes small profits on gains around a "
        "self-tracked cost basis (Kahneman-Tversky 1979; Shefrin-Statman 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["loss_threshold"] = float(
            extras.get("loss_threshold", 0.03)
        )
        self.state.custom_state["gain_threshold"] = float(
            extras.get("gain_threshold", 0.01)
        )
        self.state.custom_state["sell_fraction_loss"] = float(
            extras.get("sell_fraction_loss", 0.80)
        )
        self.state.custom_state["sell_fraction_gain"] = float(
            extras.get("sell_fraction_gain", 0.50)
        )
        # Optional entry price override; otherwise seed from first broadcast.
        self.state.custom_state["cost_basis"] = extras.get("cost_basis")

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") in (None, 0, 0.0):
            price = market_data.get("price")
            if price is not None and float(price) > 0:
                self.state.custom_state["cost_basis"] = float(price)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        loss_th = self.state.custom_state["loss_threshold"]
        gain_th = self.state.custom_state["gain_threshold"]
        sfl = self.state.custom_state["sell_fraction_loss"]
        sfg = self.state.custom_state["sell_fraction_gain"]
        cost_basis = self.state.custom_state.get("cost_basis") or state.price

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if cost_basis <= 0 or state.position <= 0:
            return hold

        gain_pct = (state.price - cost_basis) / cost_basis

        if gain_pct < -loss_th:
            qty = sfl * state.position
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if gain_pct > gain_th:
            qty = sfg * state.position
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLossAverse(CanonicalLLMPlayer):
    STRATEGY = "loss-averse"
    DEFAULT_SYS_PROMPT = """\
You are a loss-averse investor with an asymmetric reaction to gains and
losses around your entry cost. You cut a large fraction of your position
after even modest paper losses, and you clip small profits early on gains.
Your reference point is where you bought, not fundamental value.

Output format:
<analysis>state your cost basis, current gain/loss, and which trigger fires.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide loss-aversely around your entry cost: cut heavy on losses, clip
small profits on gains, hold within the tolerance band.
"""


__all__ = ["RuleLossAverse", "LLMLossAverse"]
