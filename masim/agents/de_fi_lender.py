"""de-fi-lender — Protocol-liquidated DeFi collateral holder.

Canonical implementation of the ``de-fi-lender`` archetype documented in
``masim/agents/defines/finance/de-fi-lender.md``. When the price deviates
below a liquidation threshold from parity, the protocol force-sells a
fixed fraction of the agent's collateral position. Otherwise the agent
holds. Never buys.

Theoretical basis:
    Perez et al. (2021) — DeFi liquidation cascades.
    Werner et al. (2022) — automated forced-liquidation mechanics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - parity) / parity

    If deviation < -liquidation_threshold and position > 0:
        sell_qty = floor(position * liquidation_fraction)
        sell_qty = min(sell_qty, position)              → sell
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``liquidation_threshold`` : float — deviation magnitude triggering
                                  forced liquidation (default 0.08).
    * ``liquidation_fraction``  : float in (0, 1] — fraction of position
                                  force-sold per trigger (default 0.6).
    * ``parity``                : float — reference collateral value
                                  (default 1.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleDeFiLender(CanonicalRulePlayer):
    STRATEGY = "de-fi-lender"
    DISPLAY_NAME = "DeFi Collateral Lender (Force-Liquidated)"
    SUMMARY = (
        "Force-liquidates a fixed fraction of collateral when price "
        "deviates below parity (Perez et al. 2021; Werner et al. 2022)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["liquidation_threshold"] = float(
            extras.get("liquidation_threshold", 0.08)
        )
        self.state.custom_state["liquidation_fraction"] = float(
            extras.get("liquidation_fraction", 0.6)
        )
        self.state.custom_state["parity"] = float(extras.get("parity", 1.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cs = self.state.custom_state
        parity = cs["parity"]
        liquidation_threshold = cs["liquidation_threshold"]
        liquidation_fraction = cs["liquidation_fraction"]

        if parity <= 0 or state.position <= 0:
            return hold
        deviation = (state.price - parity) / parity

        if deviation < -liquidation_threshold:
            raw_qty = math.floor(state.position * liquidation_fraction)
            sell_qty = min(float(raw_qty), state.position)
            if sell_qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=sell_qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMDeFiLender(CanonicalLLMPlayer):
    STRATEGY = "de-fi-lender"
    DEFAULT_SYS_PROMPT = """\
You are a DeFi collateralised lender / borrower. You never trade
proactively. When the collateral price falls below the liquidation
threshold relative to parity, the protocol force-sells a fixed fraction
of your position — mechanistic, not psychological. Above that threshold
you hold indefinitely. You never buy.

Output format:
<analysis>state deviation vs liquidation threshold.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If price has fallen below the liquidation threshold from parity,
force-sell a fixed fraction of collateral; otherwise hold.
"""


__all__ = ["RuleDeFiLender", "LLMDeFiLender"]
