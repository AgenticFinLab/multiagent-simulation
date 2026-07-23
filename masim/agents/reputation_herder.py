"""reputation-herder — Career-concern reputation herder.

Canonical implementation of the ``reputation-herder`` archetype documented
in ``examples/AGENT_POOL/finance/reputation-herder.md``. Trades in the
direction of the crowd (proxied here by the sign of the broadcast
price-to-fundamental deviation) to protect reputation.

Theoretical basis:
    Scharfstein & Stein (1990) — Herd Behavior and Investment.
    Chevalier & Ellison (1999) — Career concerns of mutual fund managers.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| > 0.02``:
        qty       = min(max_order, int(|deviation| * reputation_concern * 4000))
        quantity  = sign(deviation) * qty
    Otherwise: quantity = 0.

    Positive quantity → buy; negative → sell; zero → hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``reputation_concern`` : float — career-concern intensity multiplier
                                (default 0.7).
    * ``max_order``          : int > 0 — hard cap on order size
                                (default 600).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleReputationHerder(CanonicalRulePlayer):
    STRATEGY = "reputation-herder"
    DISPLAY_NAME = "Career-Concern Reputation Herder"
    SUMMARY = (
        "Herds with the observable deviation signal to protect reputation "
        "(Scharfstein & Stein 1990; Chevalier & Ellison 1999)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["reputation_concern"] = float(
            extras.get("reputation_concern", 0.7)
        )
        self.state.custom_state["max_order"] = int(extras.get("max_order", 600))
        # Threshold is hard-wired at 0.02 in the profile §Mathematical Model.
        self.state.custom_state["dev_threshold"] = float(
            extras.get("dev_threshold", 0.02)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        concern = self.state.custom_state["reputation_concern"]
        max_order = self.state.custom_state["max_order"]
        threshold = self.state.custom_state["dev_threshold"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if abs(state.deviation) <= threshold:
            return hold

        qty = min(max_order, int(abs(state.deviation) * concern * 4000))
        if qty <= 0:
            return hold
        factory = InvestorOrder.buy if state.deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=float(qty),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMReputationHerder(CanonicalLLMPlayer):
    STRATEGY = "reputation-herder"
    DEFAULT_SYS_PROMPT = """\
You are a career-concerned institutional manager. Your bonus and job
security depend on not standing out from the crowd. When the market shows
a clear directional deviation from fundamental value you trade with it —
buying when price is above fundamental (crowd is long) and selling when
it is below (crowd is short) — because being wrong alone is far more
costly than being wrong with everyone else.

Output format:
<analysis>state the sign and magnitude of the deviation and your herding stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Herd with the crowd: buy in the direction of a meaningful deviation, hold
when the deviation is small. Reputation trumps contrarian conviction.
"""


__all__ = ["RuleReputationHerder", "LLMReputationHerder"]
