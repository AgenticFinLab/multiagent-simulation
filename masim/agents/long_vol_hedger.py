"""long-vol-hedger — Long-volatility crash hedger.

Canonical implementation of the ``long-vol-hedger`` archetype documented in
``examples/AGENT_POOL/finance/long-vol-hedger.md``. Buys cheap convexity
when the market has crashed below fundamental and rolls it off after a
sharp recovery.

Theoretical basis:
    Bakshi & Kapadia (2003) — negative variance risk premium.
    Coval & Shumway (2001) — expected option returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``deviation < -crash_threshold``: buy long-vol exposure sized as
        ``min(max_order, hedge_ratio * cash / price)``.
    If ``deviation > recovery_threshold`` and ``position > 0``: sell
        ``min(max_order, position)`` — roll off the hedge.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``hedge_ratio``        : float — fraction of cash committed per
                                buy signal (default 0.10).
    * ``crash_threshold``    : float — deviation below which we buy
                                (default 0.05, i.e. 5% below fundamental).
    * ``recovery_threshold`` : float — deviation above which we roll off
                                (default 0.10, i.e. 10% above fundamental).
    * ``max_order``          : float — per-round order cap
                                (default 500.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLongVolHedger(CanonicalRulePlayer):
    STRATEGY = "long-vol-hedger"
    DISPLAY_NAME = "Long-Vol Crash Hedger"
    SUMMARY = (
        "Buys convexity after crashes and rolls it off after recoveries "
        "(Bakshi & Kapadia 2003; Coval & Shumway 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["hedge_ratio"] = float(
            extras.get("hedge_ratio", 0.10)
        )
        self.state.custom_state["crash_threshold"] = float(
            extras.get("crash_threshold", 0.05)
        )
        self.state.custom_state["recovery_threshold"] = float(
            extras.get("recovery_threshold", 0.10)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 500.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hedge_ratio = self.state.custom_state["hedge_ratio"]
        crash_th = self.state.custom_state["crash_threshold"]
        recovery_th = self.state.custom_state["recovery_threshold"]
        max_order = self.state.custom_state["max_order"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if deviation != deviation or math.isnan(deviation):
            return hold
        if state.price <= 0:
            return hold

        if deviation < -crash_th:
            qty = min(max_order, hedge_ratio * state.cash / state.price)
            if qty <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation > recovery_th and state.position > 0:
            qty = min(max_order, state.position)
            if qty <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLongVolHedger(CanonicalLLMPlayer):
    STRATEGY = "long-vol-hedger"
    DEFAULT_SYS_PROMPT = """\
You are a long-volatility hedger. You buy convexity (upside/downside optionality
via the underlying) when the market has crashed well below fundamental value,
and you roll off the hedge after a sharp recovery. You never fight sideways
markets — small deviations are noise, not a hedging opportunity.

Output format:
<analysis>state the current deviation and whether we are in crash, recovery, or noise regime.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide as a long-vol hedger: buy convexity after crashes, roll off after
recoveries, hold otherwise.
"""


__all__ = ["RuleLongVolHedger", "LLMLongVolHedger"]
