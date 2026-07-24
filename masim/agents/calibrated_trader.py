"""calibrated-trader — Calibrated-signal-precision contrarian trader.

Canonical implementation of the ``calibrated-trader`` archetype documented in
``examples/AGENT_POOL/finance/calibrated-trader.md``.

Theoretical basis:
    Grossman & Stiglitz (1980) — informed traders correcting mispricings
    at a bounded intensity determined by signal precision; Odean (1998) —
    calibrated (unbiased) confidence as the rational benchmark.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental   (broadcast)

    If ``|deviation| > trade_threshold``:
        raw_qty  = int(|deviation| * signal_precision * sizing_gain)
        quantity = min(base_size, raw_qty)
        deviation > 0 -> sell (overvalued)
        deviation < 0 -> buy  (undervalued)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``trade_threshold``  : float — trigger (default 0.03).
    * ``signal_precision`` : float — evidence gain (default 1.0).
    * ``sizing_gain``      : float — deviation -> qty gain (default 3000.0).
    * ``base_size``        : int  — per-tick cap (default 500).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleCalibratedTrader(CanonicalRulePlayer):
    STRATEGY = "calibrated-trader"
    DISPLAY_NAME = "Calibrated Rational Trader"
    SUMMARY = (
        "Calibrated rational trader sizing by signal-precision-weighted "
        "deviation (Grossman & Stiglitz 1980; Odean 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["trade_threshold"] = float(
            extras.get("trade_threshold", 0.03)
        )
        self.state.custom_state["signal_precision"] = float(
            extras.get("signal_precision", 1.0)
        )
        self.state.custom_state["sizing_gain"] = float(
            extras.get("sizing_gain", 3000.0)
        )
        self.state.custom_state["base_size"] = int(
            extras.get("base_size", 500)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        threshold = self.state.custom_state["trade_threshold"]
        if abs(deviation) <= threshold:
            return hold

        precision = self.state.custom_state["signal_precision"]
        gain = self.state.custom_state["sizing_gain"]
        cap = self.state.custom_state["base_size"]

        raw_qty = int(abs(deviation) * precision * gain)
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


class LLMCalibratedTrader(CanonicalLLMPlayer):
    STRATEGY = "calibrated-trader"
    DEFAULT_SYS_PROMPT = """\
You are a calibrated rational trader. Your confidence in your
fundamental signal is honest (not over- or under-confident), so you
scale position size linearly in signal-precision-weighted deviation.
You buy when price is materially below fundamental, sell when above,
and hold inside a small trade threshold to avoid overtrading noise.

Output format:
<analysis>state deviation vs threshold and calibrated size.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Trade calibrated to deviation: buy underpriced, sell overpriced, hold
inside the small threshold; size scales with signal precision.
"""


__all__ = ["RuleCalibratedTrader", "LLMCalibratedTrader"]
