"""MASim Player Module.

This module provides the core Player abstraction for autonomous agents.

Base Classes (base.py) - Abstract Definitions Only:
    - BasePlayer: Abstract base class for all Player implementations
    - PlayerConfig: Configuration container for Player initialization
    - PlayerState: Private state container for Player entities
    - Action: Behavioral output contract (what Players produce)
    - LocalObservation: Player's own perception from environment
    - Observation: Complete observation (local + inbounds)
    - StepResult: Result of one perceive-decide-act cycle
    - TurnResult: Result of a turn (multiple steps)

General Implementations (general.py):
    - GeneralPlayer: Ready-to-use Player with default behavior
"""

from masim.player.base import (
    # Types
    PayloadType,
    ActionStatus,
    Action,
    LocalObservation,
    Observation,
    Outbound,
    Inbound,
    StepResult,
    TurnResult,
    # Config
    PlayerConfig,
    # State
    PlayerState,
    # Base class (abstract)
    BasePlayer,
)

from masim.player.general import (
    # Player implementations
    GeneralPlayer,
)

__all__ = [
    # Base types
    "PayloadType",
    "ActionStatus",
    "Action",
    "LocalObservation",
    "Observation",
    "Outbound",
    "Inbound",
    "StepResult",
    "TurnResult",
    "PlayerConfig",
    "PlayerState",
    "BasePlayer",
    # General implementations
    "GeneralPlayer",
]
