"""ideologue — Belief-persistent directional trader.

Canonical implementation of the ``ideologue`` archetype documented in
``examples/AGENT_POOL/finance/ideologue.md``. Trades in a fixed direction
determined by an ideological belief (bull or bear); intensity is scaled by
conviction and (optionally) decays each tick.

Theoretical basis:
    Nickerson (1998) — confirmation bias.
    Lord, Ross & Lepper (1979) — belief perseverance.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    Each tick, decrement belief_strength by belief_decay (floored at 0).

    If belief_direction == "bull":
        qty = min(cash / price, conviction_size * belief_strength)
        action = buy
    Elif belief_direction == "bear":
        qty = min(position, conviction_size * belief_strength)
        action = sell
    If resources exhausted -> hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``belief_direction`` : str in {"bull", "bear"} — fixed directional
                              belief (default "bull").
    * ``belief_strength``  : float in [0, 1] — conviction intensity
                              (default 0.8, Nickerson 1998).
    * ``conviction_size``  : float > 0 — base order size (default 400.0).
    * ``belief_decay``     : float >= 0 — per-tick decay in conviction
                              (default 0.0, Lord et al. 1979).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIdeologue(CanonicalRulePlayer):
    STRATEGY = "ideologue"
    DISPLAY_NAME = "Ideological Directional Trader"
    SUMMARY = (
        "Fixed bullish/bearish belief that persists regardless of market "
        "signals (Nickerson 1998; Lord, Ross & Lepper 1979)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        direction = str(extras.get("belief_direction", "bull")).lower()
        if direction not in {"bull", "bear"}:
            direction = "bull"
        self.state.custom_state["belief_direction"] = direction
        self.state.custom_state["belief_strength"] = float(
            extras.get("belief_strength", 0.8)
        )
        self.state.custom_state["conviction_size"] = float(
            extras.get("conviction_size", 400.0)
        )
        self.state.custom_state["belief_decay"] = float(
            extras.get("belief_decay", 0.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        direction = self.state.custom_state["belief_direction"]
        strength = self.state.custom_state["belief_strength"]
        conviction = self.state.custom_state["conviction_size"]
        decay = self.state.custom_state["belief_decay"]

        # Apply per-tick decay to belief strength (floored at 0).
        strength = max(0.0, strength - decay)
        self.state.custom_state["belief_strength"] = strength

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or strength <= 0:
            return hold

        desired = conviction * strength
        if direction == "bull":
            qty = min(state.cash / state.price, desired)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # bear
        qty = min(state.position, desired)
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIdeologue(CanonicalLLMPlayer):
    STRATEGY = "ideologue"
    DEFAULT_SYS_PROMPT = """\
You are an ideological trader. You hold a fixed directional view — bullish
or bearish — that will not be shaken by day-to-day price action. If
bullish, you buy persistently; if bearish, you sell persistently. You do
not fade your own view, you do not hedge, and you do not update on
disconfirming evidence. Order size scales with your current conviction.

Output format:
<analysis>state your ideological direction and current conviction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Act on your fixed belief: bulls buy, bears sell; hold only when resources
in your belief direction are exhausted.
"""


__all__ = ["RuleIdeologue", "LLMIdeologue"]
