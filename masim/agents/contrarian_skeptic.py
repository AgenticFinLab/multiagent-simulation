"""contrarian-skeptic — Skepticism-scaled contrarian.

Canonical implementation of the ``contrarian-skeptic`` archetype
documented in ``examples/AGENT_POOL/finance/contrarian-skeptic.md``.
Trades opposite deviation with quantity scaled by a skepticism factor —
sells premium, buys discount.

Theoretical basis:
    De Bondt & Thaler (1985) — long-run reversal.
    Daniel, Hirshleifer & Subrahmanyam (1998) — investor psychology
    and security-market under- and overreactions.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    IF |deviation| > activation_threshold:
        qty = min(max_order, int(|deviation| * quantity_scale * skepticism_level))
        direction = -sign(deviation)   (dev > 0 → SELL, dev < 0 → BUY)
    ELSE:
        HOLD

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float > 0 — |deviation| trigger
                                   (default 0.05).
    * ``quantity_scale``       : float > 0 — |deviation| → qty scale
                                   (default 3000.0).
    * ``max_order``            : int > 0 — per-round order cap
                                   (default 500).
    * ``skepticism_level``     : float in [0, 1] — conviction multiplier
                                   (default 0.6).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContrarianSkeptic(CanonicalRulePlayer):
    STRATEGY = "contrarian-skeptic"
    DISPLAY_NAME = "Skeptical Contrarian"
    SUMMARY = (
        "Trades against deviation with skepticism-scaled sizing "
        "(De Bondt & Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["max_order"] = int(extras.get("max_order", 500))
        self.state.custom_state["skepticism_level"] = float(
            extras.get("skepticism_level", 0.6)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        theta = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        cap = self.state.custom_state["max_order"]
        skep = self.state.custom_state["skepticism_level"]

        dev = state.deviation
        if abs(dev) <= theta:
            return hold

        qty = min(cap, int(abs(dev) * scale * skep))
        if qty <= 0:
            return hold
        factory = InvestorOrder.sell if dev > 0 else InvestorOrder.buy
        return factory(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMContrarianSkeptic(CanonicalLLMPlayer):
    STRATEGY = "contrarian-skeptic"
    DEFAULT_SYS_PROMPT = """\
You are a skeptical contrarian. You do not fully trust market prices:
when they diverge from fundamental you trade against the divergence,
but your conviction is capped by a skepticism factor — you never bet
the farm on a mean-reversion (De Bondt & Thaler 1985).

Output format:
<analysis>state the deviation and your skepticism-scaled sized order.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade against deviation when |deviation| clears activation; size the
order by |deviation| × skepticism; hold otherwise.
"""


__all__ = ["RuleContrarianSkeptic", "LLMContrarianSkeptic"]
