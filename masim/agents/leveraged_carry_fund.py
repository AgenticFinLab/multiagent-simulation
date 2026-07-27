"""leveraged-carry-fund — Stop-loss triggered leveraged carry fund.

Canonical implementation of the ``leveraged-carry-fund`` archetype documented
in ``examples/AGENT_POOL/finance/leveraged-carry-fund.md``. Sits on a
leveraged carry position under normal conditions and executes forced
liquidations once the price deviation breaches the stop-loss threshold.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Funding-liquidity spirals and
    stop-loss driven forced sales.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``deviation > stop_loss``: sell ``min(position, leverage * base_size)``.
    Else: hold.

    Note — the profile expresses ``deviation`` as a positive stop-loss cut-off
    on the price↔fundamental deviation (positive deviation = worsening carry).
    The agent only sells; it never adds to the position.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``stop_loss``   : float > 0 — deviation triggering forced sell
                         (default 0.03).
    * ``leverage``    : float > 1 — leverage multiplier on the base
                         liquidation size (default 5.0).
    * ``base_size``   : float > 0 — base liquidation size (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedCarryFund(CanonicalRulePlayer):
    STRATEGY = "leveraged-carry-fund"
    DISPLAY_NAME = "Leveraged Carry Fund (Stop-Loss)"
    SUMMARY = (
        "Leveraged carry fund that force-liquidates when the stop-loss "
        "threshold is breached (Brunnermeier & Pedersen 2009)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["stop_loss"] = float(extras.get("stop_loss", 0.03))
        self.state.custom_state["leverage"] = float(extras.get("leverage", 5.0))
        self.state.custom_state["base_size"] = float(extras.get("base_size", 800.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        stop_loss = self.state.custom_state["stop_loss"]
        leverage = self.state.custom_state["leverage"]
        base_size = self.state.custom_state["base_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold
        if state.deviation <= stop_loss:
            return hold
        if state.position <= 0:
            return hold

        sell_qty = min(state.position, leverage * base_size)
        if sell_qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=sell_qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLeveragedCarryFund(CanonicalLLMPlayer):
    STRATEGY = "leveraged-carry-fund"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged carry fund. Under normal conditions you sit on your
position collecting carry. When the deviation breaches your stop-loss
threshold, however, you liquidate aggressively — the exit is
non-discretionary. You never add to the position.

Output format:
<analysis>report deviation vs stop-loss and inventory.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Force-sell (leverage × base size, capped by position) if deviation
breaches your stop-loss; otherwise hold.
"""


__all__ = ["RuleLeveragedCarryFund", "LLMLeveragedCarryFund"]
