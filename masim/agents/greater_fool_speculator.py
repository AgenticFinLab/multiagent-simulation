"""greater-fool-speculator — Bubble rider exiting on momentum reversal.

Canonical implementation of the ``greater-fool-speculator`` archetype
documented in ``examples/AGENT_POOL/finance/greater-fool-speculator.md``.
Rides positive momentum while overvaluation is below a crash threshold,
then exits aggressively when momentum turns or the ratio nears crash.

Theoretical basis:
    Tirole (1985) — Asset bubbles and overlapping generations.
    De Long, Shleifer, Summers & Waldmann (1990) — Noise trader risk in
    financial markets.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    overvaluation_ratio = price / fundamental_value
    If ``overvaluation_ratio >= crash_threshold * exit_trigger`` and
        ``position > 0``: sell entire position (emergency exit).
    If ``momentum_signal < 0`` and ``position > 0``:
        sell ``exit_speed * position``.
    If ``momentum_signal > 0`` and
        ``overvaluation_ratio < crash_threshold``:
        buy ``min(cash / price, momentum_size * momentum_signal)``.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``crash_threshold`` : float — collapse expectation (default 2.0).
    * ``momentum_size``   : float — buy scaling (default 500.0).
    * ``exit_speed``      : float — sell fraction (default 0.7).
    * ``exit_trigger``    : float — emergency fraction (default 0.9).

Scenario-specific input (via ``state.raw``, declared through
``REQUIRES_FEATURES``): ``momentum_signal``. Falls back to
``state.price_change`` when the scenario does not broadcast it.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleGreaterFoolSpeculator(CanonicalRulePlayer):
    STRATEGY = "greater-fool-speculator"
    DISPLAY_NAME = "Greater Fool Speculator"
    SUMMARY = (
        "Rides bubbles on positive momentum and exits on reversal or when "
        "price nears crash threshold (Tirole 1985; De Long et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ("momentum_signal",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["crash_threshold"] = float(extras.get("crash_threshold", 2.0))
        cs["momentum_size"] = float(extras.get("momentum_size", 500.0))
        cs["exit_speed"] = float(extras.get("exit_speed", 0.7))
        cs["exit_trigger"] = float(extras.get("exit_trigger", 0.9))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        crash_threshold = cs["crash_threshold"]
        momentum_size = cs["momentum_size"]
        exit_speed = cs["exit_speed"]
        exit_trigger = cs["exit_trigger"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold
        fundamental = state.fundamental
        if math.isnan(fundamental) or fundamental <= 0:
            return hold

        overvaluation_ratio = state.price / fundamental
        momentum_signal = float(
            state.raw.get("momentum_signal", state.price_change)
        )

        # Emergency exit dominates.
        if (
            overvaluation_ratio >= crash_threshold * exit_trigger
            and state.position > 0
        ):
            return InvestorOrder.sell(
                quantity=state.position,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if momentum_signal < 0 and state.position > 0:
            quantity = exit_speed * state.position
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if momentum_signal > 0 and overvaluation_ratio < crash_threshold:
            quantity = min(state.cash / state.price, momentum_size * momentum_signal)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        return hold


class LLMGreaterFoolSpeculator(CanonicalLLMPlayer):
    STRATEGY = "greater-fool-speculator"
    DEFAULT_SYS_PROMPT = """\
You are a greater-fool speculator riding an asset bubble. You buy while
positive momentum persists and overvaluation is still below your crash
threshold. When momentum turns negative you exit a large fraction of
your position; when overvaluation nears your crash trigger you dump
everything.

Output format:
<analysis>state overvaluation, momentum, and your intent.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}), change {price_change:+.2%}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Ride the bubble on positive momentum, dump on reversal or near-crash.
"""


__all__ = ["RuleGreaterFoolSpeculator", "LLMGreaterFoolSpeculator"]
