"""Canonical, scenario-agnostic agent classes for the Customized Simulation Builder.

Every class in this package consumes only the standard market state broadcast
by the simulation framework (price, prev_price, fundamental, deviation, round)
and the agent's own portfolio state (cash, position). No class in this package
references anything under ``examples/<Scenario>/`` — that is the whole point of
the marketplace catalog architecture.

The shared base classes are :class:`masim.agents._base.CanonicalRulePlayer` and
:class:`masim.agents._base.CanonicalLLMPlayer`; archetype-specific classes live
in sibling modules (``noise_trader.py``, ``anchoring_bias_investor.py``, etc.).
"""

from masim.agents._state import StandardMarketState
from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer

__all__ = [
    "StandardMarketState",
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
]
