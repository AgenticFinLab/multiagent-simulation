"""momentum-trader — Short-term momentum trader.

Canonical implementation of the ``momentum-trader`` archetype documented in
``examples/AGENT_POOL/finance/momentum-trader.md``. Chases recent price
trends and amplifies short-run moves — diverges from fundamental during
trending episodes.

Theoretical basis:
    Jegadeesh & Titman (1993) — return continuation on 3–12-month horizons.
    De Long, Shleifer, Summers & Waldmann (1990) — positive-feedback
    traders and rational speculation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    return_pct = (price - prev_price) / prev_price   (single-tick return)

    If ``return_pct > +threshold``: buy — chase the up-move.
    If ``return_pct < -threshold``: sell — chase the down-move.
    Otherwise: hold.

    Quantity = ``min(base_position_size, |return_pct| * sizing_scale)``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``threshold``           : float in [0, 1] — entry cut-off on the
                                 single-tick return (default 0.02).
    * ``base_position_size``  : float > 0 — order-size cap (default 20.0).
    * ``sizing_scale``        : float > 0 — return→quantity factor
                                 (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMomentumTrader(CanonicalRulePlayer):
    STRATEGY = "momentum-trader"
    DISPLAY_NAME = "Short-Term Momentum Trader"
    SUMMARY = (
        "Chases recent price trends and amplifies short-run moves "
        "(Jegadeesh & Titman 1993; De Long et al. 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.prev_price <= 0:
            return hold
        return_pct = (state.price - state.prev_price) / state.prev_price

        if abs(return_pct) <= threshold:
            return hold

        quantity = min(base, abs(return_pct) * sizing)
        factory = InvestorOrder.buy if return_pct > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMomentumTrader(CanonicalLLMPlayer):
    STRATEGY = "momentum-trader"
    DEFAULT_SYS_PROMPT = """\
You are a short-term momentum trader. Recent moves matter more than
long-run averages; you buy into rallies and sell into declines,
amplifying whatever short-term trend is in force. When the market is
flat you stand aside.

Output format:
<analysis>describe the recent price change and your momentum stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide by following the recent trend: buy on rallies, sell on declines,
hold when the market is flat.
"""


__all__ = ["RuleMomentumTrader", "LLMMomentumTrader"]
