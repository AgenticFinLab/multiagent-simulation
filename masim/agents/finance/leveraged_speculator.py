"""leveraged-speculator — Aggressive leveraged directional speculator.

Canonical implementation of the ``leveraged-speculator`` archetype documented
in ``masim/agents/defines/finance/leveraged-speculator.md``. Trades a
directional signal at extreme leverage and is force-liquidated once the
margin utilisation crosses the margin-call level.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Funding-liquidity spirals and margin
    calls.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``margin_used > margin_call_level``:
        liquidate |position|             (forced sell)
    Else:
        signal ∈ ℝ
        If ``|signal| <= entry_threshold``: hold.
        If ``signal > +entry_threshold``: buy  min(leverage * base_size,
                                                  max_position - position)
        If ``signal < -entry_threshold``: sell min(leverage * base_size,
                                                  position)

Scenario-specific fields consumed via ``state.raw`` (see
``REQUIRES_FEATURES``): ``signal`` (directional trigger) and ``margin_used``
(current margin utilisation fraction).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``leverage``           : float > 1 (default 12.0, Brunnermeier &
                                Pedersen 2009).
    * ``base_size``          : float > 0 (default 500.0).
    * ``entry_threshold``    : float > 0 (default 0.01).
    * ``margin_call_level``  : float in (0, 1) (default 0.85).
    * ``max_position``       : float > 0 (default 10000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedSpeculator(CanonicalRulePlayer):
    STRATEGY = "leveraged-speculator"
    DISPLAY_NAME = "Leveraged Directional Speculator"
    SUMMARY = (
        "Extreme-leverage directional speculator; force-liquidates when "
        "margin utilisation crosses the call level (Brunnermeier & "
        "Pedersen 2009)."
    )
    # ``signal`` and ``margin_used`` are scenario-specific fields read via
    # state.raw — the scenario feature registry must expose them for this
    # archetype to activate meaningfully.
    REQUIRES_FEATURES: tuple = ("signal", "margin_used")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["leverage"] = float(extras.get("leverage", 12.0))
        self.state.custom_state["base_size"] = float(extras.get("base_size", 500.0))
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.01)
        )
        self.state.custom_state["margin_call_level"] = float(
            extras.get("margin_call_level", 0.85)
        )
        self.state.custom_state["max_position"] = float(
            extras.get("max_position", 10000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        leverage = self.state.custom_state["leverage"]
        base = self.state.custom_state["base_size"]
        threshold = self.state.custom_state["entry_threshold"]
        call_level = self.state.custom_state["margin_call_level"]
        max_pos = self.state.custom_state["max_position"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        margin_used = state.raw_require("margin_used", cast=float)
        signal = state.raw_require("signal", cast=float)

        # Margin call takes priority over the entry signal.
        if margin_used > call_level and state.position > 0:
            return InvestorOrder.sell(
                quantity=state.position,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        if abs(signal) <= threshold:
            return hold

        base_qty = leverage * base
        if signal > threshold:
            headroom = max(max_pos - state.position, 0.0)
            qty = min(base_qty, headroom)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # signal < -threshold
        qty = min(base_qty, max(state.position, 0.0))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLeveragedSpeculator(CanonicalLLMPlayer):
    STRATEGY = "leveraged-speculator"
    DEFAULT_SYS_PROMPT = """\
You are an aggressive leveraged speculator. You trade a directional
signal at extreme leverage — doubling down when the signal is with you
and unwinding when it flips. If your margin utilisation crosses the
margin-call level you are force-liquidated regardless of view.

Output format:
<analysis>report margin utilisation and the directional signal.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Force-liquidate on margin-call breach; otherwise leveraged-trade the
signal when |signal| exceeds the entry threshold; hold otherwise.
"""


__all__ = ["RuleLeveragedSpeculator", "LLMLeveragedSpeculator"]
