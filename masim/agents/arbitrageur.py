"""arbitrageur — Classic convergence arbitrageur.

Canonical implementation of the ``arbitrageur`` archetype documented in
``examples/AGENT_POOL/finance/arbitrageur.md``.

Theoretical basis:
    Shleifer & Vishny (1997) — limits of arbitrage; classical
    convergence-trading role of arbitrageurs (Grossman & Stiglitz 1980).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``|deviation| > activation_threshold``:
        qty = min(max_order, int(|deviation| * quantity_scale))
        deviation > 0 -> sell   (overvalued)
        deviation < 0 -> buy    (undervalued)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — trigger (default 0.05).
    * ``quantity_scale``       : float — deviation -> qty gain
                                  (default 3000.0).
    * ``max_order``            : int  — per-tick cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleArbitrageur(CanonicalRulePlayer):
    STRATEGY = "arbitrageur"
    DISPLAY_NAME = "Convergence Arbitrageur"
    SUMMARY = (
        "Convergence arbitrageur trading contrarian to broadcast deviation "
        "(Shleifer & Vishny 1997; Grossman & Stiglitz 1980)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.05)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["max_order"] = int(
            extras.get("max_order", 500)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["activation_threshold"]
        if abs(deviation) <= threshold:
            return hold

        scale = self.state.custom_state["quantity_scale"]
        cap = self.state.custom_state["max_order"]
        raw_qty = int(abs(deviation) * scale)
        quantity = min(cap, raw_qty)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMArbitrageur(CanonicalLLMPlayer):
    STRATEGY = "arbitrageur"
    DEFAULT_SYS_PROMPT = """\
You are a convergence arbitrageur. You take contrarian positions when
price diverges materially from fundamental value: buying when
undervalued, selling when overvalued. You respect a per-tick order cap
and hold whenever deviation is inside the activation band.

Output format:
<analysis>compare deviation to activation threshold and pick direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Arbitrage the gap: buy if underpriced past the band, sell if overpriced
past the band, hold otherwise; scale by |deviation|.
"""


__all__ = ["RuleArbitrageur", "LLMArbitrageur"]
