"""MASim Player Module.

This module provides the core Player abstraction for autonomous agents.

Base Classes (base.py):
    - BasePlayer: Abstract base class for all Player implementations
    - PlayerConfig: Configuration container for Player initialization
    - PlayerState: Private state container for Player entities
    - Action: Behavioral output contract (what Players produce)
    - Observation: Structured input from environment
    - StepResult: Result of one perceive→decide→act cycle
    - TurnResult: Result of a turn (multiple steps)

General Implementations (general.py):
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
    Observation,
    StepResult,
    TurnResult,
    # Config/State
    PlayerConfig,
    PlayerState,
    # Base class
    BasePlayer,
)

from masim.player.general import (
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
    "Observation",
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
