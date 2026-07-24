"""loss-frame-reactor — Framing-effect deviation reactor.

Canonical implementation of the ``loss-frame-reactor`` archetype documented
in ``examples/AGENT_POOL/finance/loss-frame-reactor.md``. Trades against
mispricing framed as loss/gain relative to fundamental, with a dead band
inside which the deviation is treated as noise.

Theoretical basis:
    Kahneman & Tversky (1979) — Prospect Theory framing effects.
    Thaler (1985) — mental accounting and reference-dependent choice.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= dead_band``: hold.
    If ``deviation > dead_band``:
        buy min(max_order, int(|deviation| * sizing_scale)).
    If ``deviation < -dead_band``:
        sell min(max_order, int(|deviation| * sizing_scale), position).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``dead_band``    : float — |deviation| tolerance band (default 0.02).
    * ``sizing_scale`` : float — deviation→quantity factor (default 5000.0).
    * ``max_order``    : float — per-round order cap (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLossFrameReactor(CanonicalRulePlayer):
    STRATEGY = "loss-frame-reactor"
    DISPLAY_NAME = "Framing-Effect Deviation Reactor"
    SUMMARY = (
        "Trades against mispricing framed as loss/gain vs fundamental with "
        "a dead-band tolerance (Kahneman-Tversky 1979; Thaler 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["dead_band"] = float(
            extras.get("dead_band", 0.02)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(
            extras.get("max_order", 800.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        dead_band = self.state.custom_state["dead_band"]
        sizing = self.state.custom_state["sizing_scale"]
        max_order = self.state.custom_state["max_order"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if deviation != deviation or math.isnan(deviation):
            return hold
        if abs(deviation) <= dead_band:
            return hold

        signal_qty = int(abs(deviation) * sizing)
        qty = float(min(max_order, signal_qty))
        if qty <= 0:
            return hold

        if deviation > dead_band:
            return InvestorOrder.buy(
                quantity=qty,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # deviation < -dead_band
        qty = float(min(qty, state.position))
        if qty <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMLossFrameReactor(CanonicalLLMPlayer):
    STRATEGY = "loss-frame-reactor"
    DEFAULT_SYS_PROMPT = """\
You are a framing-effect reactor. You frame the current price gap against
fundamental as either a loss (price above fundamental, over-bought) or a
gain to be captured (price below fundamental, over-sold). Small deviations
inside a dead band feel like noise and you ignore them; larger deviations
scale your order size linearly in the mispricing.

Output format:
<analysis>describe the deviation frame and where the signal falls relative
to your dead band.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide by framing: hold inside the dead band, otherwise trade against the
mispricing with size proportional to |deviation|.
"""


__all__ = ["RuleLossFrameReactor", "LLMLossFrameReactor"]
