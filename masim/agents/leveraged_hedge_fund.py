"""leveraged-hedge-fund — Margin-constrained leveraged hedge fund.

Canonical implementation of the ``leveraged-hedge-fund`` archetype documented
in ``examples/AGENT_POOL/finance/leveraged-hedge-fund.md``. Sizes trades on
short-run momentum when the margin ratio is healthy and liquidates
partially/fully once the margin ratio breaches a floor.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Funding-liquidity spirals.
    Adrian & Shin (2010) — Procyclical leverage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    position_value = position * price
    equity         = initial_equity + position * (price - entry_price)
    margin_ratio   = equity / position_value   (1.0 when position_value = 0)

    If ``margin_ratio < liquidation_level``: sell full position.
    Elif ``margin_ratio < margin_call_level``: sell position * 0.5.
    Else:
        price_return = (price - prev_price) / prev_price
        raw_qty      = momentum_sensitivity * price_return * 1000
        qty          = clip(raw_qty, -20, +30)
        if qty > 0: buy qty
        elif qty < 0: sell |qty|
        else: hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``margin_call_level``     : float in (0, 1) (default 0.5).
    * ``liquidation_level``     : float in (0, 1) (default 0.3).
    * ``momentum_sensitivity``  : float > 0 (default 1.0).
    * ``initial_leverage``      : float > 1 (default 3.0).
    * ``initial_equity``        : float > 0 (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedHedgeFund(CanonicalRulePlayer):
    STRATEGY = "leveraged-hedge-fund"
    DISPLAY_NAME = "Leveraged Hedge Fund"
    SUMMARY = (
        "Momentum-following leveraged hedge fund with margin-driven "
        "partial/full liquidations (Brunnermeier & Pedersen 2009; "
        "Adrian & Shin 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["margin_call_level"] = float(
            extras.get("margin_call_level", 0.5)
        )
        self.state.custom_state["liquidation_level"] = float(
            extras.get("liquidation_level", 0.3)
        )
        self.state.custom_state["momentum_sensitivity"] = float(
            extras.get("momentum_sensitivity", 1.0)
        )
        self.state.custom_state["initial_leverage"] = float(
            extras.get("initial_leverage", 3.0)
        )
        self.state.custom_state["initial_equity"] = float(
            extras.get("initial_equity", 1000.0)
        )
        self.state.custom_state["entry_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("entry_price") is None:
            self.state.custom_state["entry_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        mc_level = self.state.custom_state["margin_call_level"]
        liq_level = self.state.custom_state["liquidation_level"]
        sens = self.state.custom_state["momentum_sensitivity"]
        init_equity = self.state.custom_state["initial_equity"]
        entry_price = self.state.custom_state.get("entry_price") or state.price

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        position_value = state.position * state.price
        equity = init_equity + state.position * (state.price - entry_price)
        margin_ratio = (equity / position_value) if position_value > 0 else 1.0

        # 1) Full liquidation.
        if margin_ratio < liq_level and state.position > 0:
            return InvestorOrder.sell(
                quantity=state.position,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # 2) Partial liquidation.
        if margin_ratio < mc_level and state.position > 0:
            qty = state.position * 0.5
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # 3) Momentum sizing.
        if state.prev_price <= 0:
            return hold
        price_return = (state.price - state.prev_price) / state.prev_price
        raw_qty = sens * price_return * 1000.0
        qty = max(min(raw_qty, 30.0), -20.0)
        if qty > 0:
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if qty < 0:
            return InvestorOrder.sell(
                quantity=float(-qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLeveragedHedgeFund(CanonicalLLMPlayer):
    STRATEGY = "leveraged-hedge-fund"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged hedge fund. When your margin ratio is healthy you
size trades from short-run price momentum. When your margin ratio drops
below the partial-call level you halve your position; below the
liquidation level you exit entirely. Margin logic always beats momentum.

Output format:
<analysis>report margin ratio, then the momentum signal.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Check margin ratio first — full or partial liquidation if breached; else
size a small momentum trade capped at +30 / −20.
"""


__all__ = ["RuleLeveragedHedgeFund", "LLMLeveragedHedgeFund"]
