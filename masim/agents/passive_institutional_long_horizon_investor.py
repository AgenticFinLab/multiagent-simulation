"""PassiveInstitutionalLongHorizonInvestor — large-balance-sheet calendar rebalancer.

Theoretical basis: Brinson, Hood & Beebower (1986); Garleanu & Pedersen (2013);
Anand et al. (2013) — institutional rebalancing flow.

Decision rule:
    Identical mechanism to :class:`RebalancingStatusQuoInvestor` but tuned for
    institutional cadence: wider band, slower speed, periodic check (every
    ``rebalance_check_period`` rounds).  When the cycle gate is closed the
    agent holds.

Parameters (read from ``extras``):
    * ``target_allocation``: float, [0, 1] — strategic equity weight w*
      (default 0.60; Brinson-Hood-Beebower 1986 institutional baseline).
    * ``rebalance_band``: float — no-trade tolerance (default 0.05).
    * ``rebalance_speed``: float, (0, 1] — gap fraction closed per trigger
      (default 0.20).
    * ``rebalance_check_period``: int — cycle-gate length in rounds
      (default 20).
    * ``panic_band``: float — drawdown band beyond which rebalancing is
      suspended (default 0.20).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState


class RulePassiveInstitutionalLongHorizonInvestor(CanonicalRulePlayer):
    STRATEGY = "PassiveInstitutionalLongHorizonInvestor"
    DISPLAY_NAME = "Passive Institutional / Long-Horizon Investor"
    SUMMARY = (
        "Calendar-paced institutional rebalancer; large balance sheet, slow "
        "drift correction (Brinson-Hood-Beebower 1986)."
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
            extras.get("rebalance_speed", 0.20)
        )
        self.state.custom_state["rebalance_check_period"] = max(
            int(extras.get("rebalance_check_period", 20)), 1
        )
        self.state.custom_state["panic_band"] = float(
            extras.get("panic_band", 0.20)
        )

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        period = self.state.custom_state["rebalance_check_period"]
        if state.round <= 0 or (state.round % period) != 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        target = self.state.custom_state["target_allocation"]
        band = self.state.custom_state["rebalance_band"]
        speed = self.state.custom_state["rebalance_speed"]
        panic = self.state.custom_state["panic_band"]

        wealth = state.portfolio_value
        if wealth <= 0 or state.price <= 0:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        equity_value = state.position * state.price
        w_now = equity_value / wealth
        gap = target - w_now
        if abs(gap) > panic:
            # Stress regime: suspend rebalancing.
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}
        if abs(gap) <= band:
            return {"action": "hold", "quantity": 0.0, "bid_price": state.price}

        dollar_trade = abs(gap) * speed * wealth
        quantity = dollar_trade / state.price
        action = "buy" if gap > 0 else "sell"
        return {"action": action, "quantity": quantity, "bid_price": state.price}


class LLMPassiveInstitutionalLongHorizonInvestor(CanonicalLLMPlayer):
    STRATEGY = "PassiveInstitutionalLongHorizonInvestor"
    DEFAULT_SYS_PROMPT = """\
You are a large passive institutional investor (index fund or pension).
You target a long-run equity weight (e.g. 60%). You only check on a
slow calendar (e.g. every 20 rounds), and even then you trade in a
narrow band — never trying to time markets. In stress (very wide
gaps to target), you suspend rebalancing rather than fight the tide.

Output format:
<analysis>state whether the calendar gate is open and your gap to target</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": float,
           "bid_price": float, "reasoning": "..."}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}.
Cash={cash:.2f}, position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Hold by default; only act on your calendar cadence and only inside
normal-regime bands.
"""


__all__ = [
    "RulePassiveInstitutionalLongHorizonInvestor",
    "LLMPassiveInstitutionalLongHorizonInvestor",
]
