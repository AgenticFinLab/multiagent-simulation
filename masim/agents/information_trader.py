"""information-trader — Predatory informed front-runner.

Canonical implementation of the ``information-trader`` archetype documented
in ``examples/AGENT_POOL/finance/information-trader.md``. Detects an
impending forced-liquidation signal with Bernoulli probability and front-
runs it; covers the resulting short after the recovery threshold is
crossed.

Theoretical basis:
    Kyle (1985) — informed trading with private signals.
    Brunnermeier & Pedersen (2005) — predatory trading around distressed
    liquidations.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    If deviation < detection_threshold and Bernoulli(detection_ability):
        sell min(front_run_size, position); short_position += qty
    Elif deviation > cover_threshold and short_position > 0:
        buy  min(cover_size, short_position, cash / price);
        short_position -= qty
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``detection_ability``    : float in [0,1] — probability of detecting
                                  the liquidation signal (default 0.50).
    * ``detection_threshold``  : float — deviation trigger for distress
                                  detection (default -0.05).
    * ``front_run_size``       : float — max sell on detection (default 1000).
    * ``cover_threshold``      : float — deviation above which covering is
                                  allowed (default -0.03).
    * ``cover_size``           : float — max buy-to-cover (default 500).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInformationTrader(CanonicalRulePlayer):
    STRATEGY = "information-trader"
    DISPLAY_NAME = "Predatory Informed Front-Runner"
    SUMMARY = (
        "Detects impending forced liquidation and front-runs it, covering "
        "the short after recovery (Kyle 1985; Brunnermeier & Pedersen 2005)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["detection_ability"] = float(
            extras.get("detection_ability", 0.50)
        )
        self.state.custom_state["detection_threshold"] = float(
            extras.get("detection_threshold", -0.05)
        )
        self.state.custom_state["front_run_size"] = float(
            extras.get("front_run_size", 1000.0)
        )
        self.state.custom_state["cover_threshold"] = float(
            extras.get("cover_threshold", -0.03)
        )
        self.state.custom_state["cover_size"] = float(
            extras.get("cover_size", 500.0)
        )
        # Virtual short position tracker (base framework does not permit
        # true shorting; we increment on emitted sells and decrement on
        # covers so the state variable in the profile is available).
        self.state.custom_state["short_position"] = 0.0

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        p_detect = self.state.custom_state["detection_ability"]
        theta_detect = self.state.custom_state["detection_threshold"]
        front_run_size = self.state.custom_state["front_run_size"]
        theta_cover = self.state.custom_state["cover_threshold"]
        cover_size = self.state.custom_state["cover_size"]
        short_pos = float(self.state.custom_state.get("short_position", 0.0))

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        if deviation < theta_detect and random.random() < p_detect:
            qty = min(front_run_size, state.position)
            if qty > 0:
                self.state.custom_state["short_position"] = short_pos + qty
                return InvestorOrder.sell(
                    quantity=float(qty),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )
            return hold

        if deviation > theta_cover and short_pos > 0:
            qty = min(cover_size, short_pos, state.cash / state.price)
            if qty > 0:
                self.state.custom_state["short_position"] = short_pos - qty
                return InvestorOrder.buy(
                    quantity=float(qty),
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )
            return hold

        return hold


class LLMInformationTrader(CanonicalLLMPlayer):
    STRATEGY = "information-trader"
    DEFAULT_SYS_PROMPT = """\
You are a predatory informed trader who reads order-flow stress around
forced-liquidation episodes. When distress is deep enough that your
private detection succeeds, you sell into the weakness ahead of the
liquidator, building a short. Once price recovers past your cover
threshold, you buy back to close. Otherwise you hold and wait.

Output format:
<analysis>state the distress / cover signals and your position stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Front-run detected liquidation, cover once recovery is under way; hold
otherwise.
"""


__all__ = ["RuleInformationTrader", "LLMInformationTrader"]
