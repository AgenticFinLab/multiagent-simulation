"""momentum-retail — Late-arriving FOMO retail buyer.

Canonical implementation of the ``momentum-retail`` archetype documented
in ``examples/AGENT_POOL/finance/momentum-retail.md``. Sits out until the
deviation from fundamental exceeds a FOMO threshold, then buys a small
capped quantity per round — never sells.

Theoretical basis:
    Barber, Huang, Odean & Schwarz (2022) — attention-induced trading
    (Robinhood users).
    Lyocsa, Baumohl & Vyrost (2022) — YOLO trading and late arrivals
    during GameStop.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``price <= 0`` or fundamental invalid: hold.
    If ``deviation <= fomo_threshold``: hold.
    Else:
        affordable = int(cash / price)
        qty = min(max_buy, affordable)
        emit buy(qty) at price if qty > 0, else hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``fomo_threshold`` : float — minimum |deviation| to activate FOMO
                            entry (default 0.05).
    * ``max_buy``        : int   — per-round buy cap (default 50).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumRetail(CanonicalRulePlayer):
    STRATEGY = "momentum-retail"
    DISPLAY_NAME = "Late-Arriving FOMO Retail Buyer"
    SUMMARY = (
        "Enters late in a squeeze once visible momentum crosses the FOMO "
        "threshold; buy-only (Barber et al. 2022; Lyocsa et al. 2022)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["fomo_threshold"] = float(
            extras.get("fomo_threshold", 0.05)
        )
        self.state.custom_state["max_buy"] = int(extras.get("max_buy", 50))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["fomo_threshold"]
        max_buy = self.state.custom_state["max_buy"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0:
            return hold
        fundamental = state.fundamental
        if fundamental != fundamental or math.isnan(fundamental) or fundamental <= 0:
            return hold

        deviation = (state.price - fundamental) / fundamental
        if deviation <= threshold:
            return hold

        affordable = int(state.cash / state.price) if state.price > 0 else 0
        qty = min(max_buy, max(affordable, 0))
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMomentumRetail(CanonicalLLMPlayer):
    STRATEGY = "momentum-retail"
    DEFAULT_SYS_PROMPT = """\
You are a late-arriving retail momentum buyer. You sit on the sidelines
until you can see visible price momentum — a clear gap above fundamental —
and only then chase in with a small buy. You never sell; once you own
shares you hold them regardless of what happens next. Small deviations
inside your FOMO threshold do not qualify as visible momentum.

Output format:
<analysis>state the current deviation and whether the FOMO threshold is crossed.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as late-arrival FOMO retail: buy a small capped size when
deviation is clearly positive; never sell; hold otherwise.
"""


__all__ = ["RuleMomentumRetail", "LLMMomentumRetail"]
