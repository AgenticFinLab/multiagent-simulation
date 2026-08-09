"""liquidity-demander — Urgency-driven immediate transactor.

Canonical implementation of the ``liquidity-demander`` archetype documented
in ``masim/agents/defines/finance/liquidity-demander.md``. When a liquidity
need is signalled with sufficient urgency it fires an immediate market
order in the required direction.

Theoretical basis:
    Amihud (2002) — Illiquidity and stock returns; sizing of urgent demand.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``liquidity_need <= urgency_threshold``: hold.
    If ``need_direction == "buy"``:
        qty = min(cash / price, order_size_fraction * base_demand)
        buy qty.
    If ``need_direction == "sell"``:
        qty = min(position, order_size_fraction * base_demand)
        sell qty.

Scenario-specific fields consumed via ``state.raw`` (see
``REQUIRES_FEATURES``): ``liquidity_need`` (urgency intensity in [0, 1]) and
``need_direction`` (enum {"buy", "sell"}).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``urgency_threshold``    : float in [0, 1] (default 0.50).
    * ``order_size_fraction``  : float in (0, 1] (default 0.15,
                                  Amihud 2002).
    * ``base_demand``          : float > 0 (default 2000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLiquidityDemander(CanonicalRulePlayer):
    STRATEGY = "liquidity-demander"
    DISPLAY_NAME = "Urgency-Driven Liquidity Demander"
    SUMMARY = (
        "Urgent, cost-insensitive transactor; fires an immediate market "
        "order when a directional liquidity need crosses the urgency "
        "threshold (Amihud 2002)."
    )
    REQUIRES_FEATURES: tuple = ("liquidity_need", "need_direction")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["urgency_threshold"] = float(
            extras.get("urgency_threshold", 0.50)
        )
        self.state.custom_state["order_size_fraction"] = float(
            extras.get("order_size_fraction", 0.15)
        )
        self.state.custom_state["base_demand"] = float(
            extras.get("base_demand", 2000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        urgency_thr = self.state.custom_state["urgency_threshold"]
        frac = self.state.custom_state["order_size_fraction"]
        base = self.state.custom_state["base_demand"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        liquidity_need = state.raw_require("liquidity_need", cast=float)
        direction = state.raw_require("need_direction", cast=str).lower()
        if liquidity_need <= urgency_thr or direction not in {"buy", "sell"}:
            return hold

        target = frac * base
        if direction == "buy":
            if state.price <= 0 or state.cash <= 0:
                return hold
            qty = min(state.cash / state.price, target)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # sell
        qty = min(state.position, target)
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLiquidityDemander(CanonicalLLMPlayer):
    STRATEGY = "liquidity-demander"
    DEFAULT_SYS_PROMPT = """\
You are a liquidity demander. External flow needs (redemptions, hedging,
mandate rebalancing) drive your trades. When a directional need is
urgent enough you cross the spread immediately for a fixed slice of your
base demand. You do not negotiate on price.

Output format:
<analysis>report the urgency of your need and the required direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
If a directional liquidity need is above your urgency threshold, cross
the market for the fraction of base demand you can afford; else hold.
"""


__all__ = ["RuleLiquidityDemander", "LLMLiquidityDemander"]
