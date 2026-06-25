"""RebalancingStatusQuoInvestor — band-rebalancer with inertial/loss-aversion bias.

Theoretical basis: Perold & Sharpe (1988) — Dynamic Strategies; Samuelson &
Zeckhauser (1988) — Status Quo Bias; Madrian & Shea (2001); Constantinides (1984).

Decision rule:
    Each round, compute current equity weight
        equity_value = position * price
        wealth       = cash + equity_value
        w_now        = equity_value / wealth   (0 if wealth <= 0)
    If wealth is zero or stale, hold.  Otherwise, with probability
    ``engagement_probability`` the agent "checks" the band:
        gap = target_allocation - w_now
        If |gap| > rebalance_band:
            close ``rebalance_speed`` of the gap, sized to current wealth.
            buy if gap > 0, sell if gap < 0.

Parameters (read from ``extras``):
    * ``target_allocation``: float, [0, 1] — strategic equity weight w*
      (default 0.60).
    * ``rebalance_band``: float — no-trade tolerance (default 0.05).
    * ``rebalance_speed``: float, (0, 1] — gap fraction closed per trade
      (default 0.30).
    * ``engagement_probability``: float, (0, 1] — probability of checking the
      band each round (default 0.10; default-follower benchmark from
      Madrian-Shea 2001).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RuleRebalancingStatusQuoInvestor(CanonicalRulePlayer):
    STRATEGY = "RebalancingStatusQuoInvestor"
    DISPLAY_NAME = "Rebalancing / Status-Quo Investor"
    SUMMARY = (
        "Band-rebalancer with inertial bias; checks weights infrequently "
        "(Perold-Sharpe 1988; Madrian-Shea 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_allocation"] = float(
            extras.get("target_allocation", 0.60)
        )
        self.state.custom_state["rebalance_band"] = float(
            extras.get("rebalance_band", 0.05)
        )
        self.state.custom_state["rebalance_speed"] = float(
            extras.get("rebalance_speed", 0.30)
        )
        self.state.custom_state["engagement_probability"] = float(
            extras.get("engagement_probability", 0.10)
        )

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        target = self.state.custom_state["target_allocation"]
        band = self.state.custom_state["rebalance_band"]
        speed = self.state.custom_state["rebalance_speed"]
        engagement = self.state.custom_state["engagement_probability"]

        wealth = state.portfolio_value
        if wealth <= 0 or state.price <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        if random.random() >= engagement:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        equity_value = state.position * state.price
        w_now = equity_value / wealth
        gap = target - w_now
        if abs(gap) <= band:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        # Trade ``speed`` of the dollar gap, converted to shares at current price.
        dollar_trade = abs(gap) * speed * wealth
        quantity = dollar_trade / state.price
        action = "buy" if gap > 0 else "sell"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMRebalancingStatusQuoInvestor(CanonicalLLMPlayer):
    STRATEGY = "RebalancingStatusQuoInvestor"
    DEFAULT_SYS_PROMPT = """\
You are a band-rebalancing retail investor with strong status-quo bias.
You target a fixed equity weight (e.g. 60%) and only act when your
portfolio drifts outside a tolerance band. You check the band rarely
— most rounds you simply hold. When you do act, you partially close
the gap toward target.

Output format:
<analysis>state current equity weight, target, and whether you check today</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}.
Cash={cash:.2f}, position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If you decide to engage today and the equity weight is outside your
band, partially close the gap; otherwise hold.
"""


__all__ = [
    "RuleRebalancingStatusQuoInvestor",
    "LLMRebalancingStatusQuoInvestor",
]
