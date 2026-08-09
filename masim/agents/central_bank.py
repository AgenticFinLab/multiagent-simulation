"""central-bank — Stochastic lender-of-last-resort central bank.

Canonical implementation of the ``central-bank`` archetype documented in
``masim/agents/defines/finance/central-bank.md``. Intervenes stochastically
on the buy side when the market trades sufficiently far below fundamental
— a probabilistic Bagehot-style rescue.

Theoretical basis:
    Bagehot (1873) — Lombard Street; lender-of-last-resort doctrine.
    Reinhart & Rogoff (2009) — This Time is Different; discretionary
    central-bank rescues.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental
    IF deviation < -intervention_threshold AND random() < rescue_probability:
        BUY rescue_size shares
    ELSE:
        HOLD (never sells)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``intervention_threshold`` : float > 0 — |deviation| trigger
                                    (default 0.10).
    * ``rescue_probability``     : float in [0, 1] — per-round rescue
                                    probability (default 0.50).
    * ``rescue_size``            : float > 0 — units bought per rescue
                                    (default 2000.0).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCentralBank(CanonicalRulePlayer):
    STRATEGY = "central-bank"
    DISPLAY_NAME = "Lender-of-Last-Resort Central Bank"
    SUMMARY = (
        "Stochastically buys the market when deviation is deeply "
        "negative — Bagehot (1873) lender-of-last-resort doctrine."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["intervention_threshold"] = float(
            extras.get("intervention_threshold", 0.10)
        )
        self.state.custom_state["rescue_probability"] = float(
            extras.get("rescue_probability", 0.50)
        )
        self.state.custom_state["rescue_size"] = float(
            extras.get("rescue_size", 2000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold

        theta = self.state.custom_state["intervention_threshold"]
        prob = self.state.custom_state["rescue_probability"]
        size = self.state.custom_state["rescue_size"]

        if state.deviation >= -theta:
            return hold
        if random.random() >= prob:
            return hold
        if size <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=size,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMCentralBank(CanonicalLLMPlayer):
    STRATEGY = "central-bank"
    DEFAULT_SYS_PROMPT = """\
You are a central bank acting as lender of last resort. You NEVER sell
into the market; when the price falls deeply below fundamental you may,
at your discretion, inject buying support — a Bagehot-style rescue that
is stochastic in timing but never pro-cyclical.

Output format:
<analysis>state whether the deviation crosses your intervention threshold and whether you rescue.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Intervene only when deviation is deeply negative; buy rescue_size if you
decide to act, otherwise hold. Never sell.
"""


__all__ = ["RuleCentralBank", "LLMCentralBank"]
