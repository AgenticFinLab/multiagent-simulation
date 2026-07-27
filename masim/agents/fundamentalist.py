"""fundamentalist — Brock-Hommes fundamentalist with noise and frequency gating.

Canonical implementation of the ``fundamentalist`` archetype documented in
``examples/AGENT_POOL/finance/fundamentalist.md``. Trades on noisy value
estimates every ``trade_frequency`` rounds; provides slow stabilising
demand around the true fundamental.

Theoretical basis:
    Brock & Hommes (1998) — Heterogeneous beliefs and routes to chaos in
    a simple asset pricing model.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Only trade if ``round % trade_frequency == 0``.
    estimated_value = fundamental + N(0, value_noise_std)
    deviation = (estimated_value - price) / price
    quantity = value_sensitivity * deviation * base_position_size
    Clamp signed quantity to [-20, 20]; positive → buy, negative → sell.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``trade_frequency``    : int — trade every N rounds (default 3).
    * ``value_sensitivity``  : float — deviation multiplier (default 0.5).
    * ``base_position_size`` : float — base sizing (default 20.0).
    * ``value_noise_std``    : float — noise std dev on value (default 2.0).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundamentalist(CanonicalRulePlayer):
    STRATEGY = "fundamentalist"
    DISPLAY_NAME = "Fundamentalist (Brock-Hommes)"
    SUMMARY = (
        "Noisy value estimator trading periodically toward true fundamental "
        "(Brock & Hommes 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["trade_frequency"] = int(extras.get("trade_frequency", 3))
        cs["value_sensitivity"] = float(extras.get("value_sensitivity", 0.5))
        cs["base_position_size"] = float(extras.get("base_position_size", 20.0))
        cs["value_noise_std"] = float(extras.get("value_noise_std", 2.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        freq = cs["trade_frequency"]
        sensitivity = cs["value_sensitivity"]
        base = cs["base_position_size"]
        noise_std = cs["value_noise_std"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if freq <= 0 or state.round % freq != 0:
            return hold
        if state.price <= 0 or math.isnan(state.fundamental):
            return hold

        noise = random.gauss(0.0, noise_std) if noise_std > 0 else 0.0
        estimated_value = state.fundamental + noise
        deviation = (estimated_value - state.price) / state.price
        raw_quantity = sensitivity * deviation * base
        signed = max(-20.0, min(raw_quantity, 20.0))
        if signed > 0:
            return InvestorOrder.buy(
                quantity=signed,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if signed < 0:
            return InvestorOrder.sell(
                quantity=abs(signed),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMFundamentalist(CanonicalLLMPlayer):
    STRATEGY = "fundamentalist"
    DEFAULT_SYS_PROMPT = """\
You are a Brock-Hommes fundamentalist. You believe price should revert
to fundamental value, but your estimate of that value is noisy. You
review the market only every few rounds; when you do act, you take a
small position in the direction of your estimated mispricing.

Output format:
<analysis>note your noisy value estimate vs price.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade a small position toward fundamental if this is your active round.
"""


__all__ = ["RuleFundamentalist", "LLMFundamentalist"]
