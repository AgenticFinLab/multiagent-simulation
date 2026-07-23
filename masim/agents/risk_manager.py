"""risk-manager — VaR-triggered forced deleveraging.

Canonical implementation of the ``risk-manager`` archetype documented in
``examples/AGENT_POOL/finance/risk-manager.md``. Sells a fraction of the
existing long position whenever the price-to-fundamental deviation breaches
three times the configured VaR limit. Never buys.

Theoretical basis:
    Jorion (2000) — Value-at-Risk methodology.
    Brunnermeier & Pedersen (2009) — Funding-liquidity spirals and forced
        deleveraging.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation         = (price - fundamental) / fundamental
    effective_trigger = var_limit * 3

    IF |deviation| > effective_trigger AND position > 0:
        qty    = max(1, int(position * cut_fraction))
        action = "sell"
    ELSE: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``var_limit``     : float (default 0.05, Jorion 2000).
    * ``cut_fraction``  : float in (0, 1] (default 0.50,
                          Brunnermeier & Pedersen 2009).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRiskManager(CanonicalRulePlayer):
    STRATEGY = "risk-manager"
    DISPLAY_NAME = "Institutional Risk Manager"
    SUMMARY = (
        "VaR-triggered forced deleveraging — cuts a fraction of long "
        "exposure when deviation breaches 3× the VaR limit "
        "(Jorion 2000; Brunnermeier & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["var_limit"] = float(extras.get("var_limit", 0.05))
        self.state.custom_state["cut_fraction"] = float(
            extras.get("cut_fraction", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        var_limit = self.state.custom_state["var_limit"]
        cut_fraction = self.state.custom_state["cut_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # NaN guard — no fundamental broadcast means the VaR trigger cannot fire.
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.position <= 0:
            return hold

        effective_trigger = var_limit * 3.0
        if abs(state.deviation) <= effective_trigger:
            return hold

        qty = max(1, int(state.position * cut_fraction))
        qty = min(qty, int(state.position))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRiskManager(CanonicalLLMPlayer):
    STRATEGY = "risk-manager"
    DEFAULT_SYS_PROMPT = """\
You are an institutional risk manager overseeing an existing long book.
Your mandate is loss containment, not alpha generation. When the market
deviation from fundamental exceeds three times your Value-at-Risk limit
you force a partial liquidation of the existing position. You never
initiate new long exposure — only sell.

Output format:
<analysis>state whether the VaR-scaled trigger has been breached and how much to cut.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Cut a fraction of the long position only when the deviation clearly
breaches your VaR-scaled threshold. Never buy.
"""


__all__ = ["RuleRiskManager", "LLMRiskManager"]
