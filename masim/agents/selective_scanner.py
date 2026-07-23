"""selective-scanner — Confirmation-biased selective information scanner.

Canonical implementation of the ``selective-scanner`` archetype documented
in ``examples/AGENT_POOL/finance/selective-scanner.md``. Weights confirming
signals heavily while systematically discounting disconfirming ones, unless
the disconfirming evidence is overwhelming.

Theoretical basis:
    Nickerson (1998) — Confirmation bias.
    Peng & Xiong (2006) — Investor attention and selective information
        processing.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    signal = raw["signal"]                       (from state.raw)

    IF signal * prior_direction > 0:                    (confirming)
        qty = confirm_weight * base_size * |signal|
        action = "buy" if prior_direction > 0 else "sell"
    ELIF signal * prior_direction < 0
         AND |signal| > stubbornness_threshold:         (overwhelming disconfirm)
        qty = disconfirm_weight * base_size * |signal|
        action = "buy" if signal > 0 else "sell"
    ELSE: hold.

Scenario-specific fields (see ``REQUIRES_FEATURES``):
    * ``signal`` : float in [-1, +1] — directional news signal.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``confirm_weight``         : float (default 0.85).
    * ``disconfirm_weight``      : float (default 0.15).
    * ``base_size``              : float (default 200.0).
    * ``stubbornness_threshold`` : float (default 0.60).
    * ``prior_direction``        : int in {-1, +1} (default +1).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleSelectiveScanner(CanonicalRulePlayer):
    STRATEGY = "selective-scanner"
    DISPLAY_NAME = "Confirmation-Biased Selective Scanner"
    SUMMARY = (
        "Confirmation-biased scanner — weights confirming signals heavily "
        "and discounts disconfirmations (Nickerson 1998; Peng & Xiong 2006)."
    )
    REQUIRES_FEATURES: tuple = ("signal",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["confirm_weight"] = float(
            extras.get("confirm_weight", 0.85)
        )
        self.state.custom_state["disconfirm_weight"] = float(
            extras.get("disconfirm_weight", 0.15)
        )
        self.state.custom_state["base_size"] = float(
            extras.get("base_size", 200.0)
        )
        self.state.custom_state["stubbornness_threshold"] = float(
            extras.get("stubbornness_threshold", 0.60)
        )
        prior = int(extras.get("prior_direction", 1))
        self.state.custom_state["prior_direction"] = 1 if prior >= 0 else -1

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        signal_raw = state.raw.get("signal", None)
        if signal_raw is None:
            return hold
        try:
            signal = float(signal_raw)
        except (TypeError, ValueError):
            return hold
        if math.isnan(signal):
            return hold

        prior = cs["prior_direction"]
        aligned = signal * prior

        if aligned > 0:
            # Confirming: weight heavily and act in prior direction.
            qty = cs["confirm_weight"] * cs["base_size"] * abs(signal)
            if qty <= 0:
                return hold
            factory = InvestorOrder.buy if prior > 0 else InvestorOrder.sell
            return factory(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if aligned < 0 and abs(signal) > cs["stubbornness_threshold"]:
            # Disconfirming but overwhelming: reluctantly act in the
            # signal's direction with a heavily discounted size.
            qty = cs["disconfirm_weight"] * cs["base_size"] * abs(signal)
            if qty <= 0:
                return hold
            factory = InvestorOrder.buy if signal > 0 else InvestorOrder.sell
            return factory(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMSelectiveScanner(CanonicalLLMPlayer):
    STRATEGY = "selective-scanner"
    DEFAULT_SYS_PROMPT = """\
You are a confirmation-biased investor. You have a prior directional
belief (long or short) and you weight incoming signals asymmetrically:
signals that agree with your prior get almost their full weight, while
signals that disagree get heavily discounted unless the disconfirming
evidence is overwhelming enough to override your prior.

Output format:
<analysis>state your prior, the signal, and whether it confirms or overwhelms it.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Weight confirming information heavily and discount disconfirming
information; only override your prior when disconfirmation is
overwhelming.
"""


__all__ = ["RuleSelectiveScanner", "LLMSelectiveScanner"]
