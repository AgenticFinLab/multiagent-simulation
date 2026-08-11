"""pro-cyclical-lender — Procyclical lending / credit-cycle amplifier.

Canonical implementation of the ``pro-cyclical-lender`` archetype
documented in ``masim/agents/defines/finance/pro-cyclical-lender.md``.
The agent expands lending (buys) in expansions and contracts lending
(sells) in downturns, amplifying the underlying cycle.

Theoretical basis:
    Adrian & Shin (2010) — liquidity and leverage: financial-sector
    leverage moves procyclically with asset prices.
    Minsky (1986) — endogenous credit cycle: stability breeds instability.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    C = cycle_indicator  (scenario broadcast)

    If ``C > expansion_threshold`` AND cash > 0:
        buy = lending_rate * cash / price * min(C/expansion_threshold,
                                                 cycle_sensitivity).
    If ``C < -contraction_threshold`` AND position > 0:
        sell = contraction_rate * position * min(|C|/contraction_threshold,
                                                  cycle_sensitivity).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``expansion_threshold``   : float — cycle level at which lending
                                   expands (default 0.10, Adrian & Shin
                                   2010).
    * ``contraction_threshold`` : float — cycle level at which lending
                                   contracts (default 0.10).
    * ``lending_rate``          : float — expansion trade fraction
                                   (default 0.10).
    * ``contraction_rate``      : float — contraction trade fraction
                                   (default 0.15).
    * ``cycle_sensitivity``     : float — cap on the cycle multiplier
                                   (default 2.0).

``cycle_indicator`` is read from ``state.raw``.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleProCyclicalLender(CanonicalRulePlayer):
    STRATEGY = "pro-cyclical-lender"
    DISPLAY_NAME = "Procyclical Lender"
    SUMMARY = (
        "Expands credit in booms, contracts in busts — amplifies the "
        "financial cycle (Adrian & Shin 2010; Minsky 1986)."
    )
    REQUIRES_FEATURES: tuple = ("cycle_indicator",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["expansion_threshold"] = float(
            extras.get("expansion_threshold", 0.10)
        )
        self.state.custom_state["contraction_threshold"] = float(
            extras.get("contraction_threshold", 0.10)
        )
        self.state.custom_state["lending_rate"] = float(
            extras.get("lending_rate", 0.10)
        )
        self.state.custom_state["contraction_rate"] = float(
            extras.get("contraction_rate", 0.15)
        )
        self.state.custom_state["cycle_sensitivity"] = float(
            extras.get("cycle_sensitivity", 2.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        C = state.raw_require("cycle_indicator", cast=float)
        exp_t = self.state.custom_state["expansion_threshold"]
        con_t = self.state.custom_state["contraction_threshold"]
        lr = self.state.custom_state["lending_rate"]
        cr = self.state.custom_state["contraction_rate"]
        cs = self.state.custom_state["cycle_sensitivity"]

        if C > exp_t and state.cash > 0:
            multiplier = min(C / exp_t, cs)
            quantity = lr * (state.cash / state.price) * multiplier
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if C < -con_t and state.position > 0:
            multiplier = min(abs(C) / con_t, cs)
            quantity = cr * state.position * multiplier
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMProCyclicalLender(CanonicalLLMPlayer):
    STRATEGY = "pro-cyclical-lender"
    DEFAULT_SYS_PROMPT = """\
You are a procyclical lender (bank / broker). In credit expansions you
extend more balance-sheet capacity, buying more assets; in contractions
you pull credit and sell into weakness. You amplify whatever regime the
cycle indicator says you are in; you do not act as a counter-cyclical
stabiliser.

Output format:
<analysis>state cycle regime and your lending stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Follow the cycle: buy in expansions, sell in contractions.
"""


__all__ = ["RuleProCyclicalLender", "LLMProCyclicalLender"]
