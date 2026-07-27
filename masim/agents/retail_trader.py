"""retail-trader — Small retail noise-plus-mean-reversion trader.

Canonical implementation of the ``retail-trader`` archetype documented in
``examples/AGENT_POOL/finance/retail-trader.md``. Emits a small mean-reverting
noise order on a fixed cadence.

Theoretical basis:
    Black (1986) — Noise trading; small uninformed retail orders.
    simulation-bases.md §4.6 — Retail parameter calibrations.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    If ``round % trade_frequency != 0``: hold.
    Else:
        random_trade = gauss(0, noise_std)
        reversion    = -position_mean_reversion * position
        raw_quantity = random_trade + reversion
        quantity     = clamp(raw_quantity, -max_quantity, +max_quantity)

    quantity > 0 → buy; quantity < 0 → sell; else hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``trade_frequency``         : int > 0 (default 5).
    * ``noise_std``               : float > 0 (default 8.0).
    * ``position_mean_reversion`` : float (default 0.1).
    * ``max_quantity``            : int > 0 (default 15).
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRetailTrader(CanonicalRulePlayer):
    STRATEGY = "retail-trader"
    DISPLAY_NAME = "Small Retail Trader"
    SUMMARY = (
        "Small retail trader — noise order every few rounds with a mild "
        "position-mean-reversion pull (Black 1986)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["trade_frequency"] = int(
            extras.get("trade_frequency", 5)
        )
        self.state.custom_state["noise_std"] = float(extras.get("noise_std", 8.0))
        self.state.custom_state["position_mean_reversion"] = float(
            extras.get("position_mean_reversion", 0.1)
        )
        self.state.custom_state["max_quantity"] = int(
            extras.get("max_quantity", 15)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        freq = max(1, self.state.custom_state["trade_frequency"])
        noise_std = self.state.custom_state["noise_std"]
        rev = self.state.custom_state["position_mean_reversion"]
        max_q = self.state.custom_state["max_quantity"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.round % freq != 0:
            return hold

        random_trade = random.gauss(0.0, noise_std)
        reversion = -rev * state.position
        raw_quantity = random_trade + reversion
        # Clamp symmetrically to ±max_quantity per profile.
        if raw_quantity > max_q:
            raw_quantity = float(max_q)
        elif raw_quantity < -max_q:
            raw_quantity = float(-max_q)

        if raw_quantity > 0:
            return InvestorOrder.buy(
                quantity=float(raw_quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if raw_quantity < 0:
            return InvestorOrder.sell(
                quantity=float(-raw_quantity),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMRetailTrader(CanonicalLLMPlayer):
    STRATEGY = "retail-trader"
    DEFAULT_SYS_PROMPT = """\
You are a small retail trader. You trade infrequently — only every few
rounds — and your orders are small, roughly random in direction with a
mild pull toward keeping your position near zero. You do not track
fundamentals or momentum with any precision.

Output format:
<analysis>state whether this round is an active trading round and your bias.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade only on your infrequent active rounds; keep the order small and
biased toward reverting your position back toward zero.
"""


__all__ = ["RuleRetailTrader", "LLMRetailTrader"]
