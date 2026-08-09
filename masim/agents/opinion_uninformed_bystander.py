"""opinion-uninformed-bystander — Uninformed passive bystander (opinion domain).

Canonical implementation of the ``uninformed-bystander`` archetype documented
in ``masim/agents/defines/opinion/uninformed-bystander.md``. Models a passive
social-media reader who receives information without retransmitting it. In
Watts (2002)'s cascade model these are the silent majority whose belief may
drift with the ambient signal, but who never actively propagate.

Domain projection (opinion-diffusion → InvestorOrder):
    The native decision space is {receive} (never share). Since the
    canonical order schema only exposes {buy, sell, hold}, the agent's
    action is *always* ``hold`` — it updates its internal belief state
    every tick via ``env_belief`` but produces no outbound orders.

    We nevertheless maintain the belief update so that downstream analytics
    (or future extensions of the order schema) can inspect the agent's
    passive drift.

Theoretical basis:
    Watts, D. J. (2002). A simple model of global cascades on random
    networks. *PNAS*, 99(9), 5766-5771. Most nodes in information networks
    are passive; global cascades depend on the active minority crossing a
    critical threshold.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    # Passive absorption of ambient belief at rate `absorption_rate`.
    my_belief = clamp(my_belief + absorption_rate * (env_belief - my_belief), 0, 1)
    action    = "hold"                       # never share, always receive

Parameters (read from ``extras``; profile lists none — sensible defaults):
    * ``absorption_rate`` : float, [0, 1] — passive belief drift rate toward
                             ``env_belief`` each tick (default 0.05).
    * ``initial_belief``  : float, [0, 1] — starting ``my_belief``
                             (default 0.5).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


class RuleOpinionUninformedBystander(CanonicalRulePlayer):
    STRATEGY = "opinion-uninformed-bystander"
    DISPLAY_NAME = "Uninformed Passive Bystander (Opinion)"
    SUMMARY = (
        "Silent-majority reader who absorbs ambient belief but never "
        "retransmits (Watts 2002)."
    )
    REQUIRES_FEATURES: tuple = ("env_belief",)

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["absorption_rate"] = float(
            extras.get("absorption_rate", 0.05)
        )
        self.state.custom_state["my_belief"] = float(
            extras.get("initial_belief", 0.5)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        absorption_rate = cs["absorption_rate"]

        env_belief = state.raw_require("env_belief", cast=float)
        my_belief = float(cs.get("my_belief", 0.5))
        my_belief = _clamp(
            my_belief + absorption_rate * (env_belief - my_belief), 0.0, 1.0
        )
        cs["my_belief"] = my_belief

        # Profile mandate: always receive, never share.
        return InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )


class LLMOpinionUninformedBystander(CanonicalLLMPlayer):
    STRATEGY = "opinion-uninformed-bystander"
    DEFAULT_SYS_PROMPT = """\
You are a passive social-media reader. You see messages roll by and your
private belief drifts slowly with the ambient signal, but you never share,
never argue, and never trade on rumors. You are part of the silent majority
whose non-participation is the reason most information cascades die out
(Watts 2002). In this simulation your action is always "hold".

Output format:
<analysis>briefly note passive belief drift.</analysis>
<decision>{"action": "hold", "quantity": 0.0,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
You are a passive bystander; hold every round.
"""


__all__ = ["RuleOpinionUninformedBystander", "LLMOpinionUninformedBystander"]
