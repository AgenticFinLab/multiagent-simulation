"""funding-currency-buyer — Supportive buyer of a currency under stress.

Canonical implementation of the ``funding-currency-buyer`` archetype
documented in ``examples/AGENT_POOL/finance/funding-currency-buyer.md``.
Steps in with size ``position_size`` when the currency's deviation drops
below the negative risk threshold; otherwise sits out.

Theoretical basis:
    Ranaldo & Söderlind (2010) — Safe haven currencies.

Decision rule (from AGENT_POOL profile §Behavioral Framework — reproduced
literally per Golden Rule 6):

    If ``deviation < -risk_threshold``: buy ``position_size`` (capped by
    ``cash / price``, respecting an optional ``cash_floor``).
    Otherwise: hold.

Note: The worked example in the profile flips the sign convention (uses
``deviation > +risk_threshold`` as the trigger). Per Golden Rule 6, this
implementation follows the §Core Behavioral Mechanism text literally.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``risk_threshold`` : float — stress trigger (default 0.05).
    * ``position_size``  : float — buy quantity (default 500.0).
    * ``cash_floor``     : float — reserve floor (default 0.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleFundingCurrencyBuyer(CanonicalRulePlayer):
    STRATEGY = "funding-currency-buyer"
    DISPLAY_NAME = "Funding Currency Buyer"
    SUMMARY = (
        "Supportive buyer of a stressed currency (Ranaldo & Soderlind 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["risk_threshold"] = float(extras.get("risk_threshold", 0.05))
        cs["position_size"] = float(extras.get("position_size", 500.0))
        cs["cash_floor"] = float(extras.get("cash_floor", 0.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["risk_threshold"]
        size = cs["position_size"]
        cash_floor = cs["cash_floor"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or state.price <= 0:
            return hold
        if state.deviation >= -threshold:
            return hold

        spendable = max(0.0, state.cash - cash_floor)
        quantity = min(size, spendable / state.price)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMFundingCurrencyBuyer(CanonicalLLMPlayer):
    STRATEGY = "funding-currency-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a supportive buyer of a stressed funding currency. When the
currency has weakened enough versus fundamental (deviation is negative
beyond your threshold), you step in with a supportive buy. In normal
conditions you stay on the sidelines.

Output format:
<analysis>state the stress level and your supportive stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Provide supportive buying when the currency is stressed below threshold.
"""


__all__ = ["RuleFundingCurrencyBuyer", "LLMFundingCurrencyBuyer"]
