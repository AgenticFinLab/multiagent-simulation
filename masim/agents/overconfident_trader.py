"""overconfident-trader — Precision-overestimating trader (DHS 1998).

Canonical implementation of the ``overconfident-trader`` archetype
documented in ``examples/AGENT_POOL/finance/overconfident-trader.md``. The
agent takes the raw mispricing signal ``(fundamental - price) / price`` and
inflates it by a precision-overestimate multiplier, then trades in the
direction of the (inflated) signal with oversized quantities.

Theoretical basis:
    Daniel, Hirshleifer & Subrahmanyam (1998) — overconfidence and asset
    pricing.
    Odean (1998) — excess volume from overconfidence.
    Barber & Odean (2000) — overconfident traders' cost of trading.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation_signed = (fundamental - price) / price   (positive => underpriced)
    perceived        = deviation_signed * precision_overestimate

    If ``|perceived| <= activation_threshold``: hold.
    Elif ``perceived > 0``: buy (underpriced).
    Else: sell (overpriced).

    Quantity = ``min(base_size * 2, int(|perceived| * quantity_scale))``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``precision_overestimate`` : float — inflation multiplier (default 2.0).
    * ``activation_threshold``   : float — perceived-signal cut-off
                                    (default 0.01).
    * ``base_size``              : float — base per-trade size (default 400.0).
    * ``quantity_scale``         : float — |perceived|→shares scale
                                    (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleOverconfidentTrader(CanonicalRulePlayer):
    STRATEGY = "overconfident-trader"
    DISPLAY_NAME = "Precision-Overestimating Trader"
    SUMMARY = (
        "Inflates the perceived precision of the mispricing signal and "
        "trades oversized in its direction (Daniel et al. 1998; Odean 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["precision_overestimate"] = float(
            extras.get("precision_overestimate", 2.0)
        )
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.01)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 400.0))
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        precision = self.state.custom_state["precision_overestimate"]
        threshold = self.state.custom_state["activation_threshold"]
        base = self.state.custom_state["base_size"]
        q_scale = self.state.custom_state["quantity_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold
        # Profile-specific direction convention: positive means underpriced.
        deviation_signed = (state.fundamental - state.price) / state.price
        perceived = deviation_signed * precision

        if abs(perceived) <= threshold:
            return hold

        raw_qty = int(abs(perceived) * q_scale)
        quantity = float(min(base * 2.0, float(raw_qty)))
        if quantity <= 0:
            return hold
        factory = InvestorOrder.buy if perceived > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMOverconfidentTrader(CanonicalLLMPlayer):
    STRATEGY = "overconfident-trader"
    DEFAULT_SYS_PROMPT = """\
You are an overconfident trader. You see the same public signals as
everyone else, but you believe your read of them is far more precise
than it really is. Whenever price is below fundamental, you are
extra-sure it will rebound — you buy aggressively. Whenever price is
above fundamental, you are extra-sure it will fall — you sell
aggressively. Your position sizes are always oversized relative to a
calibrated trader.

Output format:
<analysis>state the mispricing signal and how your overconfidence inflates it.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade with inflated precision: buy hard when price is below fundamental,
sell hard when above; small perceived signals below your threshold: hold.
"""


__all__ = ["RuleOverconfidentTrader", "LLMOverconfidentTrader"]
