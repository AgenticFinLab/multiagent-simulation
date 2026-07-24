"""process-evaluator — Process-oriented contrarian evaluator.

Canonical implementation of the ``process-evaluator`` archetype
documented in ``examples/AGENT_POOL/finance/process-evaluator.md``.
The agent trades contrarian to observed deviations, scaled by the
process-vs-outcome weighting that Roese & Vohs (2012) invoke as a
hindsight-debiasing device.

Theoretical basis:
    Roese & Vohs (2012) — hindsight bias and debiasing via
    process-oriented evaluation.
    Fischhoff (1975) — knew-it-all-along effect.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``|deviation| > activation_threshold``:
        qty = min(max_order, int(|dev| * quantity_scale * process_weight
                                       * outcome_weight))
        direction = -sign(deviation)  (contrarian)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — no-trade band (default 0.05).
    * ``quantity_scale``       : float — dev→qty conversion (default 3000).
    * ``max_order``            : float — per-tick order cap (default 500).
    * ``process_weight``       : float — weight on process (default 0.8).
    * ``outcome_weight``       : float — weight on outcome (default 1.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleProcessEvaluator(CanonicalRulePlayer):
    STRATEGY = "process-evaluator"
    DISPLAY_NAME = "Process Evaluator"
    SUMMARY = (
        "Contrarian trader who scales sizing by process-vs-outcome weights "
        "(Roese & Vohs 2012 hindsight debiasing)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 500.0)
        )
        self.state.custom_state["process_weight"] = float(
            extras.get("process_weight", 0.8)
        )
        self.state.custom_state["outcome_weight"] = float(
            extras.get("outcome_weight", 1.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold

        theta = self.state.custom_state["activation_threshold"]
        qscale = self.state.custom_state["quantity_scale"]
        qmax = self.state.custom_state["max_order"]
        pw = self.state.custom_state["process_weight"]
        ow = self.state.custom_state["outcome_weight"]

        dev = state.deviation
        if abs(dev) <= theta:
            return hold

        raw_qty = abs(dev) * qscale * pw * ow
        quantity = min(qmax, float(int(raw_qty)))
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMProcessEvaluator(CanonicalLLMPlayer):
    STRATEGY = "process-evaluator"
    DEFAULT_SYS_PROMPT = """\
You are a process-oriented evaluator who resists hindsight bias. You
judge decisions by the quality of the process and the mispricing signal,
not by whichever way the crowd is moving. When price drifts far above
fundamental you sell; when it drifts far below you buy; you size the
trade by the mispricing magnitude filtered through process and outcome
weights.

Output format:
<analysis>state the deviation and your contrarian stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade contrarian to observable deviation, sized by the mispricing.
"""


__all__ = ["RuleProcessEvaluator", "LLMProcessEvaluator"]
