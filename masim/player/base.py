"""
Base Player module for the Multi-Agent Simulation (MASim) framework.

================================================================================
                          MODULE CONTENTS
================================================================================

This module contains ONLY:
- Dataclasses: Type definitions for Actions, Observations, Results
- Abstract BasePlayer: Interface contract for all Player implementations

For concrete implementations, see general.py:
- PlayerState: Private state container
- GeneralPlayer: Ready-to-use implementation
- EchoPlayer, NoOpPlayer, ReactivePlayer: Specialized players

================================================================================
                           MODULE OVERVIEW
================================================================================

This module defines the core Player abstraction - the fundamental autonomous
entity in the MASim framework. A Player represents any agent that can:
1. Perceive observations from the environment
2. Make decisions based on internal state and observations
3. Generate Actions that directly affect the environment

================================================================================
                      CORE DESIGN PHILOSOPHY
================================================================================

1. BEHAVIORAL CONTRACT PRINCIPLE
   -----------------------------
   Player is defined by its OUTPUT, not its internal capabilities.

   The critical question: "If I remove this component, what breaks?"
   Answer for Player: Environment cannot receive valid Actions.

   This means:
   - Player → Action → Environment (direct interpretation)
   - Coordinator (role='coordinator') → Actions → Other Players (coordination)

2. INFORMATION ASYMMETRY
   ----------------------
   Player state is PRIVATE and INVISIBLE to other components.

3. THREE-LAYER ARCHITECTURE (Persona Pattern)
   --------------------------------------------
   Player accesses infrastructure ONLY through Persona:

   Player (What: Pure Domain Logic)
       │
       └── Persona (When: Infrastructure Coordination)
                │
                ├── communication_proxy
                ├── storage_proxy
                ├── resource_proxy
                └── observability_proxy

================================================================================
"""

import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from masim.communication.base import Message


# =============================================================================
#                           TYPE ALIASES
# =============================================================================

PayloadType = Union[Dict[str, Any], np.ndarray, bytes]


# =============================================================================
#                              ENUMS
# =============================================================================


class ActionStatus(Enum):
    """
    Lifecycle status of an Action.

    State Transitions:
        CREATED ─────► PENDING ─────► EXECUTING ─────► COMPLETED
                          │               │
                          │               └─────────► FAILED
                          │
                          └───────────────────────► CANCELLED
    """

    CREATED = auto()
    PENDING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


# =============================================================================
#                          CORE DATA TYPES
# =============================================================================


@dataclass
class Action:
    """
    The behavioral output contract for Player entities.

    An Action is a COMMAND that is DIRECTLY INTERPRETED by the environment.
    Player ────► Action ────► Environment (DIRECT execution)

    Attributes:
        action_type: Semantic category (e.g., "trade", "move", "communicate")
        payload: Action parameters (domain-specific structure)
        source_id: ID of the Player that generated this action
        action_id: Unique identifier (auto-generated UUID)
        timestamp: ISO-8601 creation timestamp
        metadata: Optional additional context
        status: Current lifecycle status
    """

    action_type: str
    payload: PayloadType
    source_id: str
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ActionStatus = ActionStatus.CREATED

    def __post_init__(self):
        """Post-initialization validation."""
        self._validate_payload()

    def _validate_payload(self) -> None:
        """Validate payload is serialization-friendly."""
        if self.payload is None:
            return
        if isinstance(self.payload, (dict, list, np.ndarray, bytes)):
            return
        raise TypeError(
            f"Action payload must be dict, list, numpy.ndarray, or bytes. "
            f"Got: {type(self.payload).__name__}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Action to dictionary for transmission/storage."""
        payload_data = self.payload
        if isinstance(self.payload, np.ndarray):
            payload_data = self.payload.tolist()
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "payload": payload_data,
            "source_id": self.source_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "status": self.status.name,
        }


@dataclass
class LocalObservation:
    """
    Player's own perception from environment/sensors.

    Attributes:
        data: Actual observation data (market prices, sensor readings, etc.)
        timestamp: When this observation was captured
        extras: Additional data for extensibility
    """

    data: PayloadType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    extras: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate observation data."""
        if self.data is not None and not isinstance(
            self.data, (dict, list, np.ndarray, bytes)
        ):
            raise TypeError(
                f"LocalObservation.data must be dict, list, numpy.ndarray, or bytes. "
                f"Got: {type(self.data).__name__}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data_serialized = self.data
        if isinstance(self.data, np.ndarray):
            data_serialized = self.data.tolist()
        return {
            "data": data_serialized,
            "timestamp": self.timestamp,
            "extras": self.extras,
        }


@dataclass
class Observation:
    """
    Complete observation for a Player each round.

    Observation Structure:
    - local: LocalObservation (player's own perception)
    - notification: Dict (round notification from coordinator/environment)
    - round: int (simulation round number)
    - extras: Dict (extensibility)

    Note: Messages from other players are NOT part of Observation.
    Messages are stored in Player's message_inbox and accessed via
    get_pending_messages().
    """

    local: LocalObservation
    notification: Dict[str, Any]
    round: int = 0
    extras: Dict[str, Any] = field(default_factory=dict)

    @property
    def data(self) -> PayloadType:
        """Shortcut to access local.data."""
        return self.local.data

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "local": self.local.to_dict(),
            "notification": self.notification,
            "round": self.round,
            "extras": self.extras,
        }


@dataclass
class Outbound:
    """
    Content-focused outbound data that Player wants to send.

    Player returns these in decide() result under 'outbound_messages' key.
    Persona converts them to Message objects and handles routing via topology.

    Attributes:
        payload: The actual content to send
        content_type: Optional categorization of the content
        extras: Flexible additional fields
    """

    payload: PayloadType
    content_type: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "payload": self.payload,
            "content_type": self.content_type,
            "extras": self.extras,
        }


@dataclass
class StepResult:
    """
    Result container for a single step (perceive → decide → act).

    This is the atomic unit of Player execution.
    """

    decision_payload: PayloadType
    action: Action
    tick_step_count: int = 0
    tick_step_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "decision_payload": self.decision_payload,
            "action": self.action.to_dict() if self.action else None,
            "tick_step_count": self.tick_step_count,
            "tick_step_duration_ms": round(self.tick_step_duration_ms, 3),
        }


@dataclass
class TurnResult:
    """
    Result container for a Player's turn (multiple steps).

    Hierarchical execution model:
    - Simulator: round (orchestrates all entities)
    - Player: turn (contains multiple steps)
    - Player: step (one perceive→decide→act cycle)
    """

    step_results: List[StepResult]
    final_action: Optional[Action] = None
    tick_turn_count: int = 0
    tick_turn_duration_ms: float = 0.0
    tick_turn_total_duration_ms: float = 0.0
    tick_step_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "step_results": [sr.to_dict() for sr in self.step_results],
            "final_action": self.final_action.to_dict() if self.final_action else None,
            "tick_turn_count": self.tick_turn_count,
            "tick_turn_duration_ms": round(self.tick_turn_duration_ms, 3),
            "tick_turn_total_duration_ms": round(self.tick_turn_total_duration_ms, 3),
            "tick_step_count": self.tick_step_count,
        }


# =============================================================================
#                      CONFIGURATION
# =============================================================================


@dataclass
class PlayerConfig:
    """
    Configuration container for Player initialization.

    Attributes:
        name: Human-readable unique name for the Player
        identity: Technical identifier for routing, storage, Ray naming
        role: 'player' (default) or 'coordinator'
        group_tags: Tags for group-based operations
        extras: Domain-specific configuration
    """

    name: str
    identity: str
    role: str = "player"
    group_tags: List[str] = field(default_factory=list)
    extras: Dict[str, Any] = field(default_factory=dict)

    def is_coordinator(self) -> bool:
        """Check if this player has coordinator role."""
        return self.role == "coordinator"


# =============================================================================
#                          BASE PLAYER CLASS
# =============================================================================


class BasePlayer(ABC):
    """
    Abstract base class for all Player entities in the MASim framework.

    ╔═════════════════════════════════════════════════════════════════════╗
    ║                       PLAYER BEHAVIORAL CONTRACT                     ║
    ╠═════════════════════════════════════════════════════════════════════╣
    ║                                                                      ║
    ║  A Player is defined by its behavioral OUTPUT: it generates Actions ║
    ║  that are DIRECTLY INTERPRETED by the environment.                  ║
    ║                                                                      ║
    ║  The canonical decision cycle:                                       ║
    ║                                                                      ║
    ║      Observation ──► perceive() ──► Internal State Update           ║
    ║      Internal State ──► decide() ──► Decision Payload               ║
    ║      Decision Payload ──► act() ──► Action                          ║
    ║                                                                      ║
    ╚═════════════════════════════════════════════════════════════════════╝

    Subclasses MUST implement three abstract methods:
    1. perceive(observation) - Process incoming observation
    2. decide() -> PayloadType - Make a decision
    3. act(decision_payload) -> Action - Create the Action

    For a ready-to-use implementation, see GeneralPlayer in general.py.
    """

    # =========================================================================
    # Required Attributes (set by subclass __init__)
    # =========================================================================
    name: str
    identity: str
    group_tags: List[str]
    config: PlayerConfig
    capabilities: List[str]
    is_initialized: bool
    is_running: bool
    topology_targets: List[str]

    # =========================================================================
    #              CORE BEHAVIORAL CONTRACT (ABSTRACT METHODS)
    # =========================================================================

    @abstractmethod
    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> None:
        """
        Process an incoming observation from the environment.

        This method updates the Player's internal state based on new
        information. It should NOT make decisions.

        Args:
            observation: The observation data from environment
            prev_result: Result from the previous step (None for first step)
        """
        ...

    @abstractmethod
    async def decide(self) -> PayloadType:
        """
        Make a decision based on current internal state.

        Returns:
            Decision payload that will be passed to act().
        """
        ...

    @abstractmethod
    async def act(self, decision_payload: PayloadType) -> Action:
        """
        Execute the decision and produce an Action.

        Args:
            decision_payload: The output from decide()

        Returns:
            Action object ready for environment execution
        """
        ...

    # =========================================================================
    #                        LIFECYCLE (Override in subclass)
    # =========================================================================

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the Player for simulation."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the Player after simulation."""
        ...

    # =========================================================================
    #                        EXECUTION (Override in subclass)
    # =========================================================================

    @abstractmethod
    async def step(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> "StepResult":
        """Execute one atomic step: perceive → decide → act."""
        ...

    @abstractmethod
    async def turn(
        self,
        notification: Dict[str, Any],
        round_num: int,
        num_steps: int = 1,
    ) -> "TurnResult":
        """Execute a turn consisting of multiple steps."""
        ...

    # =========================================================================
    #                      MESSAGE HANDLING (Override in subclass)
    # =========================================================================

    @abstractmethod
    def on_message(self, message: "Message") -> None:
        """Receive a message from another player."""
        ...

    @abstractmethod
    def get_pending_messages(self) -> List["Message"]:
        """Get and clear pending messages from inbox."""
        ...

    @abstractmethod
    def is_proceed(self) -> bool:
        """Check if player is ready to proceed with execution."""
        ...

    # =========================================================================
    #                      STATE PERSISTENCE (Override in subclass)
    # =========================================================================

    @abstractmethod
    def save_state(self) -> Dict[str, Any]:
        """Return state that should be persisted."""
        ...

    @abstractmethod
    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state from persisted data."""
        ...
