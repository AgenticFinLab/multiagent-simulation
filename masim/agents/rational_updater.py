"""rational-updater — Fundamental-value rational updater.

Canonical implementation of the ``rational-updater`` archetype documented in
``examples/AGENT_POOL/finance/rational-updater.md``. This is the rational
benchmark: no bias, no anchoring, no herding — just directional trades
whenever the broadcast ``deviation`` exceeds a threshold.

Theoretical basis:
    Muth (1961) — Rational Expectations.
    Fama (1970) — Efficient Markets Hypothesis (semi-strong form).

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast by market)

    If ``deviation < -threshold``: buy — price is underpriced.
    If ``deviation > threshold``:  sell — price is overpriced.
    Otherwise: hold.

    Quantity = ``min(base_position_size, |deviation| * sizing_scale)``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``threshold``           : float in [0, 1] — deviation cut-off
                                 (default 0.02).
    * ``base_position_size``  : float > 0 — order-size cap (default 20.0).
    * ``sizing_scale``        : float > 0 — deviation→quantity factor
                                 (default 1000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalUpdater(CanonicalRulePlayer):
    STRATEGY = "rational-updater"
    DISPLAY_NAME = "Rational Fundamental Updater"
    SUMMARY = (
        "Trades directly on the broadcast price↔fundamental deviation; "
        "converges on fundamental value (Muth 1961; Fama 1970)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.02))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        # `deviation` may be NaN when the scenario does not model a
        # fundamental (see StandardMarketState.from_market_data). Any
        # comparison with NaN is False, so an untreated deviation would
        # slip into the trade branch below with garbage sizing. Explicit
        # NaN check keeps the rational updater at hold.
        if deviation != deviation or math.isnan(deviation):  # NaN guard
            return hold
        if abs(deviation) <= threshold:
            return hold

        quantity = min(base, abs(deviation) * sizing)
        factory = InvestorOrder.buy if deviation < 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRationalUpdater(CanonicalLLMPlayer):
    STRATEGY = "rational-updater"
    DEFAULT_SYS_PROMPT = """\
You are a rational updater. You treat the broadcast fundamental as the
correct long-run value and the observed deviation as an unbiased signal.
When deviation is meaningful you trade toward fundamental; otherwise
you hold. No anchoring, no momentum-chasing, no disposition effects.

Output format:
<analysis>compare the observed deviation to your threshold and justify.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide rationally: buy when price is below fundamental, sell when above.
"""


__all__ = ["RuleRationalUpdater", "LLMRationalUpdater"]
