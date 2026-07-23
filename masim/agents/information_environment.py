"""information-environment — Rumor / belief coordinator.

Canonical implementation of the ``information-environment`` archetype
documented in ``examples/AGENT_POOL/finance/information-environment.md``.
This archetype represents the shared social space through which rumors
propagate. It is not a market participant in the usual sense: it holds
every round and instead maintains and broadcasts aggregate belief and
distortion state derived from other participants' spreading / correcting
actions.

Because the canonical agent contract requires an ``InvestorOrder`` return
value, this agent always emits ``hold``. Its side-effect is to update
``belief`` and ``distortion`` inside ``custom_state`` so downstream tooling
(e.g. a scenario coordinator that reads these from the agent record) can
consume them.

Theoretical basis:
    Shibutani (1966) — the information environment as a "marketplace of
    rumors".
    Sunstein (2009) — how information environments shape and are shaped
    by participant behaviour.
    Allport & Postman (1947); Bartlett (1932) — sharpening and leveling
    of distortion.
    Vosoughi, Roy & Aral (2018) — spread dynamics of true and false news.
    Lewandowsky et al. (2012) — misinformation correction dynamics.

State evolution (from AGENT_POOL profile §Mathematical Model):

    Inputs read from ``state.raw`` each round:
        spread_intensities   : List[float]
        correct_intensities  : List[float]

    net_spread     = sum(spread_intensities) - sum(correct_intensities)
    spreader_count = len(spread_intensities)

    noise         ~ N(0, noise_std)
    new_belief    = clamp(belief
                           + spread_impact * net_spread
                           + truth_correction * (rumor_truth_value - belief)
                           + noise,
                          0, 1)
    new_distortion = clamp(distortion
                            - leveling_rate * distortion
                            + sharpening_rate * spreader_count
                                * (1 - rumor_truth_value),
                           0, 1)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``rumor_truth_value`` : float in [0,1] (default 0.1).
    * ``initial_belief``    : float in [0,1] (default 0.3).
    * ``spread_impact``     : float (default 0.15, Vosoughi et al. 2018).
    * ``truth_correction``  : float (default 0.02, Lewandowsky et al. 2012).
    * ``leveling_rate``     : float (default 0.01, Allport & Postman 1947).
    * ``sharpening_rate``   : float (default 0.02, Allport & Postman 1947).
    * ``noise_std``         : float (default 0.01).
    * ``initial_distortion``: float in [0,1] (default 0.1).
"""

from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


def _sum_intensities(raw_value: Any) -> tuple[float, int]:
    """Return (sum, count) from a possibly-missing intensity payload."""
    if raw_value is None:
        return 0.0, 0
    if isinstance(raw_value, dict):
        items: Iterable[float] = raw_value.values()
    else:
        try:
            items = list(raw_value)
        except TypeError:
            return 0.0, 0
    total = 0.0
    count = 0
    for v in items:
        try:
            total += float(v)
            count += 1
        except (TypeError, ValueError):
            continue
    return total, count


class RuleInformationEnvironment(CanonicalRulePlayer):
    STRATEGY = "information-environment"
    DISPLAY_NAME = "Rumor / Information Environment Coordinator"
    SUMMARY = (
        "Central coordinator that evolves aggregate belief and distortion "
        "state from participant spreading and correcting actions "
        "(Shibutani 1966; Allport & Postman 1947; Vosoughi et al. 2018)."
    )
    # The coordinator reads participant intensities from the raw payload.
    REQUIRES_FEATURES: tuple = ("spread_intensities", "correct_intensities")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["rumor_truth_value"] = float(
            extras.get("rumor_truth_value", 0.1)
        )
        self.state.custom_state["initial_belief"] = float(
            extras.get("initial_belief", 0.3)
        )
        self.state.custom_state["spread_impact"] = float(
            extras.get("spread_impact", 0.15)
        )
        self.state.custom_state["truth_correction"] = float(
            extras.get("truth_correction", 0.02)
        )
        self.state.custom_state["leveling_rate"] = float(
            extras.get("leveling_rate", 0.01)
        )
        self.state.custom_state["sharpening_rate"] = float(
            extras.get("sharpening_rate", 0.02)
        )
        self.state.custom_state["noise_std"] = float(extras.get("noise_std", 0.01))
        self.state.custom_state["initial_distortion"] = float(
            extras.get("initial_distortion", 0.1)
        )
        self.state.custom_state["belief"] = self.state.custom_state["initial_belief"]
        self.state.custom_state["distortion"] = self.state.custom_state[
            "initial_distortion"
        ]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        # Read intensities from the raw scenario payload.
        spread_sum, spreader_count = _sum_intensities(
            state.raw.get("spread_intensities")
        )
        correct_sum, _ = _sum_intensities(state.raw.get("correct_intensities"))
        net_spread = spread_sum - correct_sum

        belief = float(self.state.custom_state["belief"])
        distortion = float(self.state.custom_state["distortion"])
        truth = self.state.custom_state["rumor_truth_value"]
        spread_impact = self.state.custom_state["spread_impact"]
        truth_correction = self.state.custom_state["truth_correction"]
        leveling = self.state.custom_state["leveling_rate"]
        sharpening = self.state.custom_state["sharpening_rate"]
        noise_std = self.state.custom_state["noise_std"]

        noise = random.gauss(0.0, noise_std) if noise_std > 0 else 0.0
        new_belief = belief + spread_impact * net_spread + truth_correction * (
            truth - belief
        ) + noise
        new_belief = max(0.0, min(1.0, new_belief))

        new_distortion = (
            distortion
            - leveling * distortion
            + sharpening * spreader_count * (1.0 - truth)
        )
        new_distortion = max(0.0, min(1.0, new_distortion))

        self.state.custom_state["belief"] = new_belief
        self.state.custom_state["distortion"] = new_distortion

        # The coordinator does not itself trade — it evolves the shared
        # information environment. Always emit hold.
        return InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )


class LLMInformationEnvironment(CanonicalLLMPlayer):
    STRATEGY = "information-environment"
    DEFAULT_SYS_PROMPT = """\
You are the shared information environment for a rumor-spreading
simulation. You are a coordinator, not a market participant: you never
buy and never sell. Your role is to reflect the aggregate spreading and
correcting behaviour of other agents by evolving a collective belief
level and distortion level, and to hold in the market at all times.

Output format:
<analysis>describe the current aggregate belief and distortion.</analysis>
<decision>{"action": "hold", "quantity": 0,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
You are the information environment; always hold and reason about the
aggregate belief and distortion state.
"""


__all__ = ["RuleInformationEnvironment", "LLMInformationEnvironment"]
