"""risk-neutral-investor — Kelly-fraction expected-return investor.

Canonical implementation of the ``risk-neutral-investor`` archetype
documented in ``examples/AGENT_POOL/finance/risk-neutral-investor.md``.
Trades in proportion to the expected return relative to a perceived fair
value, sized as a fraction of the growth-optimal Kelly bet.

Theoretical basis:
    Kelly (1956) — A New Interpretation of Information Rate.
    Thorp (2006) — Half-Kelly practical betting.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    expected_return = (fair_value - price) / price

    IF expected_return > edge_threshold:
        q_buy  = min(cash / price,
                     kelly_fraction * (cash / price) * (expected_return / edge_scale))
    ELIF expected_return < -edge_threshold:
        q_sell = min(position,
                     kelly_fraction * position * (|expected_return| / edge_scale))
    ELSE: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``edge_threshold`` : float (default 0.01) — minimum |expected_return|.
    * ``kelly_fraction`` : float in (0, 1] (default 0.50) — half-Kelly.
    * ``edge_scale``     : float > 0 (default 0.05) — edge→size normaliser.
    * ``fair_value``     : float > 0 (default 100.0) — perceived fair value.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRiskNeutralInvestor(CanonicalRulePlayer):
    STRATEGY = "risk-neutral-investor"
    DISPLAY_NAME = "Risk-Neutral Expected-Return Investor"
    SUMMARY = (
        "Risk-neutral trader sizing in proportion to expected return via a "
        "fractional-Kelly rule (Kelly 1956; Thorp 2006)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["edge_threshold"] = float(
            extras.get("edge_threshold", 0.01)
        )
        self.state.custom_state["kelly_fraction"] = float(
            extras.get("kelly_fraction", 0.50)
        )
        self.state.custom_state["edge_scale"] = float(
            extras.get("edge_scale", 0.05)
        )
        self.state.custom_state["fair_value"] = float(
            extras.get("fair_value", 100.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        expected_return = (cs["fair_value"] - state.price) / state.price
        edge_scale = cs["edge_scale"]
        if edge_scale <= 0:
            return hold

        if expected_return > cs["edge_threshold"]:
            base_shares = state.cash / state.price
            sized = cs["kelly_fraction"] * base_shares * (
                expected_return / edge_scale
            )
            quantity = min(base_shares, max(0.0, sized))
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if expected_return < -cs["edge_threshold"] and state.position > 0:
            sized = cs["kelly_fraction"] * state.position * (
                abs(expected_return) / edge_scale
            )
            quantity = min(state.position, max(0.0, sized))
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=float(quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRiskNeutralInvestor(CanonicalLLMPlayer):
    STRATEGY = "risk-neutral-investor"
    DEFAULT_SYS_PROMPT = """\
You are a risk-neutral investor sizing positions according to expected
return. You buy when price is meaningfully below your fair-value estimate
and sell when it is above. Order size scales linearly with the edge —
larger discounts trigger larger bets — but never exceeds a fractional-Kelly
cap on your available capital.

Output format:
<analysis>state your expected return and the resulting Kelly-fraction size.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade only when expected return exceeds your edge threshold; size the
order in proportion to the edge, capped at a fractional-Kelly bet.
"""


__all__ = ["RuleRiskNeutralInvestor", "LLMRiskNeutralInvestor"]
