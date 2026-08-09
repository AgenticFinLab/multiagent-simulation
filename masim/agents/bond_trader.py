"""bond-trader — Fixed-income deadband contrarian trader.

Canonical implementation of the ``bond-trader`` archetype documented in
``masim/agents/defines/finance/bond-trader.md``.

Theoretical basis:
    Ellul, Jotikasthira & Lundblad (2011) — fire-sale mispricings in
    corporate bonds; Collin-Dufresne, Goldstein & Martin (2001) —
    mean-reversion in credit spreads.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``|deviation| > deadband_threshold``:
        raw_qty  = int(|deviation| * sizing_gain)
        quantity = min(quantity_cap, raw_qty)
        deviation > 0 -> sell (overvalued)
        deviation < 0 -> buy  (undervalued)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``deadband_threshold`` : float — trigger (default 0.03).
    * ``sizing_gain``        : float — deviation -> qty gain
                                (default 3000.0).
    * ``quantity_cap``       : int  — per-tick cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleBondTrader(CanonicalRulePlayer):
    STRATEGY = "bond-trader"
    DISPLAY_NAME = "Fixed-Income Bond Trader"
    SUMMARY = (
        "Deadband bond trader exploiting mark-to-market dislocations "
        "(Ellul, Jotikasthira & Lundblad 2011; Collin-Dufresne et al. 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["deadband_threshold"] = float(
            extras.get("deadband_threshold", 0.03)
        )
        self.state.custom_state["sizing_gain"] = float(
            extras.get("sizing_gain", 3000.0)
        )
        self.state.custom_state["quantity_cap"] = int(
            extras.get("quantity_cap", 500)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["deadband_threshold"]
        if abs(deviation) <= threshold:
            return hold

        gain = self.state.custom_state["sizing_gain"]
        cap = self.state.custom_state["quantity_cap"]
        raw_qty = int(abs(deviation) * gain)
        quantity = min(cap, raw_qty)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=float(quantity),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMBondTrader(CanonicalLLMPlayer):
    STRATEGY = "bond-trader"
    DEFAULT_SYS_PROMPT = """\
You are a professional fixed-income trader at a broker-dealer or asset
manager. You exploit mark-to-market dislocations in bank-related
securities: buying when they trade materially below fundamental value
and selling when they trade materially above. Inside a 3% deadband
you hold to avoid trading on noise.

Output format:
<analysis>state |deviation| vs deadband and direction.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
If |deviation| exceeds the deadband, trade contrarian; otherwise hold.
"""


__all__ = ["RuleBondTrader", "LLMBondTrader"]
