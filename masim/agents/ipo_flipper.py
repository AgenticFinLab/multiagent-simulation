"""ipo-flipper — Short-horizon IPO allocation flipper.

Canonical implementation of the ``ipo-flipper`` archetype documented in
``examples/AGENT_POOL/finance/ipo-flipper.md``. Receives an IPO allocation
at ``offer_price`` on the first tick of the IPO window and flips it out when
either a target return or a maximum-hold horizon is reached.

Theoretical basis:
    Ritter (1991) — Long-run underperformance of IPOs and first-day pops.
    Ljungqvist (2007) — IPO underpricing and short-horizon flipping.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``ipo_active == False``: hold.
    If ``ipo_active`` and ``position == 0`` and ``ticks_since_ipo == 0``:
        buy ``min(cash / offer_price, allocation_size)`` at market.
    If ``position > 0``:
        current_return = (price - offer_price) / offer_price
        If ``current_return >= flip_target_return``
           or ``ticks_since_ipo >= max_hold_ticks``
           or ``current_return <= stop_loss``: sell entire position.
    Otherwise: hold.

Scenario-specific fields consumed via ``state.raw`` (see
``REQUIRES_FEATURES``): ``offer_price``, ``ipo_active``, ``ticks_since_ipo``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``flip_target_return`` : float > 0 — return level triggering flip
                                (default 0.10, Ritter 1991).
    * ``max_hold_ticks``     : int   > 0 — ticks before forced exit
                                (default 3, Ljungqvist 2007).
    * ``allocation_size``    : float > 0 — IPO shares allocated
                                (default 500.0).
    * ``stop_loss``          : float — negative return triggering exit
                                (default -0.05).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIpoFlipper(CanonicalRulePlayer):
    STRATEGY = "ipo-flipper"
    DISPLAY_NAME = "IPO Flipper"
    SUMMARY = (
        "Short-horizon IPO allocation flipper — buys at offer, sells on "
        "target return or time limit (Ritter 1991; Ljungqvist 2007)."
    )
    REQUIRES_FEATURES: tuple = ("offer_price", "ipo_active", "ticks_since_ipo")

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["flip_target_return"] = float(
            extras.get("flip_target_return", 0.10)
        )
        self.state.custom_state["max_hold_ticks"] = int(
            extras.get("max_hold_ticks", 3)
        )
        self.state.custom_state["allocation_size"] = float(
            extras.get("allocation_size", 500.0)
        )
        self.state.custom_state["stop_loss"] = float(extras.get("stop_loss", -0.05))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target = self.state.custom_state["flip_target_return"]
        max_hold = self.state.custom_state["max_hold_ticks"]
        alloc = self.state.custom_state["allocation_size"]
        stop_loss = self.state.custom_state["stop_loss"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        offer_price = state.raw_require("offer_price", cast=float)
        ipo_active = state.raw_require("ipo_active", cast=bool)
        ticks_since_ipo = state.raw_require("ticks_since_ipo", cast=int)

        if not ipo_active:
            return hold

        # Fresh allocation on the first tick of the IPO event.
        if state.position <= 0 and ticks_since_ipo == 0:
            if offer_price <= 0 or state.cash <= 0:
                return hold
            quantity = min(state.cash / offer_price, alloc)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=offer_price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        # Manage the existing IPO position.
        if state.position > 0 and offer_price > 0:
            current_return = (state.price - offer_price) / offer_price
            if (
                current_return >= target
                or current_return <= stop_loss
                or ticks_since_ipo >= max_hold
            ):
                return InvestorOrder.sell(
                    quantity=state.position,
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )
        return hold


class LLMIpoFlipper(CanonicalLLMPlayer):
    STRATEGY = "ipo-flipper"
    DEFAULT_SYS_PROMPT = """\
You are an IPO flipper. You receive an allocation at the offer price on
day one and dump it into the first-day pop as soon as a target return is
hit or your maximum-hold window elapses. You have no attachment to the
stock — you are a mechanical short-horizon profit-taker.

Output format:
<analysis>state whether the flip target or time limit has been reached.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy at the IPO on the first tick of the allocation window; sell the whole
position once the flip-target return, stop-loss, or max-hold horizon is
reached. Hold otherwise.
"""


__all__ = ["RuleIpoFlipper", "LLMIpoFlipper"]
