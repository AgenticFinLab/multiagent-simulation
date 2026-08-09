"""central-bank-defender — Currency peg defender with reserve-floor exit.

Canonical implementation of the ``central-bank-defender`` archetype
documented in ``masim/agents/defines/finance/central-bank-defender.md``.
Defends a fixed peg by contrarian intervention scaled by deviation
magnitude, and capitulates when reserves fall below the credibility
floor (twin-crisis capitulation).

Theoretical basis:
    Krugman (1979) — a model of balance-of-payments crises;
    Obstfeld (1996) — self-fulfilling speculative attacks;
    Kaminsky & Reinhart (1999) — twin crises: reserves-and-currency.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    initial_reserves captured on first observation.
    IF cash < reserve_floor * initial_reserves: DEACTIVATED (hold forever).
    dev = price - peg_target
    IF |dev| > defense_threshold:
        q = defense_intensity * |dev| * sizing_scale
        SELL q if dev > 0 (defend against overshoot)
        BUY  q if dev < 0 (defend against undershoot)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``peg_target``          : float > 0 — the peg level (default 1.0).
    * ``defense_threshold``   : float > 0 — |P − peg| trigger
                                 (default 0.01).
    * ``defense_intensity``   : float > 0 — response coefficient
                                 (default 2.0).
    * ``sizing_scale``        : float > 0 — |dev| → qty scale
                                 (default 10000.0).
    * ``reserve_floor``       : float in [0, 1] — fraction of initial
                                 reserves below which the defender
                                 capitulates (default 0.10).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCentralBankDefender(CanonicalRulePlayer):
    STRATEGY = "central-bank-defender"
    DISPLAY_NAME = "Currency Peg Defender"
    SUMMARY = (
        "Defends a fixed peg with proportional counter-orders until "
        "reserves collapse below the credibility floor "
        "(Krugman 1979; Obstfeld 1996)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["peg_target"] = float(extras.get("peg_target", 1.0))
        self.state.custom_state["defense_threshold"] = float(
            extras.get("defense_threshold", 0.01)
        )
        self.state.custom_state["defense_intensity"] = float(
            extras.get("defense_intensity", 2.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 10000.0)
        )
        self.state.custom_state["reserve_floor"] = float(
            extras.get("reserve_floor", 0.10)
        )
        self.state.custom_state["initial_reserves"] = None
        self.state.custom_state["capitulated"] = False

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Capture the reserve baseline the first time we ever see market
        # data — before any intervention has burned through cash.
        if self.state.custom_state.get("initial_reserves") is None:
            self.state.custom_state["initial_reserves"] = float(
                self.state.custom_state["cash"]
            )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        initial = self.state.custom_state.get("initial_reserves")
        floor_frac = self.state.custom_state["reserve_floor"]
        if initial is None:
            # first tick: allow one round of observation
            return hold

        # Capitulation: once broken, stay broken.
        if self.state.custom_state["capitulated"]:
            return hold
        if state.cash < floor_frac * initial:
            self.state.custom_state["capitulated"] = True
            return hold

        peg = self.state.custom_state["peg_target"]
        theta = self.state.custom_state["defense_threshold"]
        intensity = self.state.custom_state["defense_intensity"]
        sizing = self.state.custom_state["sizing_scale"]

        dev = state.price - peg
        if abs(dev) <= theta:
            return hold

        qty = intensity * abs(dev) * sizing
        if qty <= 0:
            return hold
        if dev > 0:
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.buy(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMCentralBankDefender(CanonicalLLMPlayer):
    STRATEGY = "central-bank-defender"
    DEFAULT_SYS_PROMPT = """\
You are a central bank defending a currency peg. When the market price
overshoots the peg you sell to bring it back; when it undershoots you
buy. Response size scales with the size of the deviation. Once your
reserves fall below the credibility floor, you capitulate and stop
intervening (Krugman 1979; Obstfeld 1996).

Output format:
<analysis>state the peg, the deviation from peg, your remaining reserves, and whether you defend or capitulate.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f}. Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Defend the peg with a proportional counter-order when |price − peg|
exceeds the defense threshold; hold if you have already capitulated.
"""


__all__ = ["RuleCentralBankDefender", "LLMCentralBankDefender"]
