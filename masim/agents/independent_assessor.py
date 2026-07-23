"""independent-assessor — Statistically-literate contrarian.

Canonical implementation of the ``independent-assessor`` archetype
documented in ``examples/AGENT_POOL/finance/independent-assessor.md``.
Treats successive price changes as independent draws — buys undervalued
assets and sells overvalued ones. Higher threshold and lower cap than the
biased-momentum siblings, reflecting real-world limits to arbitrage.

Theoretical basis:
    Rabin (2002) — inference from small samples / rational assessment.
    De Bondt & Thaler (1985) — contrarian mean-reversion strategies.
    Shleifer & Vishny (1997) — limits to arbitrage.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= activation_threshold: hold.
    Else:
        qty = min(max_order, int(|deviation| * quantity_scale))
        deviation < 0 -> buy   (undervalued -> mean-revert)
        deviation > 0 -> sell  (overvalued  -> mean-revert)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — |deviation| trigger (default 0.05).
    * ``quantity_scale``       : float — deviation->qty scaling (default 3000).
    * ``max_order``            : float — per-round order cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndependentAssessor(CanonicalRulePlayer):
    STRATEGY = "independent-assessor"
    DISPLAY_NAME = "Independent Statistical Assessor"
    SUMMARY = (
        "Contrarian, statistically-literate arbitrageur that fades price "
        "deviations from fundamental (Rabin 2002; De Bondt & Thaler 1985; "
        "Shleifer & Vishny 1997)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["max_order"] = float(extras.get("max_order", 500.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        max_order = self.state.custom_state["max_order"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        qty = float(min(max_order, int(abs(deviation) * scale)))
        if qty <= 0:
            return hold

        # CONTRARIAN direction.
        factory = InvestorOrder.buy if deviation < 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIndependentAssessor(CanonicalLLMPlayer):
    STRATEGY = "independent-assessor"
    DEFAULT_SYS_PROMPT = """\
You are a statistically-literate independent assessor. You treat every
price tick as an independent draw — no hot hand, no gambler's fallacy —
and you interpret sustained deviations from fundamental as mispricings to
be faded rather than trends to be chased. You buy when price is well
below fundamental, sell when well above, and stay flat inside your
no-trade band because arbitrage is not free.

Output format:
<analysis>state the deviation and why you are fading (not chasing) it.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Fade the mispricing: buy when undervalued, sell when overvalued, hold
inside the no-trade band.
"""


__all__ = ["RuleIndependentAssessor", "LLMIndependentAssessor"]
