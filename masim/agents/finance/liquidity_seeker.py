"""liquidity-seeker — Depth-scaled uninformed liquidity seeker.

Canonical implementation of the ``liquidity-seeker`` archetype documented in
``masim/agents/defines/finance/liquidity-seeker.md``. Draws a mean-zero
Gaussian target every tick, scales it by observed market depth (proxied by
the scenario-specific ``liquidity`` field), clips to a hard per-tick cap and
executes at the market.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Uninformed liquidity demand modulated
    by depth.
    Coval & Stafford (2007) — Forced transactions scale with liquidity.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    target_raw       = N(0, target_volatility)
    adjustment       = min(1.0, liquidity / liquidity_base)
    target_scaled    = target_raw * adjustment
    quantity_signed  = clip(target_scaled, -max_quantity, max_quantity)

    quantity_signed > 0   ->  buy  round(quantity_signed)
    quantity_signed < 0   ->  sell round(|quantity_signed|)
    otherwise             ->  hold

Scenario-specific fields consumed via ``state.raw`` (see
``REQUIRES_FEATURES``): ``liquidity`` (market depth proxy). When absent, the
adjustment falls back to ``adjustment = 1.0`` so the agent still trades.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_volatility`` : float > 0 — std of the Gaussian target
                               (default 10.0, Brunnermeier & Pedersen 2009).
    * ``liquidity_base``    : float > 0 — depth reference (default 100.0).
    * ``max_quantity``      : float > 0 — per-tick cap (default 20.0).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLiquiditySeeker(CanonicalRulePlayer):
    STRATEGY = "liquidity-seeker"
    DISPLAY_NAME = "Depth-Scaled Liquidity Seeker"
    SUMMARY = (
        "Mean-zero uninformed liquidity demand scaled by market depth "
        "(Brunnermeier & Pedersen 2009; Coval & Stafford 2007)."
    )
    REQUIRES_FEATURES: tuple = ("liquidity",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_volatility"] = float(
            extras.get("target_volatility", 10.0)
        )
        self.state.custom_state["liquidity_base"] = float(
            extras.get("liquidity_base", 100.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 20.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        sigma = self.state.custom_state["target_volatility"]
        base = self.state.custom_state["liquidity_base"]
        cap = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        liquidity_val = state.raw_require("liquidity", cast=float)
        if base <= 0:
            adjustment = 1.0
        else:
            adjustment = min(1.0, liquidity_val / base)

        target_raw = random.gauss(0.0, sigma)
        target_scaled = target_raw * adjustment
        quantity_signed = max(min(target_scaled, cap), -cap)
        magnitude = abs(round(quantity_signed))
        if magnitude == 0:
            return hold
        if quantity_signed > 0:
            return InvestorOrder.buy(
                quantity=float(magnitude),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=float(magnitude),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLiquiditySeeker(CanonicalLLMPlayer):
    STRATEGY = "liquidity-seeker"
    DEFAULT_SYS_PROMPT = """\
You are a liquidity seeker. You are uninformed about direction — your
trades are mean-zero — but you scale your size with observed market
depth. Deep markets get larger orders; thin markets get proportionally
smaller ones, capped by a hard per-tick limit.

Output format:
<analysis>state depth-scaled sizing and the uninformed direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Draw a small mean-zero target, scale by observed depth, cap the size,
and execute at market — or hold when the draw rounds to zero.
"""


__all__ = ["RuleLiquiditySeeker", "LLMLiquiditySeeker"]
