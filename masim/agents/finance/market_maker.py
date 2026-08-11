"""market-maker — Inventory-reverting market maker.

Canonical implementation of the ``market-maker`` archetype documented in
``masim/agents/defines/finance/market-maker.md``. Trades to mean-revert its
inventory back toward zero, but withdraws entirely when the market is
severely mispriced vs fundamental.

Theoretical basis:
    Ho & Stoll (1981) — inventory management by a dealer.
    Kyle (1985) — informed-trader / market-maker microstructure.
    Glosten & Milgrom (1985) — adverse-selection widening of spreads.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (fundamental - price) / price

    If ``|deviation| >= withdraw_threshold``: hold (withdraw quotes).
    Elif ``inventory > 0``: sell clamp(int(mean_reversion * inventory), 1, inventory).
    Elif ``inventory < 0``: buy clamp(int(mean_reversion * |inventory|), 1, |inventory|).
    Otherwise: hold.

Note: ``inventory`` is signed; positive inventory is long, negative is
short. We take ``self.state.position`` as the inventory (scenarios that
disallow shorts will always have position >= 0).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``mean_reversion``      : float — fraction of inventory reverted
                                 per round (default 0.10).
    * ``withdraw_threshold``  : float — |deviation| above which quotes
                                 are pulled (default 0.20).
    * ``inventory_limit``     : float — soft inventory cap for scaling
                                 (default 100.0).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMarketMaker(CanonicalRulePlayer):
    STRATEGY = "market-maker"
    DISPLAY_NAME = "Inventory-Reverting Market Maker"
    SUMMARY = (
        "Mean-reverts inventory to zero and withdraws when the market is "
        "severely mispriced (Ho-Stoll 1981; Kyle 1985; Glosten-Milgrom 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["mean_reversion"] = float(
            extras.get("mean_reversion", 0.10)
        )
        self.state.custom_state["withdraw_threshold"] = float(
            extras.get("withdraw_threshold", 0.20)
        )
        self.state.custom_state["inventory_limit"] = float(
            extras.get("inventory_limit", 100.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        eta = self.state.custom_state["mean_reversion"]
        withdraw_th = self.state.custom_state["withdraw_threshold"]
        _extras = {"provides_liquidity": True, "is_market_maker": True}

        hold = replace(
            InvestorOrder.hold(
                price=state.price, investor=self.identity, strategy=self.STRATEGY
            ),
            extras=_extras,
        )
        # Compute deviation from fundamental (fund - price)/price per profile.
        if state.price <= 0:
            return hold
        fundamental = state.fundamental
        if fundamental != fundamental or math.isnan(fundamental):
            # No fundamental modelled — safe fallback is to keep quoting
            # around inventory and never withdraw.
            deviation = 0.0
        else:
            deviation = (fundamental - state.price) / state.price

        if abs(deviation) >= withdraw_th:
            return hold

        inventory = state.position
        if inventory > 0:
            qty = int(eta * inventory)
            qty = max(1, min(qty, int(inventory)))
            return replace(
                InvestorOrder.sell(
                    quantity=float(qty),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                ),
                extras=_extras,
            )
        if inventory < 0:
            qty = int(eta * abs(inventory))
            qty = max(1, min(qty, int(abs(inventory))))
            return replace(
                InvestorOrder.buy(
                    quantity=float(qty),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                ),
                extras=_extras,
            )
        return hold


class LLMMarketMaker(CanonicalLLMPlayer):
    STRATEGY = "market-maker"
    DEFAULT_SYS_PROMPT = """\
You are an inventory-managing market maker. Your first-order goal is to
keep inventory near zero — you buy when short, sell when long, in small
increments each round. When the market is severely mispriced vs
fundamental you pull your quotes entirely to avoid adverse selection.

Output format:
<analysis>state your inventory sign and whether the market is safe to quote.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a market maker: revert inventory toward zero, withdraw when
mispricing is severe.
"""


__all__ = ["RuleMarketMaker", "LLMMarketMaker"]
