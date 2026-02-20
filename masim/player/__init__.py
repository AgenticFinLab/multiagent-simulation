"""MASim Player Module.

This module provides the core Player abstraction for autonomous agents.

Base Classes (base.py) - Abstract Definitions Only:
    - BasePlayer: Abstract base class for all Player implementations
    - PlayerConfig: Configuration container for Player initialization
    - Action: Behavioral output contract (what Players produce)
    - LocalObservation: Player's own perception from environment
    - Observation: Complete observation (local + notification)
    - StepResult: Result of one perceive-decide-act cycle
    - TurnResult: Result of a turn (multiple steps)

General Implementations (general.py):
    - PlayerState: Private state container for Player entities
    - GeneralPlayer: Ready-to-use Player with default behavior
    - EchoPlayer: Player that echoes back observations
    - NoOpPlayer: Player that takes no action
    - ReactivePlayer: Player that reacts based on triggers
"""

from masim.player.base import (
    # Types
    PayloadType,
    ActionStatus,
    Action,
    LocalObservation,
    Observation,
    Outbound,
    StepResult,
    TurnResult,
    # Config
    PlayerConfig,
    # Base class (abstract)
    BasePlayer,
)

from masim.player.general import (
    # State container (implementation)
    PlayerState,
    # Player implementations
    GeneralPlayer,
    EchoPlayer,
    NoOpPlayer,
    ReactivePlayer,
)

__all__ = [
    # Base types
    "PayloadType",
    "ActionStatus",
    "Action",
    "LocalObservation",
    "Observation",
    "Outbound",
    "StepResult",
    "TurnResult",
    "PlayerConfig",
    "PlayerState",
    "BasePlayer",
    # General implementations
    "GeneralPlayer",
    "EchoPlayer",
    "NoOpPlayer",
    "ReactivePlayer",
]
