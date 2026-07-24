"""vol-etn-manager — Inverse-volatility ETP procyclical rebalance manager.

Canonical implementation of the ``vol-etn-manager`` archetype documented
in ``examples/AGENT_POOL/finance/vol-etn-manager.md``. One-sided
mechanical buy-only rebalance: whenever positive deviation exceeds a
public threshold, the product manager submits a buy order sized as a
linear function of the deviation, subject to a cash constraint. Never
sells — the procyclical Volmageddon amplifier.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Market liquidity and funding liquidity.
    U.S. SEC (2018) — Staff Report on Inverse and Leveraged ETPs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``state.deviation > rebalance_threshold``:
        q_raw = int(deviation * rebalance_size)
        q     = min(q_raw, int(cash / price))
        Emit buy at ``price`` if q > 0, else hold.
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rebalance_threshold`` : float — activation gate (default 0.05).
    * ``rebalance_size``      : float — Q_reb linear coefficient
                                 (default 10000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleVolEtnManager(CanonicalRulePlayer):
    STRATEGY = "vol-etn-manager"
    DISPLAY_NAME = "Inverse-Volatility ETP Manager"
    SUMMARY = (
        "Buy-only mechanical rebalancer that amplifies volatility spikes "
        "(Brunnermeier & Pedersen 2009; SEC 2018)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["rebalance_threshold"] = float(
            extras.get("rebalance_threshold", 0.05)
        )
        self.state.custom_state["rebalance_size"] = float(
            extras.get("rebalance_size", 10000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold

        deviation = state.deviation
        theta = self.state.custom_state["rebalance_threshold"]
        if deviation <= theta:
            return hold

        q_reb = self.state.custom_state["rebalance_size"]
        q_raw = float(int(deviation * q_reb))
        max_affordable = float(int(state.cash / state.price)) if state.cash > 0 else 0.0
        quantity = min(q_raw, max_affordable)
        if quantity <= 0:
            return hold

        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMVolEtnManager(CanonicalLLMPlayer):
    STRATEGY = "vol-etn-manager"
    DEFAULT_SYS_PROMPT = """\
You are the manager of an inverse-volatility exchange-traded product.
Your rebalance rule is public and one-sided: whenever the proxy
overshoots its fundamental by more than your rebalance threshold, you
must buy vol exposure sized as a linear function of the deviation. You
never sell — the rebalance is buy-only — and you stop only when cash is
exhausted or deviation falls back below the threshold.

Output format:
<analysis>brief reasoning (1-2 sentences) on the rebalance trigger.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance: if positive deviation exceeds your threshold, buy an amount
proportional to the deviation, capped by your available cash. Never sell.
"""


__all__ = ["RuleVolEtnManager", "LLMVolEtnManager"]
