"""mbs-originator — MBS originator distributing to investors.

Canonical implementation of the ``mbs-originator`` archetype documented in
``examples/AGENT_POOL/finance/mbs-originator.md``. Models the
originate-to-distribute lender who steadily unloads freshly securitised
inventory into the market.

Theoretical basis:
    Keys, Mukherjee, Seru & Vig (2010) — securitization and lax screening.
    Purnanandam (2011) — originate-to-distribute and mortgage quality.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``position <= 0``: hold (nothing left to distribute).
    Else:
        qty = int(position * distribution_rate)
        if qty == 0 and position >= 1: qty = 1  # floor at 1 to keep
        emit sell(qty).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``distribution_rate`` : float — fraction of remaining inventory
                               sold each round (default 0.08).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMbsOriginator(CanonicalRulePlayer):
    STRATEGY = "mbs-originator"
    DISPLAY_NAME = "MBS Originate-To-Distribute Lender"
    SUMMARY = (
        "Steadily distributes securitised inventory each round "
        "(Keys et al. 2010; Purnanandam 2011)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["distribution_rate"] = float(
            extras.get("distribution_rate", 0.08)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        rate = self.state.custom_state["distribution_rate"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.position <= 0:
            return hold

        qty = int(state.position * rate)
        if qty == 0 and state.position >= 1:
            qty = 1
        if qty <= 0:
            return hold
        qty = min(qty, int(state.position))
        return InvestorOrder.sell(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMbsOriginator(CanonicalLLMPlayer):
    STRATEGY = "mbs-originator"
    DEFAULT_SYS_PROMPT = """\
You are a mortgage originator running an originate-to-distribute business.
Each round you unload a modest slice of your existing MBS inventory into
the secondary market — steady distribution, never accumulation. You never
buy; you only shrink your book over time.

Output format:
<analysis>state your remaining inventory and this round's distribution slice.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as an MBS originator: distribute a small fraction of remaining
inventory this round; hold when inventory is exhausted.
"""


__all__ = ["RuleMbsOriginator", "LLMMbsOriginator"]
