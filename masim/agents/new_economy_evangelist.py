"""new-economy-evangelist — Paradigm-shift narrative believer.

Canonical implementation of the ``new-economy-evangelist`` archetype
documented in ``examples/AGENT_POOL/finance/new-economy-evangelist.md``.
Reads a scenario-provided ``narrative_strength`` signal (0-1). Buys
aggressively while the paradigm story is strong; capitulates and dumps a
large fraction of position when the story collapses.

Theoretical basis:
    Perez (2002) — technological revolutions and financial capital.
    Shiller (2019) — narrative economics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Read ``narrative_strength`` from ``state.raw`` (in [0, 1]).

    If ``narrative_strength > belief_threshold`` AND cash > 0:
        buy — quantity = ``narrative_weight * cash / price * (1 + eps)``,
        with ``eps ~ N(0, noise_sigma)``, floored to zero.
    Elif ``narrative_strength < capitulation_threshold`` AND position > 0:
        sell — quantity = ``panic_fraction * position``.
    Otherwise: hold.

    If ``narrative_strength`` is missing from the broadcast, hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``belief_threshold``       : float — buy trigger (default 0.50).
    * ``capitulation_threshold`` : float — capitulation trigger
                                    (default 0.15).
    * ``narrative_weight``       : float — cash fraction per buy
                                    (default 0.15).
    * ``panic_fraction``         : float — position fraction per crash sell
                                    (default 0.50).
    * ``noise_sigma``            : float — buy sizing noise stddev
                                    (default 0.05).
    * ``seed``                   : optional int — RNG seed.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleNewEconomyEvangelist(CanonicalRulePlayer):
    STRATEGY = "new-economy-evangelist"
    DISPLAY_NAME = "New-Economy Evangelist"
    SUMMARY = (
        "Buys while a paradigm-shift narrative is strong, capitulates and "
        "dumps a large fraction when the story collapses "
        "(Perez 2002; Shiller 2019)."
    )
    # Reads scenario-provided narrative_strength via state.raw.
    REQUIRES_FEATURES: tuple = ("narrative_strength",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["belief_threshold"] = float(
            extras.get("belief_threshold", 0.50)
        )
        self.state.custom_state["capitulation_threshold"] = float(
            extras.get("capitulation_threshold", 0.15)
        )
        self.state.custom_state["narrative_weight"] = float(
            extras.get("narrative_weight", 0.15)
        )
        self.state.custom_state["panic_fraction"] = float(
            extras.get("panic_fraction", 0.50)
        )
        self.state.custom_state["noise_sigma"] = float(
            extras.get("noise_sigma", 0.05)
        )
        seed = extras.get("seed")
        self.state.custom_state["rng"] = random.Random(seed)

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        belief_th = self.state.custom_state["belief_threshold"]
        capitulation_th = self.state.custom_state["capitulation_threshold"]
        weight = self.state.custom_state["narrative_weight"]
        panic_fraction = self.state.custom_state["panic_fraction"]
        sigma = self.state.custom_state["noise_sigma"]
        rng: random.Random = self.state.custom_state["rng"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        narrative = state.raw_require("narrative_strength", cast=float)

        if narrative > belief_th and state.cash > 0 and state.price > 0:
            base_qty = weight * state.cash / state.price
            noise = rng.gauss(0.0, sigma) if sigma > 0 else 0.0
            quantity = max(0.0, base_qty * (1.0 + noise))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if narrative < capitulation_th and state.position > 0:
            quantity = max(0.0, state.position * panic_fraction)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMNewEconomyEvangelist(CanonicalLLMPlayer):
    STRATEGY = "new-economy-evangelist"
    DEFAULT_SYS_PROMPT = """\
You are a new-economy evangelist. You believe in a paradigm-shift
narrative — a transformative story about the market. While that story
is strong, you deploy meaningful chunks of cash to buy in. When the
narrative collapses, you capitulate and dump a large fraction of your
position. Between those regimes you hold.

Output format:
<analysis>state the narrative strength you see and whether you are in believe/hold/capitulate mode.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide as a narrative believer: buy in while the story is strong,
capitulate when it collapses, otherwise hold.
"""


__all__ = ["RuleNewEconomyEvangelist", "LLMNewEconomyEvangelist"]
