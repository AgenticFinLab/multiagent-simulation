"""MASim Conductor Module.

This module provides the Conductor abstraction for coordination.

Base Classes (base.py):
    - BaseConductor: Abstract base class for all Conductor implementations
    - ConductorConfig: Configuration container for Conductor initialization
    - ConductorState: State container for Conductor entities
    - CoordinationDecision: Behavioral output contract (what Conductors produce)
    - CycleResult: Result of one coordination cycle
    - DecisionScope: Scope of coordination decisions (GLOBAL, GROUP, INDIVIDUAL)

General Implementations (general.py):
    - GeneralConductor: Ready-to-use Conductor with default behavior
    - PassThroughConductor: Conductor that passes through without coordination
    - ThrottlingConductor: Conductor that applies throttling based on activity
    - BroadcastConductor: Conductor that broadcasts decisions to all players
"""

from masim.conductor.base import (
    # Types
    DecisionScope,
    CoordinationDecision,
    CycleResult,
    # Config/State
    ConductorConfig,
    ConductorState,
    # Base class
    BaseConductor,
)

from masim.conductor.general import (
    GeneralConductor,
    PassThroughConductor,
    ThrottlingConductor,
    BroadcastConductor,
)

__all__ = [
    # Base types
    "DecisionScope",
    "CoordinationDecision",
    "CycleResult",
    "ConductorConfig",
    "ConductorState",
    "BaseConductor",
    # General implementations
    "GeneralConductor",
    "PassThroughConductor",
    "ThrottlingConductor",
    "BroadcastConductor",
]
