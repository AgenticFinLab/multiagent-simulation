"""sunk-cost-holder — Sunk-cost / house-money holder.

Canonical implementation of the ``sunk-cost-holder`` archetype documented
in ``examples/AGENT_POOL/finance/sunk-cost-holder.md``. Refuses to
realise losses (sunk-cost fallacy) and only partially trims once the
position is comfortably in the black.

Theoretical basis:
    Arkes & Blumer (1985) — the sunk-cost effect.
    Shefrin & Statman (1985) — disposition effect and the reluctance to
    realise losses.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    entry_price captured on first observation
    pnl = (price - entry_price) / entry_price

    if pnl <= 0:                              hold  (refuse to realise loss)
    elif pnl > take_profit and position > 0:  sell  int(position * trim_fraction)
    else:                                     hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``take_profit``     : float — pnl fraction to trigger trim
                            (default 0.10).
    * ``trim_fraction``   : float — fraction of position sold on trim
                            (default 0.6).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSunkCostHolder(CanonicalRulePlayer):
    STRATEGY = "sunk-cost-holder"
    DISPLAY_NAME = "Sunk-Cost Holder"
    SUMMARY = (
        "Refuses to sell at a loss (sunk-cost bias); trims partially only "
        "when comfortably in profit (Arkes-Blumer 1985; Shefrin-Statman "
        "1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["take_profit"] = float(
            extras.get("take_profit", 0.10)
        )
        self.state.custom_state["trim_fraction"] = float(
            extras.get("trim_fraction", 0.6)
        )
        self.state.custom_state["entry_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("entry_price") is None:
            try:
                self.state.custom_state["entry_price"] = float(
                    market_data["price"]
                )
            except (KeyError, TypeError, ValueError):
                return

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        entry = self.state.custom_state.get("entry_price")
        if entry is None or entry <= 0:
            return hold
        if state.position <= 0:
            return hold

        pnl = (state.price - entry) / entry
        if pnl <= 0:
            return hold

        take_profit = self.state.custom_state["take_profit"]
        trim = self.state.custom_state["trim_fraction"]
        if pnl <= take_profit:
            return hold

        quantity = float(int(state.position * trim))
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSunkCostHolder(CanonicalLLMPlayer):
    STRATEGY = "sunk-cost-holder"
    DEFAULT_SYS_PROMPT = """\
You are a sunk-cost-anchored retail investor. You refuse to realise a
loss on your position and only trim partially once the trade is
comfortably in profit above your take-profit level. You never buy more.

Output format:
<analysis>state the pnl vs entry and whether to trim.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Hold on any loss; trim a fixed fraction only once comfortably in profit.
"""


__all__ = ["RuleSunkCostHolder", "LLMSunkCostHolder"]
