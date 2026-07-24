"""retail-coordinator — Social-media coordinator amplifying short squeezes.

Canonical implementation of the ``retail-coordinator`` archetype documented
in ``examples/AGENT_POOL/finance/retail-coordinator.md``. Reads the
scenario's coordination and short-interest signals and either accumulates
(when coordination is high) or exits (when coordination fades).

Theoretical basis:
    Cooper (1999) — Coordination games and squeeze dynamics.
    Pedersen (2022) — Short-interest as squeeze fuel.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    signal = coordination_signal            (from state.raw)
    si     = short_interest                 (from state.raw)

    If signal > coord_threshold AND si > si_threshold:
        I  = (signal - coord_threshold) / max(1e-6, 1 - coord_threshold)
        M  = 1 + si_boost * max(0.0, si - si_threshold)
        eps = gauss(0, noise_sigma)
        q_buy = min(cash / price,
                    coordination_weight * (cash / price) * I * M * (1 + eps))
        action = "buy" with quantity q_buy.
    Elif signal < exit_threshold AND position > 0:
        q_sell = min(position, exit_fraction * position)
        action = "sell" with quantity q_sell.
    Else: hold.

Scenario-specific fields (see ``REQUIRES_FEATURES``):
    * ``coordination_signal`` : float in [0, 1] — group coherence signal.
    * ``short_interest``      : float in [0, 1+] — outstanding short ratio.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``coord_threshold``      : float (default 0.50, Cooper 1999).
    * ``si_threshold``         : float (default 0.20, Pedersen 2022).
    * ``coordination_weight``  : float (default 0.20).
    * ``si_boost``             : float (default 2.0).
    * ``exit_threshold``       : float (default 0.25).
    * ``exit_fraction``        : float (default 0.40).
    * ``noise_sigma``          : float (default 0.10).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRetailCoordinator(CanonicalRulePlayer):
    STRATEGY = "retail-coordinator"
    DISPLAY_NAME = "Retail Squeeze Coordinator"
    SUMMARY = (
        "Social-media coordinator that accumulates in high-short-interest "
        "targets and exits on coordination fade (Cooper 1999; Pedersen 2022)."
    )
    REQUIRES_FEATURES: tuple = ("coordination_signal", "short_interest")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["coord_threshold"] = float(
            extras.get("coord_threshold", 0.50)
        )
        self.state.custom_state["si_threshold"] = float(
            extras.get("si_threshold", 0.20)
        )
        self.state.custom_state["coordination_weight"] = float(
            extras.get("coordination_weight", 0.20)
        )
        self.state.custom_state["si_boost"] = float(extras.get("si_boost", 2.0))
        self.state.custom_state["exit_threshold"] = float(
            extras.get("exit_threshold", 0.25)
        )
        self.state.custom_state["exit_fraction"] = float(
            extras.get("exit_fraction", 0.40)
        )
        self.state.custom_state["noise_sigma"] = float(
            extras.get("noise_sigma", 0.10)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        signal = state.raw_require("coordination_signal", cast=float)
        short_interest = state.raw_require("short_interest", cast=float)
        if math.isnan(signal) or math.isnan(short_interest):
            return hold

        # Buy branch: coordination and short-interest both above threshold.
        if signal > cs["coord_threshold"] and short_interest > cs["si_threshold"]:
            denom = max(1e-6, 1.0 - cs["coord_threshold"])
            intensity = (signal - cs["coord_threshold"]) / denom
            multiplier = 1.0 + cs["si_boost"] * max(
                0.0, short_interest - cs["si_threshold"]
            )
            eps = random.gauss(0.0, cs["noise_sigma"])
            raw_qty = (
                cs["coordination_weight"]
                * (state.cash / state.price)
                * intensity
                * multiplier
                * (1.0 + eps)
            )
            quantity = min(state.cash / state.price, max(0.0, raw_qty))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # Exit branch: coordination fades below exit threshold.
        if signal < cs["exit_threshold"] and state.position > 0:
            quantity = min(state.position, cs["exit_fraction"] * state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        return hold


class LLMRetailCoordinator(CanonicalLLMPlayer):
    STRATEGY = "retail-coordinator"
    DEFAULT_SYS_PROMPT = """\
You are a retail-community coordinator (a social-media rallying voice)
who amplifies a coordinated buying push against heavily-shorted stocks.
You buy aggressively when the group's coordination signal is high AND the
target has meaningful short interest, and you take profits when the group
loses cohesion. You never short.

Output format:
<analysis>state the coordination and short-interest signals and your posture.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Coordinate the cohort: buy hard when the movement is strong and the
target is heavily shorted; take profits by selling a fraction of the
position when coordination fades. Otherwise hold.
"""


__all__ = ["RuleRetailCoordinator", "LLMRetailCoordinator"]
