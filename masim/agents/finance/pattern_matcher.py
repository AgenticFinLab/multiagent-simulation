"""pattern-matcher — Representativeness-heuristic pattern trader.

Canonical implementation of the ``pattern-matcher`` archetype documented
in ``masim/agents/defines/finance/pattern-matcher.md``. Interprets each
price deviation as representative of a persistent regime and trades in
its direction with size proportional to |deviation|.

Theoretical basis:
    Kahneman & Tversky (1972) — representativeness heuristic and base-rate
    neglect.
    Grether (1980) — descriptive tests of representativeness.
    De Bondt & Thaler (1985) — overreaction in stock returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation           = (price - fundamental) / fundamental
    effective_threshold = threshold_base / pattern_sensitivity

    If ``deviation > effective_threshold``:
        buy — quantity = ``min(quantity_cap, round(|deviation| * 5000))``.
    Elif ``deviation < -effective_threshold``:
        sell — quantity as above.
    Otherwise: hold.

    The profile's ``position_limit`` self-imposed cap is implicit: the base
    finaliser already clips buys to available cash and sells to available
    position, so runaway accumulation is bounded.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``pattern_sensitivity`` : float — sensitivity multiplier (default 1.0).
    * ``base_rate_ignore``    : float in [0,1] — recorded for persona
                                  parity (default 0.7).
    * ``position_limit``      : float — implicit cap (default 5000.0).
    * ``quantity_cap``        : float — per-tick max order (default 800.0).
    * ``threshold_base``      : float — base deviation threshold
                                  (default 0.02).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePatternMatcher(CanonicalRulePlayer):
    STRATEGY = "pattern-matcher"
    DISPLAY_NAME = "Pattern-Matching Representativeness Trader"
    SUMMARY = (
        "Interprets short deviations as representative of persistent regimes "
        "and trades pro-cyclically with size ∝ |deviation| "
        "(Kahneman & Tversky 1972; De Bondt & Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["pattern_sensitivity"] = float(
            extras.get("pattern_sensitivity", 1.0)
        )
        self.state.custom_state["base_rate_ignore"] = float(
            extras.get("base_rate_ignore", 0.7)
        )
        self.state.custom_state["position_limit"] = float(
            extras.get("position_limit", 5000.0)
        )
        self.state.custom_state["quantity_cap"] = float(
            extras.get("quantity_cap", 800.0)
        )
        self.state.custom_state["threshold_base"] = float(
            extras.get("threshold_base", 0.02)
        )
        # Perceived-signal-to-shares scaling (profile §Parameters: 5000).
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        sensitivity = self.state.custom_state["pattern_sensitivity"]
        cap = self.state.custom_state["quantity_cap"]
        base_th = self.state.custom_state["threshold_base"]
        q_scale = self.state.custom_state["quantity_scale"]
        position_limit = self.state.custom_state["position_limit"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if sensitivity <= 0:
            return hold
        effective_threshold = base_th / sensitivity

        if deviation > effective_threshold:
            # Suppress same-direction accumulation past the self-imposed cap.
            if state.position >= position_limit:
                return hold
            quantity = min(cap, float(round(abs(deviation) * q_scale)))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation < -effective_threshold:
            if state.position <= -position_limit:
                return hold
            quantity = min(cap, float(round(abs(deviation) * q_scale)))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMPatternMatcher(CanonicalLLMPlayer):
    STRATEGY = "pattern-matcher"
    DEFAULT_SYS_PROMPT = """\
You are a pattern-matching representativeness trader. You take short
price deviations at face value: a positive deviation is a signal that
prices will keep rising, a negative deviation that they will keep
falling. You do not adjust for mean reversion — you buy positive
deviations and sell negative ones immediately, with size scaling to
the magnitude of the deviation.

Output format:
<analysis>describe the deviation and the regime you infer from it.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Match the pattern: buy positive deviations, sell negative ones with size
proportional to |deviation|; hold inside the sensitivity-scaled band.
"""


__all__ = ["RulePatternMatcher", "LLMPatternMatcher"]
