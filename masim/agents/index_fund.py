"""index-fund — Periodic constant-weight index fund / ETF.

Canonical implementation of the ``index-fund`` archetype documented in
``examples/AGENT_POOL/finance/index-fund.md``. Rebalances toward a target
equity weight on a fixed schedule; between rebalancing rounds, holds.
Provides mechanical mean-reverting demand.

Theoretical basis:
    Sharpe (1964) — constant-weight allocation from mean-variance theory.
    Garleanu & Pedersen (2013) — partial rebalancing optimal under
    transaction costs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If round % rebalance_frequency != 0: hold.

    Else:
        portfolio_value = position * price + cash
        target_position = target_weight * portfolio_value / price
        gap             = target_position - position
        raw_qty         = gap * adjustment_speed
        qty             = clamp(int(|raw_qty|), 0, max_rebalance_qty)
        Direction: buy if raw_qty > 0, sell if raw_qty < 0, else hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``target_weight``       : float — target equity share of portfolio
                                 value (default 0.6, standard 60/40).
    * ``rebalance_frequency`` : int   — rounds between rebalances (default 10).
    * ``adjustment_speed``    : float — fraction of gap closed per rebalance
                                 (default 0.5, Garleanu & Pedersen 2013).
    * ``max_rebalance_qty``   : float — cap on shares per rebalance
                                 (default 20).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndexFund(CanonicalRulePlayer):
    STRATEGY = "index-fund"
    DISPLAY_NAME = "Periodic Index Fund / ETF"
    SUMMARY = (
        "Passive constant-weight allocator that partially rebalances toward "
        "a target equity weight on a fixed schedule (Sharpe 1964; Garleanu "
        "& Pedersen 2013)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["target_weight"] = float(
            extras.get("target_weight", 0.6)
        )
        self.state.custom_state["rebalance_frequency"] = int(
            extras.get("rebalance_frequency", 10)
        )
        self.state.custom_state["adjustment_speed"] = float(
            extras.get("adjustment_speed", 0.5)
        )
        self.state.custom_state["max_rebalance_qty"] = float(
            extras.get("max_rebalance_qty", 20.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target_weight = self.state.custom_state["target_weight"]
        freq = self.state.custom_state["rebalance_frequency"]
        speed = self.state.custom_state["adjustment_speed"]
        max_qty = self.state.custom_state["max_rebalance_qty"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold
        if freq <= 0 or state.round % freq != 0:
            return hold

        portfolio_value = state.position * state.price + state.cash
        target_position = target_weight * portfolio_value / state.price
        gap = target_position - state.position
        raw_qty = gap * speed
        qty = float(min(int(abs(raw_qty)), int(max_qty)))
        if qty <= 0:
            return hold

        if raw_qty > 0:
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIndexFund(CanonicalLLMPlayer):
    STRATEGY = "index-fund"
    DEFAULT_SYS_PROMPT = """\
You are a passive index fund. You do not form fundamental views, chase
momentum, or read technicals. You only act on scheduled rebalancing
rounds; between them you hold. When you do rebalance, you partially close
the gap between your current equity weight and your fixed target weight,
subject to a per-round trade cap that limits market impact.

Output format:
<analysis>state whether this is a rebalance round and the gap you are
closing.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Rebalance on schedule toward your target equity weight; hold otherwise.
"""


__all__ = ["RuleIndexFund", "LLMIndexFund"]
