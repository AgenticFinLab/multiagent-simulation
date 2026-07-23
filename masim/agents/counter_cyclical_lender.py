"""counter-cyclical-lender — Basel-III style counter-cyclical credit provider.

Canonical implementation of the ``counter-cyclical-lender`` archetype
documented in ``examples/AGENT_POOL/finance/counter-cyclical-lender.md``.
Uses an EMA trend of price as a credit-cycle proxy: extends credit (buys)
in busts (price below trend) and tightens (sells) in booms (price above
trend).

Theoretical basis:
    Borio (2014) — the financial cycle and macroprudential policy;
    Basel III counter-cyclical capital buffer (CCyB).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    trend_new  = (1 - smoothing_factor) * trend + smoothing_factor * price
    credit_gap = (price - trend_new) / trend_new

    If credit_gap < -gap_threshold:
        q = min(base_size * |credit_gap| * gap_scale, cash / price)   → buy
    Elif credit_gap > gap_threshold:
        q = min(base_size * credit_gap * gap_scale, position)          → sell
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``smoothing_factor`` : float — EMA weight for the trend
                             (default 0.10).
    * ``gap_threshold``    : float — minimum absolute credit gap to act
                             (default 0.03).
    * ``base_size``        : float — base credit quantity (default 600.0).
    * ``gap_scale``        : float — gap→quantity multiplier (default 8000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCounterCyclicalLender(CanonicalRulePlayer):
    STRATEGY = "counter-cyclical-lender"
    DISPLAY_NAME = "Counter-Cyclical Lender"
    SUMMARY = (
        "Extends credit in busts and tightens in booms via EMA credit-gap "
        "(Borio 2014; Basel III CCyB)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["smoothing_factor"] = float(
            extras.get("smoothing_factor", 0.10)
        )
        self.state.custom_state["gap_threshold"] = float(
            extras.get("gap_threshold", 0.03)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 600.0))
        self.state.custom_state["gap_scale"] = float(extras.get("gap_scale", 8000.0))
        self.state.custom_state["trend"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("trend") is None:
            self.state.custom_state["trend"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cs = self.state.custom_state
        alpha = cs["smoothing_factor"]
        trend = cs.get("trend") or state.price
        trend = (1.0 - alpha) * trend + alpha * state.price
        cs["trend"] = trend

        if trend <= 0 or state.price <= 0:
            return hold

        gap_threshold = cs["gap_threshold"]
        base_size = cs["base_size"]
        gap_scale = cs["gap_scale"]
        credit_gap = (state.price - trend) / trend

        if credit_gap < -gap_threshold:
            raw_q = base_size * abs(credit_gap) * gap_scale
            budget_q = state.cash / state.price if state.price > 0 else 0.0
            quantity = min(raw_q, budget_q)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if credit_gap > gap_threshold:
            raw_q = base_size * credit_gap * gap_scale
            quantity = min(raw_q, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMCounterCyclicalLender(CanonicalLLMPlayer):
    STRATEGY = "counter-cyclical-lender"
    DEFAULT_SYS_PROMPT = """\
You are a counter-cyclical lender following a Basel-III / macroprudential
mandate. You watch the price relative to a smoothed trend as a proxy for
the credit cycle: when price is meaningfully below trend (bust), you
extend credit; when price is meaningfully above trend (boom), you
tighten. Your goal is to lean against the cycle, not to chase it.

Output format:
<analysis>state the credit gap vs threshold and your policy stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Lean against the credit cycle: extend credit (buy) in busts, tighten
(sell) in booms, hold otherwise.
"""


__all__ = ["RuleCounterCyclicalLender", "LLMCounterCyclicalLender"]
