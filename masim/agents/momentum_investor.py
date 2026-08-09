"""momentum-investor — Positive-feedback momentum trader.

Canonical implementation of the ``momentum-investor`` archetype documented
in ``masim/agents/defines/finance/momentum-investor.md``. Trades on the
single-round return with a Shiller-style positive-feedback bid-price
shift; order size scales with return magnitude and cash.

Theoretical basis:
    Shiller (1984) — positive-feedback trading and excess volatility.
    Jegadeesh & Titman (1993) — momentum returns.
    De Long, Shleifer, Summers & Waldmann (1990) — noise-trader
    positive feedback.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    r        = (price - prev_price) / prev_price
    bid_price = price * (1 + lambda_price * r)
    raw_qty  = beta * r * cash / bid_price
    quantity = clip(round(raw_qty), -qty_cap, +qty_cap)

    action = "buy" if quantity > 0 else "sell" if quantity < 0 else "hold".
    Cold-start (no prev_price): hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lambda_price``  : float — bid-price feedback intensity (default 0.5).
    * ``beta``          : float — cash-commitment sensitivity (default 0.3).
    * ``qty_cap``       : int   — per-round |quantity| cap (default 50).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumInvestor(CanonicalRulePlayer):
    STRATEGY = "momentum-investor"
    DISPLAY_NAME = "Positive-Feedback Momentum Investor"
    SUMMARY = (
        "Shiller-style positive-feedback trader with return-scaled bid "
        "and clipped quantity (Shiller 1984; Jegadeesh-Titman 1993)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lambda_price"] = float(
            extras.get("lambda_price", 0.5)
        )
        self.state.custom_state["beta"] = float(extras.get("beta", 0.3))
        self.state.custom_state["qty_cap"] = int(extras.get("qty_cap", 50))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        lam = self.state.custom_state["lambda_price"]
        beta = self.state.custom_state["beta"]
        qty_cap = self.state.custom_state["qty_cap"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.prev_price is None or state.prev_price <= 0:
            return hold

        r = (state.price - state.prev_price) / state.prev_price
        bid_price = state.price * (1.0 + lam * r)
        if bid_price <= 0:
            return hold

        raw_qty = beta * r * state.cash / bid_price
        # Round then clip to [-qty_cap, +qty_cap].
        clipped = max(-qty_cap, min(qty_cap, int(round(raw_qty))))
        if clipped == 0:
            return hold
        if clipped > 0:
            return InvestorOrder.buy(
                quantity=float(clipped),
                price=bid_price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return InvestorOrder.sell(
            quantity=float(-clipped),
            price=bid_price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMomentumInvestor(CanonicalLLMPlayer):
    STRATEGY = "momentum-investor"
    DEFAULT_SYS_PROMPT = """\
You are a positive-feedback momentum investor. You buy when the last
period's return is positive and sell when it is negative; the size of your
order scales with the magnitude of the return and your available cash.
Your bid is shifted from the market price in the direction of the return
(higher bid when rising, lower when falling). No fundamental analysis, no
counter-trend trades — pure positive feedback.

Output format:
<analysis>state the last-period return and your resulting order.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a positive-feedback momentum investor: chase the sign of the
last-period return, size proportional to |return|.
"""


__all__ = ["RuleMomentumInvestor", "LLMMomentumInvestor"]
