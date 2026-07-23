"""bayesian-updater — Bayesian rational trader with base-rate weighting.

Canonical implementation of the ``bayesian-updater`` archetype documented in
``examples/AGENT_POOL/finance/bayesian-updater.md``.

Theoretical basis:
    Grether (1980) — Bayesian benchmark for belief revision;
    Black (1986) — rational-trader corrective role.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation          = (price - fundamental) / fundamental
    adjusted_deviation = deviation * (1 - base_rate_weight)

    If ``adjusted_deviation > threshold``:  sell   (overvalued).
    If ``adjusted_deviation < -threshold``: buy    (undervalued).
    Otherwise: hold.

    quantity = min(quantity_cap, round(|deviation| * 3000 * evidence_weight))

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``base_rate_weight``  : float — prior weight (default 0.7).
    * ``evidence_weight``   : float — evidence gain (default 0.4).
    * ``threshold``         : float — activation gate (default 0.05).
    * ``quantity_cap``      : int  — per-tick cap (default 500).
    * ``sizing_gain``       : float — deviation -> qty gain (default 3000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBayesianUpdater(CanonicalRulePlayer):
    STRATEGY = "bayesian-updater"
    DISPLAY_NAME = "Bayesian Rational Trader"
    SUMMARY = (
        "Rational Bayesian trader who discounts the observed deviation by "
        "base-rate mean reversion (Grether 1980; Black 1986)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["base_rate_weight"] = float(
            extras.get("base_rate_weight", 0.7)
        )
        self.state.custom_state["evidence_weight"] = float(
            extras.get("evidence_weight", 0.4)
        )
        self.state.custom_state["threshold"] = float(
            extras.get("threshold", 0.05)
        )
        self.state.custom_state["quantity_cap"] = int(
            extras.get("quantity_cap", 500)
        )
        self.state.custom_state["sizing_gain"] = float(
            extras.get("sizing_gain", 3000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        base_rate = self.state.custom_state["base_rate_weight"]
        evidence = self.state.custom_state["evidence_weight"]
        threshold = self.state.custom_state["threshold"]
        cap = self.state.custom_state["quantity_cap"]
        gain = self.state.custom_state["sizing_gain"]

        adjusted = deviation * (1.0 - base_rate)

        if adjusted > threshold:
            factory = InvestorOrder.sell
        elif adjusted < -threshold:
            factory = InvestorOrder.buy
        else:
            return hold

        raw_qty = round(abs(deviation) * gain * evidence)
        quantity = min(cap, int(raw_qty))
        if quantity <= 0:
            return hold
        return factory(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBayesianUpdater(CanonicalLLMPlayer):
    STRATEGY = "bayesian-updater"
    DEFAULT_SYS_PROMPT = """\
You are a Bayesian rational trader. You discount the observed price
deviation by the base rate of mean reversion, so you trade only when
the adjusted deviation exceeds your threshold. Direction is contrarian
to the mispricing; size scales with evidence-weighted |deviation|
subject to a per-tick cap.

Output format:
<analysis>state deviation, adjusted deviation, and direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Discount deviation by the base rate; if adjusted deviation clears the
threshold, trade contrarian.
"""


__all__ = ["RuleBayesianUpdater", "LLMBayesianUpdater"]
