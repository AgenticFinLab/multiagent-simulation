"""regulator — Central-bank / policy last-resort intervener.

Canonical implementation of the ``regulator`` archetype documented in
``examples/AGENT_POOL/finance/regulator.md``. Buys distressed assets in a
fixed rescue block when price falls far below fundamental and a probabilistic
"political willingness" draw fires.

Theoretical basis:
    Bagehot (1873) — Lender of last resort; discretionary rescue.
    Bernanke (2015) — Political / bureaucratic delay in crisis response.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental
    eligible  = deviation < -intervention_threshold
    draw      = uniform[0, 1)
    affordable = cash >= rescue_size * price
    intervening = eligible AND (draw < rescue_probability) AND affordable

    If ``intervening``: buy exactly ``rescue_size`` shares at market.
    Otherwise: hold. Never sells.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``intervention_threshold`` : float — magnitude of negative deviation
                                    required for eligibility (default 0.50).
    * ``rescue_probability``     : float in [0, 1] — per-round firing
                                    probability (default 0.60).
    * ``rescue_size``            : int > 0 — fixed intervention block
                                    (default 500).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRegulator(CanonicalRulePlayer):
    STRATEGY = "regulator"
    DISPLAY_NAME = "Regulator / Lender of Last Resort"
    SUMMARY = (
        "Probabilistic public-sector intervener that buys a fixed rescue "
        "block when price falls far below fundamental (Bagehot 1873; "
        "Bernanke 2015)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["intervention_threshold"] = float(
            extras.get("intervention_threshold", 0.50)
        )
        self.state.custom_state["rescue_probability"] = float(
            extras.get("rescue_probability", 0.60)
        )
        self.state.custom_state["rescue_size"] = int(extras.get("rescue_size", 500))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["intervention_threshold"]
        prob = self.state.custom_state["rescue_probability"]
        size = self.state.custom_state["rescue_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # NaN guard — no fundamental broadcast means no deviation-based trigger.
        if math.isnan(state.deviation) or math.isnan(state.fundamental):
            return hold
        if state.price <= 0:
            return hold

        eligible = state.deviation < -threshold
        if not eligible:
            return hold

        draw = random.random()
        if draw >= prob:
            return hold

        # Affordability gate — do not attempt a block we cannot cover.
        if state.cash < size * state.price:
            return hold

        return InvestorOrder.buy(
            quantity=float(size),
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRegulator(CanonicalLLMPlayer):
    STRATEGY = "regulator"
    DEFAULT_SYS_PROMPT = """\
You are a public-sector regulator or central bank acting as lender of last
resort. You intervene only when price collapses far below fundamental value
and your political / bureaucratic authority permits action this round. Your
mandate is systemic stability, not profit. You buy in fixed rescue blocks
and never sell.

Output format:
<analysis>state the severity of the deviation and whether intervention is warranted this round.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide: intervene with a fixed rescue block only if the market is deeply
distressed and political authority permits; otherwise hold. Never sell.
"""


__all__ = ["RuleRegulator", "LLMRegulator"]
