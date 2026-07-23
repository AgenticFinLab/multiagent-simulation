"""short-vol-trader — Short-volatility carry trader with stop-loss cover.

Canonical implementation of the ``short-vol-trader`` archetype documented in
``examples/AGENT_POOL/finance/short-vol-trader.md``. Sells short-vol
inventory during calm regimes (small negative deviation) and covers
aggressively when stress arrives (deviation above stop-loss).

Theoretical basis:
    Bollerslev (1986) — GARCH persistence and volatility risk premium.
    SEC (2018) staff report on the XIV episode — crowded-trade unwind.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    if  deviation > stop_loss  and  position < 0:
        buy   q = min(|position|, 0.8 * |position|)     # cover
    elif deviation < -0.02:
        sell  q = min(1000, cash / price)                # add carry
    else:
        hold

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``stop_loss``       : float — deviation trigger for covering
                            (default 0.15).
    * ``cover_fraction``  : float — fraction of the short book covered
                            per cover event (default 0.80).
    * ``carry_entry``     : float — negative-deviation floor triggering
                            fresh short-vol carry (default -0.02).
    * ``carry_cap``       : float — per-round unit cap on the carry sell
                            (default 1000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleShortVolTrader(CanonicalRulePlayer):
    STRATEGY = "short-vol-trader"
    DISPLAY_NAME = "Short-Volatility Carry Trader"
    SUMMARY = (
        "Sells short-vol during calm periods and covers on stress spikes "
        "(Bollerslev 1986; SEC 2018)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["stop_loss"] = float(extras.get("stop_loss", 0.15))
        self.state.custom_state["cover_fraction"] = float(
            extras.get("cover_fraction", 0.80)
        )
        self.state.custom_state["carry_entry"] = float(
            extras.get("carry_entry", -0.02)
        )
        self.state.custom_state["carry_cap"] = float(extras.get("carry_cap", 1000.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        stop_loss = self.state.custom_state["stop_loss"]
        cover_frac = self.state.custom_state["cover_fraction"]
        carry_entry = self.state.custom_state["carry_entry"]
        carry_cap = self.state.custom_state["carry_cap"]

        position = state.position
        cash = state.cash

        # Cover branch — deviation blew through stop-loss and we are short.
        if state.deviation > stop_loss and position < 0:
            magnitude = abs(position)
            quantity = min(magnitude, cover_frac * magnitude)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # Carry branch — small negative deviation invites more short-vol
        # inventory. Cap by both the per-round unit cap and cash-affordable
        # notional.
        if state.deviation < carry_entry and state.price > 0:
            quantity = min(carry_cap, cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        return hold


class LLMShortVolTrader(CanonicalLLMPlayer):
    STRATEGY = "short-vol-trader"
    DEFAULT_SYS_PROMPT = """\
You are a short-volatility carry trader. When markets are calm you press
your short-vol exposure; when the market gaps against you (price runs
well above fundamental) you slam the stop-loss and cover most of the
short book. You never chase a rally with fresh shorts.

Output format:
<analysis>state whether we are in carry, cover, or hold, and why.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide: cover when deviation is above your stop-loss and you are short;
add carry when deviation dips modestly negative; otherwise hold.
"""


__all__ = ["RuleShortVolTrader", "LLMShortVolTrader"]
