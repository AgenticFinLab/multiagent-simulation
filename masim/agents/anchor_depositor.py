"""anchor-depositor — Currency-peg anchored depositor that runs on the peg.

Canonical implementation of the ``anchor-depositor`` archetype documented in
``examples/AGENT_POOL/finance/anchor-depositor.md``.

Theoretical basis:
    Goldstein & Pauzner (2005) — depositor runs on stressed pegs;
    Krugman (1979) — currency-attack model of peg abandonment.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    parity_local = state.raw["parity"] (fallback 1.0)
    dev_local    = (price - parity_local) / parity_local

    If ``dev_local < -yield_threshold`` and ``position > 0``:
        sell floor(position * withdrawal_fraction).
    Otherwise: hold. (Sell-only — anchor depositors never buy.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``yield_threshold``     : float — peg-break threshold (default 0.12).
    * ``withdrawal_fraction`` : float — fraction withdrawn on trigger
                                (default 0.4).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleAnchorDepositor(CanonicalRulePlayer):
    STRATEGY = "anchor-depositor"
    DISPLAY_NAME = "Peg-Anchored Depositor"
    SUMMARY = (
        "Peg-anchored depositor withdrawing when the price breaks below the "
        "parity by the yield threshold (Goldstein & Pauzner 2005)."
    )
    REQUIRES_FEATURES: tuple = ("parity",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["yield_threshold"] = float(
            extras.get("yield_threshold", 0.12)
        )
        self.state.custom_state["withdrawal_fraction"] = float(
            extras.get("withdrawal_fraction", 0.4)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        parity = float(state.raw.get("parity", 1.0) or 1.0)
        if parity <= 0 or math.isnan(parity):
            return hold

        dev_local = (state.price - parity) / parity
        threshold = self.state.custom_state["yield_threshold"]
        if dev_local >= -threshold:
            return hold
        if state.position <= 0:
            return hold

        fraction = self.state.custom_state["withdrawal_fraction"]
        quantity = math.floor(state.position * fraction)
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMAnchorDepositor(CanonicalLLMPlayer):
    STRATEGY = "anchor-depositor"
    DEFAULT_SYS_PROMPT = """\
You are an anchored depositor tied to a currency peg. As long as price
tracks the parity you hold. When the market price falls below the peg
by more than your yield threshold, you interpret it as a break signal
and withdraw a fixed fraction of your holdings. You never add to the
position; you only reduce.

Output format:
<analysis>state whether the peg has broken relative to your threshold.</analysis>
<decision>{"action": "sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If the price is running significantly below the peg parity, withdraw
the configured fraction; otherwise hold.
"""


__all__ = ["RuleAnchorDepositor", "LLMAnchorDepositor"]
