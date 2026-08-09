"""index-tracker — Passive proportional rebalancer.

Canonical implementation of the ``index-tracker`` archetype documented in
``masim/agents/defines/finance/index-tracker.md``. Continuously trades a
fraction of the gap between current and target position every round,
providing slow non-directional flow toward the target.

Theoretical basis:
    Perold & Sharpe (1988) — constant-mix / proportional rebalancing.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gap = target_position - position

    If |gap| <= rebalance_threshold: hold.
    Else:
        raw_trade = gap * rebalance_rate
        trade_qty = clamp(raw_trade, -max_trade, +max_trade)
        buy  if trade_qty > 0, sell if < 0, hold if 0.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_position``     : float — target holdings (default 50.0).
    * ``rebalance_threshold`` : float — dead-band on |gap| (default 1.0,
                                 Perold & Sharpe 1988).
    * ``rebalance_rate``      : float in [0,1] — fraction of gap closed
                                 per round (default 0.3).
    * ``max_trade``           : float — per-round cap (default 10.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndexTracker(CanonicalRulePlayer):
    STRATEGY = "index-tracker"
    DISPLAY_NAME = "Passive Index Tracker"
    SUMMARY = (
        "Slow mechanical rebalancer that closes a fraction of the gap to a "
        "fixed target position every round (Perold & Sharpe 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_position"] = float(
            extras.get("target_position", 50.0)
        )
        self.state.custom_state["rebalance_threshold"] = float(
            extras.get("rebalance_threshold", 1.0)
        )
        self.state.custom_state["rebalance_rate"] = float(
            extras.get("rebalance_rate", 0.3)
        )
        self.state.custom_state["max_trade"] = float(extras.get("max_trade", 10.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target = self.state.custom_state["target_position"]
        thr = self.state.custom_state["rebalance_threshold"]
        rate = self.state.custom_state["rebalance_rate"]
        cap = self.state.custom_state["max_trade"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        gap = target - state.position
        if abs(gap) <= thr:
            return hold

        raw_trade = gap * rate
        trade_qty = max(-cap, min(cap, raw_trade))
        if trade_qty > 0:
            return InvestorOrder.buy(
                quantity=float(trade_qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if trade_qty < 0:
            return InvestorOrder.sell(
                quantity=float(abs(trade_qty)),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMIndexTracker(CanonicalLLMPlayer):
    STRATEGY = "index-tracker"
    DEFAULT_SYS_PROMPT = """\
You are a passive index tracker. You do not form views on value or
direction; you simply drift toward a fixed target position by trading a
fraction of the gap each round. Your influence is gradual — small,
regular orders that dampen extreme moves without responding to
short-term speculation.

Output format:
<analysis>state your current gap to target and the fraction you close
this round.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Close a fraction of your target-position gap; hold inside the dead band.
"""


__all__ = ["RuleIndexTracker", "LLMIndexTracker"]
