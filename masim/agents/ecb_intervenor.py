"""ecb-intervenor — Sovereign-spread central-bank backstop buyer.

Canonical implementation of the ``ecb-intervenor`` archetype documented
in ``examples/AGENT_POOL/finance/ecb-intervenor.md``. When the sovereign
spread exceeds a threshold (in bps), the central bank buys bonds at a
spread-proportional size, subject to a remaining-capacity budget. Never
sells.

Theoretical basis:
    De Grauwe (2012) — self-fulfilling sovereign crises and central-bank
    backstop. Krishnamurthy, Nagel & Vissing-Jorgensen (2018) — ECB QE
    transmission.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If spread > spread_threshold and capacity > 0:
        q = min(capacity / price,
                intervention_size * (spread - spread_threshold) /
                                     spread_threshold)             → buy
        capacity -= q * price                       (post-fill; internal)
    Else: hold.

``spread`` is read from ``state.raw["spread"]`` — declare via
``REQUIRES_FEATURES``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``spread_threshold``  : float — spread level (bps) that triggers
                              intervention (default 300.0).
    * ``intervention_size`` : float — base purchase quantity per
                              intervention (default 20000.0).
    * ``max_holdings``      : float — maximum cumulative bond holdings
                              (initial capacity) (default 250000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleEcbIntervenor(CanonicalRulePlayer):
    STRATEGY = "ecb-intervenor"
    DISPLAY_NAME = "ECB Sovereign-Bond Intervenor"
    SUMMARY = (
        "Central-bank backstop that buys sovereign bonds when spreads "
        "widen (De Grauwe 2012; Krishnamurthy et al. 2018)."
    )
    REQUIRES_FEATURES: tuple = ("spread",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["spread_threshold"] = float(
            extras.get("spread_threshold", 300.0)
        )
        self.state.custom_state["intervention_size"] = float(
            extras.get("intervention_size", 20000.0)
        )
        max_holdings = float(extras.get("max_holdings", 250000.0))
        self.state.custom_state["max_holdings"] = max_holdings
        # Capacity starts at max_holdings and monotonically decreases.
        self.state.custom_state["capacity"] = float(
            extras.get("capacity", max_holdings)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cs = self.state.custom_state
        spread_threshold = cs["spread_threshold"]
        intervention_size = cs["intervention_size"]
        capacity = float(cs.get("capacity", 0.0))

        if capacity <= 0 or state.price <= 0:
            return hold

        spread = float(state.raw.get("spread", 0.0))
        if spread <= spread_threshold:
            return hold

        qty_by_capacity = capacity / state.price
        qty_by_spread = (
            intervention_size * (spread - spread_threshold) / spread_threshold
        )
        quantity = min(qty_by_capacity, qty_by_spread)
        if quantity <= 0:
            return hold

        # Reserve the capacity now; the base finalizer may clip the order
        # further for cash but the intervention capacity budget is a
        # separate mandate constraint.
        cs["capacity"] = max(0.0, capacity - quantity * state.price)
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMEcbIntervenor(CanonicalLLMPlayer):
    STRATEGY = "ecb-intervenor"
    DEFAULT_SYS_PROMPT = """\
You are the central-bank sovereign-bond backstop (ECB-style). Your
mandate is to buy sovereign debt when the spread over the safe rate
widens beyond a policy threshold; you size the purchase proportional
to how far above the threshold the spread has moved, subject to a
remaining programme capacity. You NEVER sell bonds during the crisis.

Output format:
<analysis>state spread vs threshold and remaining programme capacity.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy sovereign bonds when the spread exceeds the intervention threshold,
sized proportional to (spread - threshold) / threshold and capped by
remaining programme capacity.
"""


__all__ = ["RuleEcbIntervenor", "LLMEcbIntervenor"]
