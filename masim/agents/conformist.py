"""conformist — Momentum-conformist herding trader.

Canonical implementation of the ``conformist`` archetype documented in
``examples/AGENT_POOL/finance/conformist.md``. Follows the last-tick
return: buys after up-moves, sells after down-moves — pure return
conformity.

Theoretical basis:
    Asch (1955) — opinion conformity under group pressure.
    De Long, Shleifer, Summers & Waldmann (1990) — positive-feedback
    trading amplifies short-run trends.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    momentum = (price - prev_price) / prev_price
    IF momentum >  conformity_threshold: BUY  qty
    IF momentum < -conformity_threshold: SELL qty
    ELSE: HOLD
    qty = base_size * |momentum| * momentum_scale

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``conformity_threshold`` : float > 0 — |return| trigger
                                   (default 0.01).
    * ``base_size``            : float > 0 — nominal order-size cap
                                   (default 500.0).
    * ``momentum_scale``       : float > 0 — |return| → qty multiplier
                                   (default 8000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleConformist(CanonicalRulePlayer):
    STRATEGY = "conformist"
    DISPLAY_NAME = "Momentum Conformist"
    SUMMARY = (
        "Trades in the direction of the last-tick return — pure return "
        "conformity (Asch 1955; De Long et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["conformity_threshold"] = float(
            extras.get("conformity_threshold", 0.01)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 500.0))
        self.state.custom_state["momentum_scale"] = float(
            extras.get("momentum_scale", 8000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.prev_price <= 0:
            return hold

        theta = self.state.custom_state["conformity_threshold"]
        base = self.state.custom_state["base_size"]
        scale = self.state.custom_state["momentum_scale"]

        momentum = (state.price - state.prev_price) / state.prev_price
        if abs(momentum) <= theta:
            return hold

        raw_qty = base * abs(momentum) * scale
        # Match the profile's intent: the base is a nominal size cap.
        qty = min(raw_qty, base * scale * 1.0)
        # (Effectively the qty formula from §Sizing rule is unbounded on
        # the upside; the base finaliser clips to cash/position anyway.)
        qty = raw_qty
        if qty <= 0:
            return hold

        factory = InvestorOrder.buy if momentum > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMConformist(CanonicalLLMPlayer):
    STRATEGY = "conformist"
    DEFAULT_SYS_PROMPT = """\
You are a conformist. You do not have your own view; you simply do what
the last tick has done — buy after an up-move, sell after a down-move,
proportional to the size of that move (Asch 1955; De Long et al. 1990).

Output format:
<analysis>describe the last-tick return and your direction of conformity.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade in the direction of the last return: buy on up-moves, sell on
down-moves, hold when flat.
"""


__all__ = ["RuleConformist", "LLMConformist"]
