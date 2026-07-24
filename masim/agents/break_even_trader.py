"""break-even-trader — Break-even loss-averse buy-the-dip trader.

Canonical implementation of the ``break-even-trader`` archetype documented in
``examples/AGENT_POOL/finance/break-even-trader.md``.

Theoretical basis:
    Barberis & Xiong (2009) — break-even effect and realization utility;
    Thaler & Johnson (1990) — house-money and break-even effects in
    sequential decisions.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Maintain entry_price seeded to the first-observed price.
    pnl_pct = (price - entry_price) / entry_price
    If pnl_pct < loss_threshold (a negative number):
        buy_qty = floor(|pnl_pct| * risk_increase_factor * sizing_gain)
    Otherwise: hold. (Buy-only.)

    On observed position increase (fill), weighted-average update:
        entry_price <- (entry_price * prev_pos + last_price * delta)
                       / new_pos.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``loss_threshold``       : float — trigger (default -0.05).
    * ``risk_increase_factor`` : float — sizing gain (default 2.0).
    * ``sizing_gain``          : float — final sizing multiplier
                                 (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBreakEvenTrader(CanonicalRulePlayer):
    STRATEGY = "break-even-trader"
    DISPLAY_NAME = "Break-Even Loss-Averse Trader"
    SUMMARY = (
        "Loss-averse trader who doubles down under water to reach "
        "break-even (Barberis & Xiong 2009; Thaler & Johnson 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["loss_threshold"] = float(
            extras.get("loss_threshold", -0.05)
        )
        self.state.custom_state["risk_increase_factor"] = float(
            extras.get("risk_increase_factor", 2.0)
        )
        self.state.custom_state["sizing_gain"] = float(
            extras.get("sizing_gain", 5000.0)
        )
        self.state.custom_state["entry_price"] = None
        self.state.custom_state["_last_position"] = float(
            self.state.custom_state.get("position", 0.0)
        )
        self.state.custom_state["_last_broadcast_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        price = float(market_data["price"])

        cur_pos = float(cs.get("position", 0.0))
        last_pos = float(cs.get("_last_position", 0.0))
        last_price = cs.get("_last_broadcast_price")

        # Fill detection: position grew since the previous broadcast.
        if (
            last_price is not None
            and cur_pos > last_pos
            and cur_pos > 0
        ):
            delta = cur_pos - last_pos
            entry = cs.get("entry_price")
            if entry is None or last_pos <= 0:
                cs["entry_price"] = float(last_price)
            else:
                cs["entry_price"] = (
                    entry * last_pos + float(last_price) * delta
                ) / cur_pos

        # Cold-start seeding: no entry_price yet -> use first observed price.
        if cs.get("entry_price") is None:
            cs["entry_price"] = price

        cs["_last_position"] = cur_pos
        cs["_last_broadcast_price"] = price

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        entry = self.state.custom_state.get("entry_price")
        if entry is None or entry <= 0:
            return hold

        pnl_pct = (state.price - entry) / entry
        loss_thresh = self.state.custom_state["loss_threshold"]
        if pnl_pct >= loss_thresh:
            return hold

        risk = self.state.custom_state["risk_increase_factor"]
        gain = self.state.custom_state["sizing_gain"]
        quantity = math.floor(abs(pnl_pct) * risk * gain)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBreakEvenTrader(CanonicalLLMPlayer):
    STRATEGY = "break-even-trader"
    DEFAULT_SYS_PROMPT = """\
You are a loss-averse retail trader driven by the break-even effect.
When your position falls below your entry price by more than a small
threshold, you increase your risk by buying more to try to reach
break-even faster. You never sell at a loss; you only add. When you
are up or flat you hold.

Output format:
<analysis>state pnl_pct vs loss threshold and additional buy size.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If you are meaningfully under water on your entry, buy more to chase
break-even; otherwise hold.
"""


__all__ = ["RuleBreakEvenTrader", "LLMBreakEvenTrader"]
