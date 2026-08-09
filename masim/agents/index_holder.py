"""index-holder — Buy-and-hold passive index holder.

Canonical implementation of the ``index-holder`` archetype documented in
``masim/agents/defines/finance/index-holder.md``. Establishes a target long
inventory at initialization and adds via scheduled contributions; never
sells and never reacts to price.

Theoretical basis:
    Passive Portfolio Theorem (Sharpe 1964; Malkiel 1973).
    Gabaix & Koijen (2021) — inelastic markets hypothesis: passive holders
    generate inelastic demand and shrink effective free-float.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If round == 0 and position < initial_target:
        buy min(initial_target - position, cash / price).
    Elif round > 0 and contribution_rate > 0
         and round % contribution_interval == 0:
        buy min(contribution_rate, cash / price).
    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``initial_target``        : float — target long inventory at start
                                   (default 50.0, from profile
                                   ``initial_position``).
    * ``contribution_rate``     : float — shares purchased per contribution
                                   tick (default 0.0).
    * ``contribution_interval`` : int   — rounds between contributions
                                   (default 20).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndexHolder(CanonicalRulePlayer):
    STRATEGY = "index-holder"
    DISPLAY_NAME = "Passive Index Holder"
    SUMMARY = (
        "Buy-and-hold passive index holder that establishes a target "
        "inventory and adds via scheduled contributions (Gabaix & Koijen "
        "2021 inelastic markets)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        # ``initial_target`` is the *target long inventory the passive
        # holder wants to build*; the engine-managed ``state.position``
        # tracks its actual holdings.
        self.state.custom_state["initial_target"] = float(
            extras.get("initial_target", extras.get("initial_position", 50.0))
        )
        self.state.custom_state["contribution_rate"] = float(
            extras.get("contribution_rate", 0.0)
        )
        self.state.custom_state["contribution_interval"] = int(
            extras.get("contribution_interval", 20)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        target = self.state.custom_state["initial_target"]
        rate = self.state.custom_state["contribution_rate"]
        interval = self.state.custom_state["contribution_interval"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold

        buy_qty = 0.0
        if state.round == 0 and state.position < target:
            buy_qty = min(target - state.position, state.cash / state.price)
        elif (
            state.round > 0
            and rate > 0
            and interval > 0
            and state.round % interval == 0
        ):
            buy_qty = min(rate, state.cash / state.price)

        if buy_qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(buy_qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIndexHolder(CanonicalLLMPlayer):
    STRATEGY = "index-holder"
    DEFAULT_SYS_PROMPT = """\
You are a passive buy-and-hold index holder. You build a fixed target
inventory at inception and add to it via scheduled cash contributions.
You never sell — not on drawdowns, not on rallies, not on any market
signal — and you do not attempt to time entries. Between contribution
ticks you simply hold.

Output format:
<analysis>state whether this is an initialization or contribution round.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Buy toward your target on round 0 or on scheduled contribution ticks;
otherwise hold. Never sell.
"""


__all__ = ["RuleIndexHolder", "LLMIndexHolder"]
