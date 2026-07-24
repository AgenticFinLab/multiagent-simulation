"""narrative-believer — Narrative-driven trend confirmer.

Canonical implementation of the ``narrative-believer`` archetype documented
in ``examples/AGENT_POOL/finance/narrative-believer.md``. Interprets each
price deviation from fundamental as evidence about a story: rising prices
confirm the narrative and trigger buying; falling prices disconfirm it and
trigger selling. Sizes conviction linearly with deviation magnitude.

Theoretical basis:
    Shiller (2017) — Narrative Economics; contagious stories driving prices.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= activation_threshold``: hold.
    Elif ``deviation > 0``: buy — narrative confirmed.
    Elif ``deviation < 0``: sell — narrative failing.

    Quantity = ``min(max_quantity, |deviation| * scaling_factor)``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — deviation cut-off (default 0.02).
    * ``scaling_factor``       : float — deviation→quantity factor
                                  (default 5000.0).
    * ``max_quantity``         : float — per-tick order cap (default 800.0).
    * ``narrative_weight``     : float in [0,1] — persona weight, recorded
                                  for the LLM sibling (default 0.8).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleNarrativeBeliever(CanonicalRulePlayer):
    STRATEGY = "narrative-believer"
    DISPLAY_NAME = "Narrative-Believer Trend Confirmer"
    SUMMARY = (
        "Treats rising prices as confirming a story and falling prices as "
        "refuting it; buys into positive deviations, sells into negative "
        "ones (Shiller 2017)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["scaling_factor"] = float(
            extras.get("scaling_factor", 5000.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 800.0)
        )
        self.state.custom_state["narrative_weight"] = float(
            extras.get("narrative_weight", 0.8)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        scaling = self.state.custom_state["scaling_factor"]
        max_qty = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        quantity = min(max_qty, abs(deviation) * scaling)
        if quantity <= 0:
            return hold
        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMNarrativeBeliever(CanonicalLLMPlayer):
    STRATEGY = "narrative-believer"
    DEFAULT_SYS_PROMPT = """\
You are a narrative-driven trader. You have a story about where price
should go, and you treat each move away from fundamental as evidence
about that story. Rising prices confirm the narrative — you buy in.
Falling prices refute it — you sell out. Your conviction (and position
size) scales with how far price has moved.

Output format:
<analysis>describe the deviation, whether it confirms or refutes your narrative, and the resulting conviction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide narrative-side: buy on confirming rises, sell on refuting falls,
hold when the deviation is inside the activation band.
"""


__all__ = ["RuleNarrativeBeliever", "LLMNarrativeBeliever"]
