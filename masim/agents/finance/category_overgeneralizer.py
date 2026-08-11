"""category-overgeneralizer — Representativeness-heuristic regime classifier.

Canonical implementation of the ``category-overgeneralizer`` archetype
documented in ``masim/agents/defines/finance/category-overgeneralizer.md``.
Assigns a regime category to the market from a single deviation
observation and commits full conviction — the representativeness
heuristic with insensitivity to sample size.

Theoretical basis:
    Tversky & Kahneman (1974) — representativeness heuristic and
    insensitivity to sample size.
    Rabin (2002) — inference by believers in the law of small numbers.
    Barberis, Shleifer & Vishny (1998) — investor sentiment and regime
    over-classification.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation           = (price - fundamental) / fundamental
    effective_threshold = threshold_base / category_weight
    IF  deviation >  effective_threshold: buy  qty = min(cap, round(|dev|*5000))
    IF  deviation < -effective_threshold: sell qty = min(cap, round(|dev|*5000))
    ELSE: hold
    Position cap: |position| <= position_limit.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``category_weight`` : float > 0 — categorization strength; lowers
                             threshold (default 1.2).
    * ``sample_bias``     : float in [0, 1] — degree of sample-size
                             insensitivity, retained for documentation
                             parity (default 0.7).
    * ``position_limit``  : int > 0 — |position| cap (default 5000).
    * ``quantity_cap``    : int > 0 — per-tick order-size cap (default 800).
    * ``threshold_base``  : float > 0 — base deviation threshold
                             (default 0.02).
    * ``sizing_scale``    : float > 0 — |deviation| → qty scale
                             (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCategoryOvergeneralizer(CanonicalRulePlayer):
    STRATEGY = "category-overgeneralizer"
    DISPLAY_NAME = "Representativeness Regime Classifier"
    SUMMARY = (
        "Assigns a bull/bear regime from a single deviation observation "
        "and commits full conviction "
        "(Tversky & Kahneman 1974; Barberis, Shleifer & Vishny 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["category_weight"] = float(
            extras.get("category_weight", 1.2)
        )
        self.state.custom_state["sample_bias"] = float(
            extras.get("sample_bias", 0.7)
        )
        self.state.custom_state["position_limit"] = int(
            extras.get("position_limit", 5000)
        )
        self.state.custom_state["quantity_cap"] = int(
            extras.get("quantity_cap", 800)
        )
        self.state.custom_state["threshold_base"] = float(
            extras.get("threshold_base", 0.02)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        cat_w = self.state.custom_state["category_weight"]
        base = self.state.custom_state["threshold_base"]
        cap = self.state.custom_state["quantity_cap"]
        pos_lim = self.state.custom_state["position_limit"]
        sizing = self.state.custom_state["sizing_scale"]
        if cat_w <= 0:
            return hold
        eff_threshold = base / cat_w
        dev = state.deviation

        if dev > eff_threshold:
            if state.position >= pos_lim:
                return hold
            qty = min(cap, round(abs(dev) * sizing))
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if dev < -eff_threshold:
            if state.position <= -pos_lim:
                return hold
            qty = min(cap, round(abs(dev) * sizing))
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCategoryOvergeneralizer(CanonicalLLMPlayer):
    STRATEGY = "category-overgeneralizer"
    DEFAULT_SYS_PROMPT = """\
You are an over-categorizer. From a single deviation observation you
already declare a regime (bull if premium, bear if discount) and trade
the full implication of that category — treating one data point as
representative of the entire distribution
(Tversky & Kahneman 1974; Barberis, Shleifer & Vishny 1998).

Output format:
<analysis>state the deviation, the implied regime, and your conviction sizing.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Assign a regime from the current deviation and trade its full
implication — buy the bull regime, sell the bear regime, hold otherwise.
"""


__all__ = ["RuleCategoryOvergeneralizer", "LLMCategoryOvergeneralizer"]
