"""independent-thinker — Bayesian contrarian who breaks cascades.

Canonical implementation of the ``independent-thinker`` archetype
documented in ``examples/AGENT_POOL/finance/independent-thinker.md``. Acts
as the rational agent in Bikhchandani et al. (1992) who breaks
information cascades by trading against the deviation direction based on
a private signal of quality ``signal_precision``.

Theoretical basis:
    Bikhchandani, Hirshleifer & Welch (1992) — informational cascades.
    Avery & Zemsky (1998) — multidimensional uncertainty and contrarian
    behaviour in financial markets.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    deviation = (price - fundamental) / fundamental

    If |deviation| <= 0.03: hold.
    Else:
        qty = min(max_order, int(|deviation| * signal_precision * 3000))
        deviation > 0 -> sell (fade the crowd)
        deviation < 0 -> buy  (fade the crowd)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``signal_precision`` : float — signal quality / contrarian intensity
                              scaler (default 0.9, Avery & Zemsky 1998).
    * ``max_order``        : float — per-round order cap (default 500).
    * ``activation_threshold`` : float — |deviation| trigger (default 0.03).
    * ``quantity_scale``   : float — base deviation->qty factor (default 3000).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndependentThinker(CanonicalRulePlayer):
    STRATEGY = "independent-thinker"
    DISPLAY_NAME = "Independent Bayesian Contrarian"
    SUMMARY = (
        "Cascade-breaking contrarian that fades deviations using a private "
        "signal (Bikhchandani et al. 1992; Avery & Zemsky 1998)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["signal_precision"] = float(
            extras.get("signal_precision", 0.9)
        )
        self.state.custom_state["max_order"] = float(extras.get("max_order", 500.0))
        self.state.custom_state["activation_threshold"] = float(
            extras.get("activation_threshold", 0.03)
        )
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        precision = self.state.custom_state["signal_precision"]
        max_order = self.state.custom_state["max_order"]
        threshold = self.state.custom_state["activation_threshold"]
        scale = self.state.custom_state["quantity_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold
        if abs(deviation) <= threshold:
            return hold

        qty = float(min(max_order, int(abs(deviation) * precision * scale)))
        if qty <= 0:
            return hold

        # CONTRARIAN direction: trade against the deviation.
        factory = InvestorOrder.sell if deviation > 0 else InvestorOrder.buy
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMIndependentThinker(CanonicalLLMPlayer):
    STRATEGY = "independent-thinker"
    DEFAULT_SYS_PROMPT = """\
You are an independent Bayesian thinker with a private signal. You do not
follow the crowd; if a cascade has pushed price meaningfully above or
below fundamental, you trade against it — buying when the market is
depressed, selling when it is exuberant. Your conviction scales with the
precision of your private signal and with the magnitude of the observed
deviation.

Output format:
<analysis>state the current deviation and how your private signal argues
against the crowd.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Break the cascade: buy when the crowd has pushed price too low, sell when
too high, hold otherwise.
"""


__all__ = ["RuleIndependentThinker", "LLMIndependentThinker"]
