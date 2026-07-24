"""macro-hedge-fund — Macro speculator / peg-attacker.

Canonical implementation of the ``macro-hedge-fund`` archetype documented
in ``examples/AGENT_POOL/finance/macro-hedge-fund.md``. Attacks mispricings
once they exceed a size threshold — famously the model of Soros-style
speculation against a defended peg (Krugman 1979, Obstfeld 1996).

Theoretical basis:
    Krugman (1979) — first-generation currency crisis model.
    Obstfeld (1996) — self-fulfilling attacks on FX pegs.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``|deviation| <= attack_threshold``: hold (no juicy signal).
    If ``deviation > attack_threshold``:
        buy min(position_cap, int(|deviation| * sizing_scale)) — price is
        rich vs fundamental? Model states the fund still presses direction.
    If ``deviation < -attack_threshold``:
        sell min(position_cap, int(|deviation| * sizing_scale)) — press
        the depreciation.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``attack_threshold``  : float — |deviation| trigger (default 0.02).
    * ``sizing_scale``      : float — |deviation|→qty factor (default 5000.0).
    * ``position_cap``      : float — per-round order cap (default 800.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMacroHedgeFund(CanonicalRulePlayer):
    STRATEGY = "macro-hedge-fund"
    DISPLAY_NAME = "Macro Hedge Fund / Peg Attacker"
    SUMMARY = (
        "Attacks large mispricings once they exceed a threshold "
        "(Krugman 1979; Obstfeld 1996)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["attack_threshold"] = float(
            extras.get("attack_threshold", 0.02)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 5000.0)
        )
        self.state.custom_state["position_cap"] = float(
            extras.get("position_cap", 800.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["attack_threshold"]
        sizing = self.state.custom_state["sizing_scale"]
        cap = self.state.custom_state["position_cap"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if deviation != deviation or math.isnan(deviation):
            return hold
        if abs(deviation) <= threshold:
            return hold

        signal_qty = int(abs(deviation) * sizing)
        qty = float(min(cap, signal_qty))
        if qty <= 0:
            return hold

        factory = InvestorOrder.buy if deviation > 0 else InvestorOrder.sell
        return factory(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMacroHedgeFund(CanonicalLLMPlayer):
    STRATEGY = "macro-hedge-fund"
    DEFAULT_SYS_PROMPT = """\
You are a macro hedge fund manager. You do not care about noise; you wait
for a mispricing large enough to be worth pressing, then size aggressively
in the direction the mispricing implies. When the mispricing is inside
your attack threshold you sit on your hands.

Output format:
<analysis>state the current deviation and whether it warrants a macro attack.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide as a macro fund: press large mispricings, ignore small ones.
"""


__all__ = ["RuleMacroHedgeFund", "LLMMacroHedgeFund"]
