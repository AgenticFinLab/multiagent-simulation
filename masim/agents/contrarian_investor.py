"""contrarian-investor — Bid-formation contrarian with Gaussian noise.

Canonical implementation of the ``contrarian-investor`` archetype
documented in ``examples/AGENT_POOL/finance/contrarian-investor.md``.
Posts a bid drawn around fundamental with additive noise and sizes an
order proportional to the mispricing, clipped to a per-tick range.

Theoretical basis:
    De Bondt & Thaler (1985) — overreaction and long-run reversal.
    LeBaron (2006) — agent-based models of financial markets;
    heterogeneous belief traders.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    mispricing = (fundamental - price) / price
    bid        = fundamental + N(0, noise_std)
    raw_qty    = beta * mispricing * cash / bid
    qty        = clip(raw_qty, -clip_range, +clip_range)
    action     = "buy" if qty>0 else "sell" if qty<0 else "hold"

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``beta``       : float > 0 — sensitivity to mispricing
                        (default 0.5).
    * ``noise_std``  : float > 0 — Gaussian noise std on bid
                        (default 0.5).
    * ``clip_range`` : float > 0 — |qty| clip per tick (default 50.0).
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContrarianInvestor(CanonicalRulePlayer):
    STRATEGY = "contrarian-investor"
    DISPLAY_NAME = "Bid-Noise Contrarian Investor"
    SUMMARY = (
        "Posts a fundamental-anchored bid with Gaussian noise and sizes "
        "orders proportional to mispricing (De Bondt & Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["beta"] = float(extras.get("beta", 0.5))
        self.state.custom_state["noise_std"] = float(extras.get("noise_std", 0.5))
        self.state.custom_state["clip_range"] = float(
            extras.get("clip_range", 50.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or state.price <= 0:
            return hold

        beta = self.state.custom_state["beta"]
        noise_std = self.state.custom_state["noise_std"]
        clip_range = self.state.custom_state["clip_range"]

        mispricing = (state.fundamental - state.price) / state.price
        bid = state.fundamental + random.gauss(0.0, noise_std)
        if bid <= 0:
            return hold
        raw_qty = beta * mispricing * state.cash / bid
        qty = max(-clip_range, min(clip_range, raw_qty))

        if qty > 0:
            return InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if qty < 0:
            return InvestorOrder.sell(
                quantity=float(-qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMContrarianInvestor(CanonicalLLMPlayer):
    STRATEGY = "contrarian-investor"
    DEFAULT_SYS_PROMPT = """\
You are a fundamental-anchored contrarian. You quote around fundamental
with a small stochastic bid noise, and you size your orders in
proportion to the mispricing — buying discounts, selling premiums —
with a strict per-tick clip on |quantity| (De Bondt & Thaler 1985).

Output format:
<analysis>state the mispricing and your sized order.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Buy the discount, sell the premium, size proportional to mispricing
with a per-tick clip; hold when mispricing is negligible.
"""


__all__ = ["RuleContrarianInvestor", "LLMContrarianInvestor"]
