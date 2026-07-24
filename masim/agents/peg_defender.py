"""peg-defender — Central-bank / peg-defending intervention agent.

Canonical implementation of the ``peg-defender`` archetype documented in
``examples/AGENT_POOL/finance/peg-defender.md``. The agent defends a
declared peg (proxied by ``fundamental``) by intervening against
deviations while it still has ammunition (cash).

Theoretical basis:
    Obstfeld (1996) — logic of currency crises; a defender's credibility
    depends on remaining reserves.
    Krugman (1979) — first-generation balance-of-payments crises.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    dev = (price - fundamental) / fundamental

    If ``|dev| > defense_trigger`` AND ``cash > 0``:
        direction is opposite to ``sign(dev)`` (buy when below peg,
        sell when above peg);
        quantity = min(defense_size, int(|dev| * 3000), int(cash / price))
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``defense_trigger`` : float — |deviation| threshold that activates
                             intervention (default 0.05, Obstfeld 1996).
    * ``defense_size``    : float — per-tick intervention cap
                             (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RulePegDefender(CanonicalRulePlayer):
    STRATEGY = "peg-defender"
    DISPLAY_NAME = "Peg Defender"
    SUMMARY = (
        "Central-bank-style intervenor: defends a declared peg by trading "
        "against deviations while reserves last (Obstfeld 1996)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["defense_trigger"] = float(
            extras.get("defense_trigger", 0.05)
        )
        self.state.custom_state["defense_size"] = float(
            extras.get("defense_size", 500.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        trigger = self.state.custom_state["defense_trigger"]
        size_cap = self.state.custom_state["defense_size"]
        dev = state.deviation

        if abs(dev) <= trigger:
            return hold

        # Direction is opposite to the sign of the deviation: buy below
        # peg (dev < 0), sell above peg (dev > 0).
        if dev > 0:
            # Overvalued: sell reserves of the asset (must have position).
            if state.position <= 0:
                return hold
            quantity = min(size_cap, abs(dev) * 3000.0, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        else:
            # Undervalued: buy the asset with remaining cash.
            if state.cash <= 0:
                return hold
            affordable = state.cash / state.price
            quantity = min(size_cap, abs(dev) * 3000.0, affordable)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )


class LLMPegDefender(CanonicalLLMPlayer):
    STRATEGY = "peg-defender"
    DEFAULT_SYS_PROMPT = """\
You are a peg defender (central bank / policy authority). Your mandate is to
defend the declared peg (fundamental value). When the market price drifts
above the peg you sell reserves to push it back down; when it drifts below
the peg you buy to push it back up. You only intervene when the deviation
is large enough to matter and you still have ammunition (cash/inventory).

Output format:
<analysis>state the deviation from peg and your intervention stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), peg/fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Reserves: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Defend the peg: sell if price is above the peg, buy if below, hold if the
deviation is small or reserves are depleted.
"""


__all__ = ["RulePegDefender", "LLMPegDefender"]
