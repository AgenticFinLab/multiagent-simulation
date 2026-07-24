"""leveraged-investor — Margin-call fire-sale investor.

Canonical implementation of the ``leveraged-investor`` archetype documented
in ``examples/AGENT_POOL/finance/leveraged-investor.md``. Fires a fixed
fraction of the position onto the market when the price deviation from
fundamental crosses a negative margin-call trigger.

Theoretical basis:
    Brunnermeier & Pedersen (2009) — Funding-liquidity spirals and
    threshold-based margin calls.
    Adrian & Shin (2010) — Geometric liquidation of leveraged balance
    sheets.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental
    breach    = (deviation < -margin_call_trigger)

    If breach and ``position > 0``:
        sell_qty = max(1, floor(position * fire_sale_fraction))
    Else: hold.

    The agent NEVER buys — position is monotonically non-increasing.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``margin_call_trigger``  : float > 0 — negative-deviation threshold
                                  (default 0.10, Brunnermeier & Pedersen 2009).
    * ``fire_sale_fraction``   : float in (0, 1] — fraction of position
                                  liquidated per breach (default 0.50,
                                  Adrian & Shin 2010).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLeveragedInvestor(CanonicalRulePlayer):
    STRATEGY = "leveraged-investor"
    DISPLAY_NAME = "Leveraged Fire-Sale Investor"
    SUMMARY = (
        "Levered balance sheet that fire-sells a fixed fraction of its "
        "position when the negative-deviation margin threshold is breached "
        "(Brunnermeier & Pedersen 2009; Adrian & Shin 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["margin_call_trigger"] = float(
            extras.get("margin_call_trigger", 0.10)
        )
        self.state.custom_state["fire_sale_fraction"] = float(
            extras.get("fire_sale_fraction", 0.50)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        trigger = self.state.custom_state["margin_call_trigger"]
        fraction = self.state.custom_state["fire_sale_fraction"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation):
            return hold
        breach = state.deviation < -trigger
        if not breach or state.position <= 0:
            return hold

        sell_qty = math.floor(state.position * fraction)
        if sell_qty <= 0 and state.position > 0:
            sell_qty = 1
        sell_qty = min(float(sell_qty), state.position)
        if sell_qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(sell_qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLeveragedInvestor(CanonicalLLMPlayer):
    STRATEGY = "leveraged-investor"
    DEFAULT_SYS_PROMPT = """\
You are a leveraged institutional investor. When the price drops far
enough below fundamental that your margin threshold is breached, your
prime broker forces you to fire-sell a fixed fraction of the position.
Otherwise you hold. You never buy.

Output format:
<analysis>state deviation vs the negative margin trigger and inventory.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Fire-sell a fixed fraction of the position if deviation is below
−margin_call_trigger and inventory remains; otherwise hold.
"""


__all__ = ["RuleLeveragedInvestor", "LLMLeveragedInvestor"]
