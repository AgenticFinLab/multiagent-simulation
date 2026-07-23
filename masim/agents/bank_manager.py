"""bank-manager — Bank ALM manager buying undervalued own securities.

Canonical implementation of the ``bank-manager`` archetype documented in
``examples/AGENT_POOL/finance/bank-manager.md``.

Theoretical basis:
    Flannery (1994) — bank asset-liability management under interest-rate
    stress; Vermaelen (1981) — issuer buybacks as a signalling and
    defensive tool.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``deviation < -defense_threshold`` and cash > 0:
        buy quantity = min(defense_size, int(cash / price))
    Otherwise: hold. (Buy-only defensive stance.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``defense_threshold`` : float — trigger below fundamental
                              (default 0.05).
    * ``defense_size``      : int  — per-tick share cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBankManager(CanonicalRulePlayer):
    STRATEGY = "bank-manager"
    DISPLAY_NAME = "Defensive Bank Manager"
    SUMMARY = (
        "Bank ALM manager defensively buying own securities when they trade "
        "meaningfully below fundamental (Flannery 1994; Vermaelen 1981)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["defense_threshold"] = float(
            extras.get("defense_threshold", 0.05)
        )
        self.state.custom_state["defense_size"] = int(
            extras.get("defense_size", 500)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["defense_threshold"]
        if deviation >= -threshold:
            return hold
        if state.cash <= 0 or state.price <= 0:
            return hold

        cap = self.state.custom_state["defense_size"]
        affordable = int(state.cash / state.price) if state.price > 0 else 0
        quantity = min(cap, affordable)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBankManager(CanonicalLLMPlayer):
    STRATEGY = "bank-manager"
    DEFAULT_SYS_PROMPT = """\
You are a bank asset-liability manager. When your own securities trade
materially below fundamental value, you defensively buy them back up
to a per-tick cap and available cash. You never sell defensively; you
only support the price when it dislocates downward.

Output format:
<analysis>state whether the discount exceeds your defense threshold.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Defend the security: buy when it trades below fundamental past the
threshold; otherwise hold.
"""


__all__ = ["RuleBankManager", "LLMBankManager"]
