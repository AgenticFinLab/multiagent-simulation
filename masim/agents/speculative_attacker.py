"""speculative-attacker — Currency-peg / reserve-run attacker.

Canonical implementation of the ``speculative-attacker`` archetype
documented in ``examples/AGENT_POOL/finance/speculative-attacker.md``.
Waits for two co-conditions on the defender's reserves and the peg's
fundamental misalignment, then attacks in size scaled by how far the
misalignment breaches its threshold.

Theoretical basis:
    Obstfeld (1996) — second-generation currency-crisis / self-fulfilling
    speculative attacks.
    Morris & Shin (1998) — coordination attack under private information.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    reserve_ratio = reserves / initial_reserves
    misalign      = fundamental_misalignment

    if reserve_ratio < reserve_threshold  and
       misalign      > misalign_threshold:
        qty = attack_size * (misalign / misalign_threshold)
        sell qty
    else:
        hold

    All inputs beyond ``price`` come from ``state.raw`` because they are
    coordinator-broadcast features of the peg/defender.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``reserve_threshold``  : float — reserve-ratio trigger
                               (default 0.10).
    * ``misalign_threshold`` : float — misalignment trigger (default 0.05).
    * ``attack_size``        : float — nominal attack quantity
                               (default 2000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _read_float(source: Dict[str, Any], key: str) -> float | None:
    value = source.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class RuleSpeculativeAttacker(CanonicalRulePlayer):
    STRATEGY = "speculative-attacker"
    DISPLAY_NAME = "Speculative Attacker"
    SUMMARY = (
        "Attacks the peg when reserves are depleted and misalignment is "
        "large (Obstfeld 1996; Morris & Shin 1998)."
    )
    REQUIRES_FEATURES: tuple = (
        "reserves",
        "initial_reserves",
        "fundamental_misalignment",
    )

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["reserve_threshold"] = float(
            extras.get("reserve_threshold", 0.10)
        )
        self.state.custom_state["misalign_threshold"] = float(
            extras.get("misalign_threshold", 0.05)
        )
        self.state.custom_state["attack_size"] = float(
            extras.get("attack_size", 2000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        reserves = state.raw_require("reserves", cast=float)
        initial_reserves = state.raw_require("initial_reserves", cast=float)
        misalign = state.raw_require("fundamental_misalignment", cast=float)
        if initial_reserves <= 0:
            return hold

        reserve_ratio = reserves / initial_reserves
        r_thresh = self.state.custom_state["reserve_threshold"]
        m_thresh = self.state.custom_state["misalign_threshold"]
        size = self.state.custom_state["attack_size"]

        if reserve_ratio >= r_thresh or misalign <= m_thresh:
            return hold
        if m_thresh <= 0:
            return hold

        quantity = size * (misalign / m_thresh)
        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMSpeculativeAttacker(CanonicalLLMPlayer):
    STRATEGY = "speculative-attacker"
    DEFAULT_SYS_PROMPT = """\
You are a speculative attacker in a currency-peg regime. You watch the
defender's reserves and the peg's fundamental misalignment: only when
reserves are visibly depleted AND misalignment is well above threshold
do you launch a coordinated short in size scaled by the breach.

Output format:
<analysis>state the reserve ratio, misalignment, and whether both trigger.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f}, fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Attack only when reserves are below your threshold AND misalignment is
above yours; otherwise hold.
"""


__all__ = ["RuleSpeculativeAttacker", "LLMSpeculativeAttacker"]
