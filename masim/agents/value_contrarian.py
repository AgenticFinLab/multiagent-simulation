"""value-contrarian — Long-horizon crisis-arb value contrarian.

Canonical implementation of the ``value-contrarian`` archetype documented
in ``masim/agents/defines/finance/value-contrarian.md``. Buys deeply
oversold assets during panic and sells into over-bullish rallies —
converges on fundamental with capital-constrained sizing.

Theoretical basis:
    Brunnermeier (2009) — Deciphering the liquidity and credit crunch 2007-2008.
    Shleifer & Vishny (1997) — The limits of arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental  (= state.deviation)

    If ``deviation < -oversold_threshold`` and cash > 0:
        q = min(base_position_size, |deviation| * sizing_scale)
        q = min(q, cash / price)
        Emit buy at ``price``.
    Elif ``deviation > overbought_threshold`` and position > 0:
        q = min(position, base_position_size)
        Emit sell at ``price``.
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``oversold_threshold``   : float — buy trigger (default 0.08).
    * ``overbought_threshold`` : float — sell trigger (default 0.10).
    * ``base_position_size``   : float — per-tick order cap (default 25.0).
    * ``sizing_scale``         : float — |deviation|→quantity multiplier
                                  (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleValueContrarian(CanonicalRulePlayer):
    STRATEGY = "value-contrarian"
    DISPLAY_NAME = "Crisis-Arbitrage Value Contrarian"
    SUMMARY = (
        "Long-horizon contrarian: buys deep discounts, sells rich premiums "
        "with capital constraints (Brunnermeier 2009; Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["oversold_threshold"] = float(
            extras.get("oversold_threshold", 0.08)
        )
        self.state.custom_state["overbought_threshold"] = float(
            extras.get("overbought_threshold", 0.10)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 25.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 800.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold

        deviation = state.deviation
        oversold = self.state.custom_state["oversold_threshold"]
        overbought = self.state.custom_state["overbought_threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        if deviation < -oversold and state.cash > 0 and state.price > 0:
            quantity = min(base, abs(deviation) * sizing)
            quantity = min(quantity, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation > overbought and state.position > 0:
            quantity = min(state.position, base)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMValueContrarian(CanonicalLLMPlayer):
    STRATEGY = "value-contrarian"
    DEFAULT_SYS_PROMPT = """\
You are a long-horizon value contrarian. You buy when price is well
below fundamental (panic selloffs), you sell when it is well above
(over-bullish rallies), and you hold inside a no-trade band. Your
capital is bounded; you size trades proportional to mispricing but
capped per round.

Output format:
<analysis>brief reasoning (1-2 sentences) on deviation vs. thresholds.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Contrarian: buy oversold, sell overbought, hold inside the no-trade band.
"""


__all__ = ["RuleValueContrarian", "LLMValueContrarian"]
