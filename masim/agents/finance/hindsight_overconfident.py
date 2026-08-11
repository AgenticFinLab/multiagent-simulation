"""hindsight-overconfident — "Knew it all along" momentum amplifier.

Canonical implementation of the ``hindsight-overconfident`` archetype
documented in ``masim/agents/defines/finance/hindsight-overconfident.md``.
Chases the current price-fundamental deviation with a bias-inflated
position size — post-hoc "obviousness" plus forward overconfidence make
its orders systematically larger than an unbiased momentum trader's.

Theoretical basis:
    Fischhoff (1975) — hindsight bias ("knew it all along").
    Daniel, Hirshleifer & Subrahmanyam (1998) — overconfidence-driven
    momentum and delayed overreaction.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= activation_threshold: hold.
    Else:
        raw_qty = |deviation| * quantity_scale
                  * hindsight_inflation * prediction_overweight
        qty     = min(max_order, int(raw_qty))
        Direction is pro-cyclical:
            deviation > 0 -> buy   (the up-move was "obvious")
            deviation < 0 -> sell  (the down-move was "obvious")

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``activation_threshold`` : float — |deviation| trigger (default 0.02).
    * ``quantity_scale``       : float — deviation->qty scaling (default 5000).
    * ``max_order``            : float — per-round order cap (default 800).
    * ``hindsight_inflation``  : float — "obvious" post-hoc multiplier
                                 (default 1.5, Fischhoff 1975).
    * ``prediction_overweight``: float — forward overconfidence multiplier
                                 (default 1.0, Daniel et al. 1998).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHindsightOverconfident(CanonicalRulePlayer):
    STRATEGY = "hindsight-overconfident"
    DISPLAY_NAME = "Hindsight-Overconfident Trend Chaser"
    SUMMARY = (
        "Pro-cyclical momentum trader whose 'knew it all along' bias inflates "
        "position size beyond rational levels (Fischhoff 1975; Daniel et al. 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.02)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 5000.0)
        )
        self.state.custom_state["max_order"] = float(extras.get("max_order", 800.0))
        self.state.custom_state["hindsight_inflation"] = float(
            extras.get("hindsight_inflation", 1.5)
        )
        self.state.custom_state["prediction_overweight"] = float(
            extras.get("prediction_overweight", 1.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]
        max_order = self.state.custom_state["max_order"]
        hindsight = self.state.custom_state["hindsight_inflation"]
        pred_ow = self.state.custom_state["prediction_overweight"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        raw_qty = abs(deviation) * scale * hindsight * pred_ow
        qty = float(min(max_order, int(raw_qty)))
        if qty <= 0:
            return hold

        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMHindsightOverconfident(CanonicalLLMPlayer):
    STRATEGY = "hindsight-overconfident"
    DEFAULT_SYS_PROMPT = """\
You are a hindsight-overconfident trader. Whatever the market has done
lately looks obvious in retrospect, and you translate that false clarity
into an inflated forward bet. When price is above fundamental you buy
"because the rally was clearly coming"; when it is below you sell
"because the drop was obviously due". You never fade the deviation and
your sizing is deliberately larger than a calibrated momentum trader's.

Output format:
<analysis>describe why the current deviation seems "obvious" and how
that inflates your intended trade.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Chase the deviation with hindsight-inflated conviction: buy above
fundamental, sell below, hold only inside the dead zone.
"""


__all__ = ["RuleHindsightOverconfident", "LLMHindsightOverconfident"]
