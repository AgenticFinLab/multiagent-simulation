"""fundamental-trader — Threshold-based fundamental trader with signed clamp.

Canonical implementation of the ``fundamental-trader`` archetype documented
in ``examples/AGENT_POOL/finance/fundamental-trader.md``. Trades when
deviation from fundamental crosses a threshold; buys are clamped to
[0, 50] and sells to [-30, 0] to reflect asymmetric conviction.

Theoretical basis:
    Shiller (1981) — Do stock prices move too much to be justified by
    subsequent changes in dividends?
    Fama (1970) — Efficient capital markets: a review of theory and
    empirical work.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (fundamental - price) / fundamental
    raw_quantity = deviation * base_position_size * value_sensitivity
                   * value_multiplier

    If ``deviation > value_threshold``: buy
        ``clamp(raw_quantity, 0, 50)``.
    Elif ``deviation < -value_threshold``: sell
        ``|clamp(raw_quantity, -30, 0)|``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``value_threshold``     : float — activation gate (default 0.10).
    * ``base_position_size``  : float — base sizing (default 30.0).
    * ``value_sensitivity``   : float — deviation multiplier (default 1.0).
    * ``value_multiplier``    : float — extra scaling (default 10.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalTrader(CanonicalRulePlayer):
    STRATEGY = "fundamental-trader"
    DISPLAY_NAME = "Fundamental Trader"
    SUMMARY = (
        "Trades on fundamental deviation with asymmetric buy/sell caps "
        "(Shiller 1981; Fama 1970)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["value_threshold"] = float(extras.get("value_threshold", 0.10))
        cs["base_position_size"] = float(extras.get("base_position_size", 30.0))
        cs["value_sensitivity"] = float(extras.get("value_sensitivity", 1.0))
        cs["value_multiplier"] = float(extras.get("value_multiplier", 10.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["value_threshold"]
        base = cs["base_position_size"]
        sensitivity = cs["value_sensitivity"]
        multiplier = cs["value_multiplier"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.fundamental == 0:
            return hold
        deviation = (state.fundamental - state.price) / state.fundamental
        raw_quantity = deviation * base * sensitivity * multiplier

        if deviation > threshold:
            quantity = max(0.0, min(raw_quantity, 50.0))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation < -threshold:
            clamped = max(-30.0, min(raw_quantity, 0.0))
            quantity = abs(clamped)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMFundamentalTrader(CanonicalLLMPlayer):
    STRATEGY = "fundamental-trader"
    DEFAULT_SYS_PROMPT = """\
You are a fundamental trader. When price deviates materially from
fundamental value, you take a directional position — buying discounts
and selling premia. Your buy conviction is stronger than your sell
conviction, so buy orders can be larger than sell orders.

Output format:
<analysis>state the fundamental deviation and your directional stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade the deviation from fundamental value, hold if within threshold.
"""


__all__ = ["RuleFundamentalTrader", "LLMFundamentalTrader"]
