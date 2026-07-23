"""institutional-holder — Passive institutional holder withholding float.

Canonical implementation of the ``institutional-holder`` archetype documented
in ``examples/AGENT_POOL/finance/institutional-holder.md``. Emits an
unconditional hold every round — models a large index fund / insider whose
locked-up position removes shares from the tradeable float.

Theoretical basis:
    Duffie, Garleanu & Pedersen (2002) — Securities lending, shorting, and
    concentrated ownership.
    Wurgler (2010) — Passive index ownership and price dynamics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Unconditional: emit ``action = "hold"``, ``quantity = 0`` on every call.
    No signals are read; the agent's contribution is structural (float
    reduction), not decision-theoretic.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``initial_position``    : int — shares permanently withheld from float
                                 (default 1000; consumed by the base
                                 initialiser as the starting position).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleInstitutionalHolder(CanonicalRulePlayer):
    STRATEGY = "institutional-holder"
    DISPLAY_NAME = "Passive Institutional Holder"
    SUMMARY = (
        "Locked-up institutional position that never trades; reduces "
        "tradeable float (Duffie, Garleanu & Pedersen 2002; Wurgler 2010)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        # ``initial_position`` is consumed by the base ``_initialize_state``;
        # we mirror it here so downstream introspection can still see the
        # withheld inventory.
        self.state.custom_state["initial_position"] = float(
            extras.get("initial_position", 1000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        # Unconditional hold — the mandate forbids any trading action.
        return InvestorOrder.hold(
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMInstitutionalHolder(CanonicalLLMPlayer):
    STRATEGY = "institutional-holder"
    DEFAULT_SYS_PROMPT = """\
You are a passive institutional holder (index fund, insider, or lock-up
holder). Your mandate forbids trading — you never buy and never sell,
regardless of price movement. Your sole role is to withhold shares from
the tradeable float.

Output format:
<analysis>state that your mandate prohibits trading.</analysis>
<decision>{"action": "hold", "quantity": 0,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Emit hold with quantity 0 — your institutional mandate prohibits trading.
"""


__all__ = ["RuleInstitutionalHolder", "LLMInstitutionalHolder"]
