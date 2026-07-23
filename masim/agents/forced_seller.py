"""forced-seller — Distressed leveraged trader unwinding into a falling market.

Canonical implementation of the ``forced-seller`` archetype documented in
``examples/AGENT_POOL/finance/forced-seller.md``. Liquidates a fraction of
the position when the current margin falls below the maintenance margin,
amplifying declines through fire-sale dynamics.

Theoretical basis:
    Shleifer & Vishny (2011) — Fire sales in finance and macroeconomics.
    Brunnermeier & Pedersen (2009) — Market liquidity and funding liquidity.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``current_margin < maintenance_margin`` and ``position > 0``:
        raw_qty = liquidation_fraction * position
                  * (maintenance_margin - current_margin) / maintenance_margin
        Enforce ``min_sell`` floor and clamp to available position.
        If ``position <= position_floor``: sell entire remaining position.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``maintenance_margin``  : float — margin trigger (default 0.30).
    * ``liquidation_fraction``: float — deficit fraction sold (default 0.35).
    * ``min_sell``            : float — minimum unit sell (default 100.0).
    * ``position_floor``      : float — clear-out level (default 50.0).

Scenario-specific input read via ``state.raw`` (declared through
``REQUIRES_FEATURES``): ``current_margin``.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleForcedSeller(CanonicalRulePlayer):
    STRATEGY = "forced-seller"
    DISPLAY_NAME = "Forced Seller"
    SUMMARY = (
        "Distressed leveraged trader liquidating into declines "
        "(Shleifer & Vishny 2011; Brunnermeier & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ("current_margin",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["maintenance_margin"] = float(extras.get("maintenance_margin", 0.30))
        cs["liquidation_fraction"] = float(extras.get("liquidation_fraction", 0.35))
        cs["min_sell"] = float(extras.get("min_sell", 100.0))
        cs["position_floor"] = float(extras.get("position_floor", 50.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        maint = cs["maintenance_margin"]
        frac = cs["liquidation_fraction"]
        min_sell = cs["min_sell"]
        floor = cs["position_floor"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.position <= 0:
            return hold

        current_margin = float(state.raw.get("current_margin", math.nan))
        if math.isnan(current_margin) or current_margin >= maint or maint <= 0:
            return hold

        # Clear out dust positions entirely.
        if state.position <= floor:
            return InvestorOrder.sell(
                quantity=state.position,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        deficit_ratio = (maint - current_margin) / maint
        raw_qty = frac * state.position * deficit_ratio
        quantity = max(raw_qty, min_sell)
        quantity = min(quantity, state.position)
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMForcedSeller(CanonicalLLMPlayer):
    STRATEGY = "forced-seller"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged trader facing a margin call. Once your margin
breaches maintenance, you must liquidate a fraction of your position
each round — regardless of price — to restore margin. You never buy;
you only sell to reduce exposure. When margin is comfortable you hold.

Output format:
<analysis>describe your margin state and any liquidation pressure.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Sell part of your position if margin has breached maintenance;
otherwise hold.
"""


__all__ = ["RuleForcedSeller", "LLMForcedSeller"]
