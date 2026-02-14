"""
Base Player module for the Multi-Agent Simulation (MASim) framework.

================================================================================
                          MODULE CONTENTS
================================================================================

Dataclasses:
    Action              - Behavioral output: action_type, payload, source_id
    Observation         - Structured input: data, source_id, target_id, step
    StepResult          - Result of one step: action, decision_payload, timing
    TurnResult          - Result of a turn: list of StepResults, final_action
    PlayerConfig        - Configuration: identity, group_tags, extras

Classes:
    PlayerState         - Private state container (invisible to other components)
    BasePlayer          - Abstract base class for all Player implementations

For concrete implementations, see general.py:
    GeneralPlayer       - Configurable via extras["strategy"]
    EchoPlayer          - Echoes observations as actions
    NoOpPlayer          - Always produces no-op actions
    ReactivePlayer      - Triggers actions based on extras["triggers"]

================================================================================
                           MODULE OVERVIEW
================================================================================

This module defines the core Player abstraction - the fundamental autonomous
entity in the MASim framework. A Player represents any agent that can:
1. Perceive observations from the environment
2. Make decisions based on internal state and observations
3. Generate Actions that directly affect the environment

Key Components:
    - Action: The behavioral output contract (what Players produce)
    - Observation: Structured input from environment (what Players consume)
    - PlayerConfig: Configuration container for initialization
    - PlayerState: Private state container (invisible to other components)
    - BasePlayer: Abstract base class for all Player implementations

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
   - Conductor → CoordinationDecision → Players (indirect influence)

   Player outputs are COMMANDS that the environment executes.
   Conductor outputs are SUGGESTIONS that Players may consider.

2. INFORMATION ASYMMETRY
   ----------------------
   Player state is PRIVATE and INVISIBLE to other components.

   ┌──────────────────────────────────────────────────────────────┐
   │                    VISIBILITY BOUNDARY                        │
   │                                                               │
   │   Conductor          ──────────────────────►  Globally Visible │
   │   Player.state       ──────────────────────►  Private         │
   │                                                               │
   │   This asymmetry is FUNDAMENTAL to multi-agent systems:       │
   │   - Enables strategic behavior                                │
   │   - Models real-world information constraints                 │
   │   - Prevents "omniscient coordinator" anti-pattern            │
   └──────────────────────────────────────────────────────────────┘

3. CAPABILITY PARITY WITH CONDUCTOR
   ---------------------------------
   Player and Conductor have EQUAL capabilities (same proxy access).
   They differ ONLY in their behavioral contracts:

   ┌─────────────────┬──────────────────────┬─────────────────────┐
   │  Component      │  Output Type         │  Environment Impact │
   ├─────────────────┼──────────────────────┼─────────────────────┤
   │  Player         │  Action              │  DIRECT             │
   │  Conductor      │  CoordinationDecision│  INDIRECT           │
   └─────────────────┴──────────────────────┴─────────────────────┘

4. THREE-LAYER ARCHITECTURE (Persona Pattern)
   --------------------------------------------
   Player accesses infrastructure ONLY through Persona:

   Player (What: Pure Domain Logic)
       │
       └── _persona ──► Persona (When: Infrastructure Coordination)
                            │
                            ├── communication_proxy
                            ├── storage_proxy
                            ├── resource_proxy
                            └── observability_proxy

   Benefits:
   - COMPLETE DECOUPLING: Player has zero proxy knowledge
   - SINGLE INTERFACE: One set_persona() instead of four attach_*() methods
   - TESTABILITY: Mock one Persona instead of four proxies
   - PURE DOMAIN LOGIC: Player contains zero infrastructure code

================================================================================
                      RAY DISTRIBUTED ARCHITECTURE
================================================================================

In the Ray-based distributed runtime, Player instances are wrapped:

    ┌─────────────────────────────────────────────────────────────┐
    │  Ray Cluster                                                 │
    │                                                              │
    │   ┌──────────────────┐      ┌──────────────────┐           │
    │   │  PlayerProxy     │      │  PlayerProxy     │           │
    │   │  (Ray Actor)     │      │  (Ray Actor)     │           │
    │   │    ┌─────────┐   │      │    ┌─────────┐   │           │
    │   │    │BasePlayer│   │      │    │BasePlayer│   │           │
    │   │    │(domain   │   │      │    │(domain   │   │           │
    │   │    │ logic)   │   │      │    │ logic)   │   │           │
    │   │    └─────────┘   │      │    └─────────┘   │           │
    │   └──────────────────┘      └──────────────────┘           │
    │            │                          │                     │
    │            └──────────────────────────┘                     │
    │                        │                                     │
    │                   Ray GCS (Global Control Store)            │
    └─────────────────────────────────────────────────────────────┘

Key insight: BasePlayer contains PURE DOMAIN LOGIC.
The Ray wrapper (PlayerProxy in simulator/) handles distribution concerns.

================================================================================
                          USAGE EXAMPLE
================================================================================

    # 1. Define a concrete Player implementation
    class TradingPlayer(BasePlayer):
        async def perceive(
            self,
            observation: Observation,
            prev_result: Optional[StepResult] = None,
        ) -> None:
            self.state.set_custom("market_data", observation.data)
            if prev_result:
                self.state.set_custom("last_action", prev_result.action)

        async def decide(self) -> Dict[str, Any]:
            market = self.state.get_custom("market_data")
            # ... decision logic ...
            return {"action": "buy", "quantity": 100}

        async def act(self, decision: Dict[str, Any]) -> Action:
            return Action(
                action_type="trade",
                payload=decision,
                source_id=self.identity
            )

    # 2. Create and configure
    config = PlayerConfig(
        identity="trader_001",
        group_tags=["market_makers"],
        extras={"capabilities": ["market_data", "order_book"]}
    )
    player = TradingPlayer(config)

    # 3. Attach Persona (infrastructure facade)
    persona = PlayerPersona(
        player,
        storage_proxy=StorageProxy(),
        resource_proxy=ResourceProxy(),
    )
    player.set_persona(persona)

    # 4. Run in simulation loop
    await player.initialize()
    # perceive → decide → act
    action = await player.step(observation)

    # 5. Use Persona for infrastructure (Player has NO direct proxy access)
    data = await player.persona.fetch_resource("mcp://market/prices")
    await player.persona.checkpoint(label="before_trade")

================================================================================
                          EXECUTION FLOW
================================================================================

Player is called by PlayerPersona (which is called by Simulator):

PlayerPersona.operate(observation, num_steps):
│
└── Player.turn(observation, num_steps)
    │
    ├── perceive(observation, prev_result=None)  # First step
    │
    └── for step_num in range(num_steps):
        │
        └── Player.step(observation, prev_result)
            │
            ├── perceive(observation, prev_result)  # Update internal state
            │   └── Access: self.state.set_custom(key, value)
            │
            ├── decide()                            # Core decision logic
            │   └── Returns: Dict[str, Any] (decision payload)
            │
            └── act(decision_payload)               # Produce Action
                └── Returns: Action(action_type, payload, source_id)
            │
            └── Returns: StepResult
    │
    └── Returns: TurnResult(step_results, final_action)

Abstract Methods (MUST implement):
    perceive(observation, prev_result) → None    # Update internal state
    decide()                           → Dict    # Core decision logic
    act(decision_payload)              → Action  # Produce behavioral output

The framework composes these into step() and turn() automatically.

================================================================================
"""

import time
import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import numpy as np

# ---------------------------------------------------------------------------
# TYPE_CHECKING Block
# ---------------------------------------------------------------------------
# These imports are only for static type checking (mypy, IDE hints).
# At runtime, they are NOT imported to avoid circular dependencies.
# This is a standard Python pattern for forward references.
# ---------------------------------------------------------------------------
if TYPE_CHECKING:
    from masim.communication.base import Message
    from masim.persona.base import PlayerPersona


# =============================================================================
#                           TYPE ALIASES
# =============================================================================
# PayloadType defines what can be transmitted through the framework.
# Supports:
#   - Dict[str, Any]: JSON-like structured data (most common)
#   - np.ndarray: Numerical arrays for ML/scientific computing (zero-copy with Arrow)
#   - bytes: Raw binary data for custom serialization
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

    - CREATED: Action just instantiated, not yet submitted
    - PENDING: Submitted to environment, awaiting execution
    - EXECUTING: Currently being processed by environment
    - COMPLETED: Successfully executed
    - FAILED: Execution failed (check metadata for error)
    - CANCELLED: Explicitly cancelled before execution
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
#
# These dataclasses define the BEHAVIORAL CONTRACTS of the framework.
# They are domain-agnostic - the framework makes NO assumptions about
# what an "action" means in your specific domain (trading, robotics, etc.)
#
# =============================================================================


@dataclass
class Action:
    """
    The behavioral output contract for Player entities.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                        ACTION CONTRACT                               │
    │                                                                      │
    │  An Action is a COMMAND that is DIRECTLY INTERPRETED by the         │
    │  environment. This is the key distinction from CoordinationDecision.│
    │                                                                      │
    │  Player ────► Action ────► Environment (DIRECT execution)           │
    │  Conductor ──► CoordinationDecision ──► Players (INDIRECT influence)│
    └─────────────────────────────────────────────────────────────────────┘

    Design Principles:
    ------------------
    1. DOMAIN AGNOSTIC: The framework doesn't know what "buy" or "move" means.
       Your environment interprets action_type and payload semantics.

    2. SERIALIZATION FRIENDLY: payload must be serializable for:
       - Ray distributed communication (pickle/Arrow)
       - Storage checkpointing (JSON/binary)
       - Network transmission (gRPC/WebSocket)

    3. TRACEABLE: Every action has unique ID and timestamp for:
       - Audit trails and compliance
       - Debugging distributed systems
       - Performance profiling

    Attributes:
        action_type: Semantic category (e.g., "trade", "move", "communicate")
        payload: Action parameters (domain-specific structure)
        source_id: ID of the Player that generated this action
        action_id: Unique identifier (auto-generated UUID)
        timestamp: ISO-8601 creation timestamp
        metadata: Optional additional context (e.g., priority, tags)
        status: Current lifecycle status

    Example:
        # Trading domain
        Action(
            action_type="limit_order",
            payload={"symbol": "AAPL", "side": "buy", "price": 150.0, "qty": 100},
            source_id="trader_001"
        )

        # Robotics domain
        Action(
            action_type="move",
            payload={"target": [10.5, 20.3, 0.0], "velocity": 1.5},
            source_id="robot_arm_01"
        )
    """

    # -------------------------------------------------------------------------
    # Required Fields (must be provided)
    # -------------------------------------------------------------------------
    # Semantic category of the action
    action_type: str
    # Action parameters (domain-specific)
    payload: PayloadType
    # ID of the generating Player
    source_id: str

    # -------------------------------------------------------------------------
    # Auto-generated Fields (with defaults)
    # -------------------------------------------------------------------------
    # Using field(default_factory=...) for mutable defaults and computed values
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ActionStatus = ActionStatus.CREATED

    def __post_init__(self):
        """
        Post-initialization validation.

        Called automatically after __init__ completes. We use this to
        validate payload type without requiring explicit validation calls.
        """
        self._validate_payload()

    def _validate_payload(self) -> None:
        """
        Validate payload is serialization-friendly.

        Raises:
            TypeError: If payload is not a supported type

        Why these types?
        - dict/list: JSON-compatible, human-readable
        - np.ndarray: Zero-copy with Apache Arrow, efficient for ML
        - bytes: Raw binary for custom protocols
        """
        if self.payload is None:
            # None is allowed (represents "no parameters")
            return

        if isinstance(self.payload, (dict, list, np.ndarray, bytes)):
            # Valid types
            return

        raise TypeError(
            f"Action payload must be dict, list, numpy.ndarray, or bytes. "
            f"Got: {type(self.payload).__name__}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize Action to dictionary for transmission/storage.

        Note: np.ndarray is converted to list for JSON compatibility.
        For high-performance scenarios, use Arrow serialization instead.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        # Handle numpy array conversion
        payload_data = self.payload
        if isinstance(self.payload, np.ndarray):
            # Convert to nested list
            payload_data = self.payload.tolist()

        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "payload": payload_data,
            "source_id": self.source_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            # Enum → string
            "status": self.status.name,
        }


@dataclass
class LocalObservation:
    """
    Player's own perception from environment/sensors.

    This represents what the player directly observes, independent of
    any coordinator signals. Think of it as the player's "eyes and ears".

    Attributes:
        data: Actual observation data (market prices, sensor readings, etc.)
        timestamp: When this observation was captured (ISO-8601 format)
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

    ┌─────────────────────────────────────────────────────────────┐
    │                     OBSERVATION STRUCTURE                       │
    │                                                                 │
    │  Observation                                                    │
    │  ├── local: LocalObservation  (player's own perception)        │
    │  │   ├── data: PayloadType    (what player "sees")              │
    │  │   └── timestamp: str       (when observed)                   │
    │  ├── conductor_notify: Dict  (coordinator signals)              │
    │  ├── round: int              (simulation round number)          │
    │  └── extras: Dict            (extensibility)                    │
    └─────────────────────────────────────────────────────────────┘

    Attributes:
        local: Player's own observation from environment
        conductor_notify: Coordinator's notification/signals
        round: Current simulation round (matches Simulator.current_round)
        extras: Additional data for extensibility

    Example:
        Observation(
            local=LocalObservation(data={"price": 100.0, "volume": 1000}),
            conductor_notify={"phase": "trading", "time_remaining": 30},
            round=5,
        )
    """

    local: LocalObservation
    conductor_notify: Dict[str, Any]
    round: int
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "local": self.local.to_dict(),
            "conductor_notify": self.conductor_notify,
            "round": self.round,
            "extras": self.extras,
        }


@dataclass
class StepResult:
    """
    Result container for a single step (perceive → decide → act).

    This is the atomic unit of Player execution. Each step processes
    one observation and produces one action.

    A turn() consists of multiple steps.
    """

    # The raw output from decide()
    decision_payload: PayloadType

    # The Action produced by act()
    action: Action

    # Which step number this is (within the current turn)
    tick_step_count: int = 0

    # Duration of this step in milliseconds
    tick_step_duration_ms: float = 0.0


@dataclass
class TurnResult:
    """
    Result container for a Player's turn (multiple steps).

    ┌─────────────────────────────────────────────────────────────────────┐
    │                        TURN RESULT STRUCTURE                          │
    │                                                                       │
    │  turn(num_steps=3) {                                                  │
    │      for i in range(num_steps):                                       │
    │          step_result = step(observation)  // StepResult              │
    │          step_results.append(step_result)                            │
    │  }                                                                     │
    │                                                                       │
    │  TurnResult bundles:                                                  │
    │    - step_results: List of StepResult from each step                  │
    │    - final_action: The last action produced                           │
    │    - tick_turn_*: Timing metrics for the entire turn                  │
    └─────────────────────────────────────────────────────────────────────┘

    Hierarchical execution model:
    - Simulator: round (orchestrates all entities)
    - Player: turn (contains multiple steps)
    - Player: step (one perceive→decide→act cycle)

    Example:
        result = await player.turn(observation, num_steps=3)
        for step_result in result.step_results:
            logger.debug("Step %d: %s", step_result.tick_step_count, step_result.action)
        logger.info("Final action: %s", result.final_action)
    """

    # List of StepResult from each step in this turn
    step_results: List[StepResult]

    # The final action (from the last step) - convenience accessor
    final_action: Optional[Action] = None

    # Turn counter - which turn number this is
    tick_turn_count: int = 0

    # Duration of this turn in milliseconds (all steps combined)
    tick_turn_duration_ms: float = 0.0

    # Cumulative total duration of all turns so far
    tick_turn_total_duration_ms: float = 0.0

    # Number of steps executed in this turn
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
#                      CONFIGURATION AND STATE
# =============================================================================


@dataclass
class PlayerConfig:
    """
    Configuration container for Player initialization.

    This separates configuration from behavior, enabling:
    - External configuration (YAML/JSON files)
    - Factory pattern instantiation
    - Configuration validation before instantiation

    Attributes:
        name: Human-readable unique name for the Player (system-wide unique)
        identity: Technical identifier for the Player (used for routing, Ray naming)
        group_tags: Tags for group-based operations (routing, filtering)
        extras: Domain-specific configuration (passed through to implementation)

    Note:
        Proxy configuration is NOT here - it belongs to Persona, which manages
        all proxy infrastructure. Players focus purely on domain behavior.

    Example:
        PlayerConfig(
            name="Alice the Market Maker",
            identity="trader_001",
            group_tags=["market_makers", "us_equities"],
            extras={
                "capabilities": ["market_data", "order_book"],
                "risk_limit": 1000000,
                "strategy": "momentum"
            }
        )
    """

    # Required: Human-readable unique name for the Player.
    # This is the PRIMARY identifier recognized by the entire system.
    # Used for display, logging, and user-facing operations.
    name: str

    # Required: Technical identifier for the Player.
    # Used for message routing, storage keys, and Ray actor naming.
    # Can be same as name, or a more technical ID (e.g., "player_001").
    identity: str

    # Optional: Tags for group-based message routing and coordination.
    # Enables Conductor to target subsets of Players (e.g., ["market_makers"]).
    group_tags: List[str] = field(default_factory=list)

    # Optional: Domain-specific configuration for subclass implementations.
    # Common keys: "capabilities" (for resource access), "strategy", "parameters".
    extras: Dict[str, Any] = field(default_factory=dict)


class PlayerState:
    """
    Private state container for Player entities.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    PRIVACY BOUNDARY                                  │
    │                                                                      │
    │  PlayerState is INVISIBLE to:                                       │
    │    ✗ Conductor (cannot see Player's internal state)                 │
    │    ✗ Other Players (no direct state access)                         │
    │    ✗ Environment (only sees Actions, not internal reasoning)        │
    │                                                                      │
    │  This privacy is FUNDAMENTAL to multi-agent systems:                │
    │    - Enables strategic/competitive behavior                         │
    │    - Models real-world information asymmetry                        │
    │    - Prevents "cheating" by omniscient coordinators                 │
    └─────────────────────────────────────────────────────────────────────┘

    State Components:
    -----------------
    - turn_count: Number of turns executed (perceive→decide→act cycles)
    - step_count: Number of internal steps within current turn
    - last_observation: Most recent observation received
    - last_action: Most recent action generated
    - custom_state: Flexible key-value store for domain logic
    - _message_inbox: Pending messages from CommunicationProxy

    In the hierarchical execution model:
    - Simulator: round (orchestrates all entities)
    - Player: turn (one perceive→decide→act cycle)  <-- THIS STATE
    - Player internal: step (iterations within decide())
    - Conductor: cycle (receive→analyze→coordinate cycle)

    Note: This is a class (not dataclass) because it has mutable state
    that changes throughout simulation, not just configuration.
    """

    def __init__(self):
        """Initialize empty state container."""
        # Tracks how many perceive→decide→act turns have been executed.
        # Used for temporal ordering and debugging simulation progress.
        self.turn_count: int = 0

        # Caches the most recent observation received from the environment.
        # Useful for decision logic that needs to reference current inputs.
        self.last_observation: Optional[Observation] = None

        # Caches the most recent action generated by this Player.
        # Enables history-dependent strategies and debugging.
        self.last_action: Optional[Action] = None

        # Flexible key-value store for domain-specific state.
        # Subclasses use this via get_custom()/set_custom() to store
        # any data needed for their decision logic (e.g., portfolio, beliefs).
        self.custom_state: Dict[str, Any] = {}

        # Queue for incoming messages from other entities via CommunicationProxy.
        # Messages accumulate here until processed by get_pending_messages().
        # Prefixed with underscore to indicate it's managed internally.
        self._message_inbox: List["Message"] = []

        # Execution clock for turn-level timing.
        # Tracks timing metrics for the perceive→decide→act cycle.
        self.turn_clock_start: Optional[float] = None
        self.turn_last_duration_ms: float = 0.0
        self.turn_total_duration_ms: float = 0.0

        # Step tracking for internal iterations within decide().
        # Allows Players to perform multiple reasoning steps internally.
        # Example: LLM agent doing think → refine → finalize within one turn.
        self.step_count: int = 0
        self.step_clock_start: Optional[float] = None
        self.step_last_duration_ms: float = 0.0
        self.step_total_duration_ms: float = 0.0

    def turn_tick_start(self) -> None:
        """
        Mark the start of a turn execution.

        Called at the beginning of the perceive→decide→act cycle.
        """
        self.turn_clock_start = time.perf_counter()

    def turn_tick_end(self) -> None:
        """
        Mark the end of a turn and calculate duration.

        Called after completing the perceive→decide→act cycle.
        Updates timing metrics automatically.
        """
        if self.turn_clock_start is not None:
            elapsed = time.perf_counter() - self.turn_clock_start
            self.turn_last_duration_ms = elapsed * 1000.0
            self.turn_total_duration_ms += self.turn_last_duration_ms
            self.turn_clock_start = None

    # -------------------------------------------------------------------------
    # Step timing (for internal iterations within decide())
    # -------------------------------------------------------------------------

    def step_reset(self) -> None:
        """
        Reset step counters for a new turn.

        Called automatically at the start of each turn to reset
        internal step tracking.
        """
        self.step_count = 0
        self.step_total_duration_ms = 0.0
        self.step_last_duration_ms = 0.0
        self.step_clock_start = None

    def step_tick_start(self) -> None:
        """
        Mark the start of an internal step.

        Call this at the beginning of each internal iteration within decide().

        Example:
            async def decide(self) -> Dict:
                for i in range(3):
                    self.state.step_tick_start()
                    result = await self._think()
                    self.state.step_tick_end()
                return result
        """
        self.step_clock_start = time.perf_counter()

    def step_tick_end(self) -> None:
        """
        Mark the end of a step and update metrics.

        Call this after each internal iteration completes.
        Automatically increments step_count.
        """
        if self.step_clock_start is not None:
            elapsed = time.perf_counter() - self.step_clock_start
            self.step_last_duration_ms = elapsed * 1000.0
            self.step_total_duration_ms += self.step_last_duration_ms
            self.step_count += 1
            self.step_clock_start = None

    def get_step_metrics(self) -> Dict[str, Any]:
        """
        Get step timing metrics for the current turn.

        Returns:
            Dictionary with step_count and timing information.
        """
        return {
            "step_count": self.step_count,
            "step_last_duration_ms": round(self.step_last_duration_ms, 3),
            "step_total_duration_ms": round(self.step_total_duration_ms, 3),
            "step_avg_duration_ms": (
                round(self.step_total_duration_ms / self.step_count, 3)
                if self.step_count > 0
                else 0.0
            ),
        }

    def update_turn(self, observation: Observation, action: Action) -> None:
        """
        Update state after completing a turn.

        Called by BasePlayer.turn() after all steps complete.

        Args:
            observation: The observation that triggered this turn
            action: The final action generated
        """
        self.last_observation = observation
        self.last_action = action
        # Note: turn_count is incremented in turn() directly

    def update_step(self, observation: Observation, action: Action) -> None:
        """
        Update state after completing a step.

        Called by BasePlayer.step() after perceive → decide → act.

        Args:
            observation: The observation that triggered this step
            action: The action generated in response
        """
        self.last_observation = observation
        self.last_action = action
        # Note: step_count is incremented by step_tick_end()

    def get_turn_metrics(self) -> Dict[str, Any]:
        """
        Get turn timing metrics for reporting/logging.

        Returns:
            Dictionary with turn_count and timing information.
        """
        return {
            "turn_count": self.turn_count,
            "turn_last_duration_ms": round(self.turn_last_duration_ms, 3),
            "turn_total_duration_ms": round(self.turn_total_duration_ms, 3),
            "turn_avg_duration_ms": (
                round(self.turn_total_duration_ms / self.turn_count, 3)
                if self.turn_count > 0
                else 0.0
            ),
        }

    def get_custom(self, key: str) -> Any:
        """
        Get a custom state value.

        Args:
            key: State key to retrieve

        Returns:
            The stored value

        Raises:
            KeyError: If key does not exist
        """
        return self.custom_state[key]

    def has_custom(self, key: str) -> bool:
        """
        Check if a custom state key exists.

        Args:
            key: State key to check

        Returns:
            True if key exists, False otherwise
        """
        return key in self.custom_state

    def set_custom(self, key: str, value: Any) -> None:
        """
        Set a custom state value.

        Args:
            key: State key to set
            value: Value to store (must be serializable for checkpointing)
        """
        self.custom_state[key] = value


# =============================================================================
#                          BASE PLAYER CLASS
# =============================================================================
#
# This is the core abstraction that domain-specific Players extend.
# It implements the ObservableEntity protocol for proxy integration
# and defines the perceive → decide → act behavioral contract.
#
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
    ║      ┌─────────────────────────────────────────────────────────┐   ║
    ║      │                                                          │   ║
    ║      │   Observation ──► perceive() ──► Internal State Update  │   ║
    ║      │                                                          │   ║
    ║      │   Internal State ──► decide() ──► Decision Payload      │   ║
    ║      │                                                          │   ║
    ║      │   Decision Payload ──► act() ──► Action                 │   ║
    ║      │                                                          │   ║
    ║      └─────────────────────────────────────────────────────────┘   ║
    ║                                                                      ║
    ╚═════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │                  OBSERVABLEENTITY PROTOCOL                           │
    │                                                                      │
    │  BasePlayer implements the ObservableEntity protocol, which defines │
    │  the MINIMAL INTERFACE that proxies can access:                     │
    │                                                                      │
    │    Property/Method         │ Used By              │ Purpose          │
    │    ────────────────────────┼──────────────────────┼─────────────────│
    │    identity                │ All proxies          │ Entity ID        │
    │    on_message()            │ CommunicationProxy   │ Message callback │
    │    save_state()            │ StorageProxy         │ State snapshot   │
    │    load_state()            │ StorageProxy         │ State restore    │
    │    get_capabilities()      │ ResourceProxy        │ Access control   │
    │                                                                      │
    │  This is ACCESS CONTROL - proxies cannot access private methods     │
    │  like _internal_strategy() or _compute_decision().                  │
    └─────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────┐
    │                      PERSONA INTEGRATION                             │
    │                                                                      │
    │  Player accesses ALL infrastructure through Persona (Facade):       │
    │                                                                      │
    │      BasePlayer (What: Pure Domain Logic)                           │
    │          │                                                          │
    │          └── _persona ──► PlayerPersona (When: Coordination)       │
    │                               │                                     │
    │                               ├── communication ─→ Message routing │
    │                               ├── storage ───────→ Checkpointing   │
    │                               ├── resource ──────→ MCP resources   │
    │                               └── observability ─→ Metrics/logging │
    │                                                                      │
    │  Key Design Decisions:                                              │
    │    1. SINGLE INTERFACE: set_persona() instead of four attach_*()   │
    │    2. COMPLETE DECOUPLING: Player has ZERO proxy references        │
    │    3. PURE DOMAIN LOGIC: No logging, metrics, or infra code        │
    │    4. LIFECYCLE HOOKS: Persona handles observability externally    │
    └─────────────────────────────────────────────────────────────────────┘

    Role Boundary Verification:
    ---------------------------
    To verify Player is correctly scoped, ask: "What breaks if removed?"

    1. Remove Player → Environment cannot receive valid Actions ✓
    2. Player output (Action) is directly interpreted by environment ✓
    3. Player state is invisible to Conductor (private) ✓

    If Player could be removed without breaking environment interaction,
    the role boundary is incorrectly defined.

    Subclass Implementation Guide:
    ------------------------------
    Subclasses MUST implement three abstract methods:

    1. perceive(observation) - Process incoming observation
       - Update internal state based on new information
       - DO NOT return anything (side-effect only)

    2. decide() -> PayloadType - Make a decision
       - Read internal state
       - Return decision parameters (not Action yet)

    3. act(decision_payload) -> Action - Create the Action
       - Transform decision into Action object
       - This is where action_type is determined

    Why split into three methods?
    - Separation of concerns (input/compute/output)
    - Easier testing (can test decision logic independently)
    - Extensibility (can override just one phase)

    Example Implementation:
        class MyPlayer(BasePlayer):
            async def perceive(
                self,
                obs: Observation,
                prev_result: Optional[StepResult] = None,
            ) -> None:
                self.state.set_custom("price", obs.data["price"])
                if prev_result:
                    self.state.set_custom("last_action", prev_result.action)

            async def decide(self) -> Dict[str, Any]:
                price = self.state.get_custom("price")
                return {"action": "buy" if price < 100 else "hold"}

            async def act(self, decision: Dict[str, Any]) -> Action:
                return Action(
                    action_type=decision["action"],
                    payload=decision,
                    source_id=self.identity
                )

    Multi-Step Example (internal iterations within decide):
        class LLMPlayer(BasePlayer):
            async def decide(self) -> Dict[str, Any]:
                # Multiple internal reasoning steps within a turn
                for iteration in range(3):
                    self.state.step_tick_start()
                    thought = await self._think(iteration)
                    self.state.step_tick_end()

                    if thought["confident"]:
                        break

                return thought

        # After turn(), TurnResult will include:
        # - tick_step_count: number of iterations (e.g., 2)
        # - tick_step_total_duration_ms: total thinking time
    """

    def __init__(self, config: PlayerConfig):
        """
        Initialize the BasePlayer with configuration.

        Args:
            config: PlayerConfig containing identity, tags, and settings

        Note:
            Proxies are NOT created here (explicit attachment pattern).
            The Player is fully functional without any proxies, just with
            reduced capabilities (no messaging, no storage, etc.).
        """
        # =====================================================================
        # Core Identity
        # =====================================================================
        # Human-readable unique name for the Player.
        # This is the PRIMARY identifier recognized by the entire system.
        self._name: str = config.name

        # Technical identifier used for message routing, storage keys, Ray naming.
        self._identity: str = config.identity

        # Tags for group-based message routing and coordination.
        # Copied to prevent mutation of original config.
        self.group_tags: List[str] = config.group_tags.copy()

        # Full config retained for reference by subclasses.
        # May contain domain-specific settings in 'extras'.
        self.config: PlayerConfig = config

        # =====================================================================
        # Private State Container
        # =====================================================================
        # PlayerState holds ALL internal state. This encapsulation ensures
        # that state access goes through well-defined interfaces.
        self.state: PlayerState = PlayerState()

        # =====================================================================
        # Capability Tags (for access control via Persona)
        # =====================================================================
        # Capabilities define which MCP resources this Player can access.
        # The Client's ResourceProxy checks capabilities before allowing fetch.
        if "capabilities" in config.extras:
            self._capabilities: List[str] = config.extras["capabilities"].copy()
        else:
            self._capabilities: List[str] = []

        # =====================================================================
        # Lifecycle Flags
        # =====================================================================
        # Tracks whether initialize() has been called.
        # Some operations (e.g., turn()) require initialization first.
        self._is_initialized: bool = False

        # Tracks whether the Player is actively participating in simulation.
        # Set to True during run, False after shutdown.
        self._is_running: bool = False

        # =====================================================================
        # Persona Layer Reference (Infrastructure Facade)
        # =====================================================================
        # The Persona Layer is the ONLY infrastructure interface for Player.
        # Player has NO direct proxy references - all infrastructure access
        # goes through the Persona.
        #
        # Three-Layer Model (Complete Decoupling):
        #   ┌─────────────────────────────────────────────┐
        #   │ Player (What): Pure domain logic              │
        #   │   - perceive() / decide() / act()             │
        #   │   - NO proxy knowledge, NO infra code         │
        #   └──────────────────────┬──────────────────────┘
        #                          │ player.persona.xxx()
        #   ┌──────────────────────▼──────────────────────┐
        #   │ Persona (When): Infrastructure coordination   │
        #   │   - Manages all proxies internally            │
        #   └──────────────────────┬──────────────────────┘
        #                          │ proxy.xxx()
        #   ┌──────────────────────▼──────────────────────┐
        #   │ Proxy (How): Infrastructure primitives        │
        #   │   - Communication, Storage, Resource, etc.    │
        #   └─────────────────────────────────────────────┘
        # =====================================================================
        self._persona: Optional["PlayerPersona"] = None

    # =========================================================================
    #          OBSERVABLEENTITY PROTOCOL IMPLEMENTATION
    # =========================================================================
    # These methods define the MINIMAL INTERFACE that proxies can access.
    # This is ACCESS CONTROL - proxies cannot call private methods.
    # =========================================================================

    @property
    def identity(self) -> str:
        """
        Technical identifier for this Player.

        Used by:
            - All proxies (for logging, routing, storage keys)
            - Simulator (for actor naming)
            - Message routing (sender_id, recipient_id)

        Returns:
            The unique identity string
        """
        return self._identity

    @property
    def name(self) -> str:
        """
        Human-readable unique name for this Player.

        This is the PRIMARY identifier recognized by the entire system.
        Used for display, logging, and user-facing operations.

        Returns:
            The unique name string
        """
        return self._name

    def get_name(self) -> str:
        """
        Get the unique name of this Player.

        This is the unique identifier recognized by the entire simulation system.
        Equivalent to accessing the `name` property.

        Returns:
            The unique name string
        """
        return self._name

    def on_message(self, message: "Message") -> None:
        """
        Callback invoked when a message is received via CommunicationProxy.

        This is part of the ObservableEntity protocol. The CommunicationProxy
        calls this method when a message arrives for this Player.

        Default Behavior:
            Stores message in _message_inbox for later processing.
            Subclasses can override for immediate message handling.

        Args:
            message: The received Message object

        Example Override:
            def on_message(self, message: Message) -> None:
                if message.message_type == MessageType.COORDINATION:
                    self._apply_coordination(message.payload)
                else:
                    super().on_message(message)  # Default handling
        """
        self.state._message_inbox.append(message)

    def save_state(self) -> Dict[str, Any]:
        """
        Return state that should be persisted by StorageProxy.

        This is part of the ObservableEntity protocol. The StorageProxy
        calls this method when creating a checkpoint.

        What to Include:
            - Turn count (for simulation position)
            - Custom state (domain-specific data)
            - Any state needed to resume from checkpoint

        What NOT to Include:
            - Proxy references (not serializable)
            - Transient computation caches
            - Large data that can be reconstructed

        Returns:
            Dictionary of serializable state data

        Override Example:
            def save_state(self) -> Dict[str, Any]:
                base = super().save_state()
                base["portfolio"] = self._portfolio.to_dict()
                base["strategy_params"] = self._strategy.params
                return base
        """
        return {
            "turn_count": self.state.turn_count,
            "custom_state": self.state.custom_state.copy(),
        }

    def get_saveable_state(self) -> Dict[str, Any]:
        """
        Alias for save_state() for backward compatibility.

        Deprecated: Use save_state() instead.
        """
        return self.save_state()

    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Restore state from persisted data.

        This is part of the ObservableEntity protocol. The StorageProxy
        calls this method when restoring from a checkpoint.

        Args:
            state: Dictionary of state data (from save_state())

        Note:
            Must validate all expected keys are present.
            State dict may be from an older version with different keys.
            Supports both 'turn_count' (new) and 'step_count' (legacy).

        Override Example:
            def load_state(self, state: Dict[str, Any]) -> None:
                super().load_state(state)
                if "portfolio" in state:
                    self._portfolio = Portfolio.from_dict(state["portfolio"])
        """
        # Support both new 'turn_count' and legacy 'step_count' keys
        if "turn_count" in state:
            self.state.turn_count = state["turn_count"]
        elif "step_count" in state:
            self.state.turn_count = state["step_count"]
        else:
            raise KeyError("State must contain 'turn_count' or 'step_count'")

        self.state.custom_state = state["custom_state"].copy()

    def get_capabilities(self) -> List[str]:
        """
        Return capability tags for ResourceProxy access control.

        Capabilities define which MCP resources this Player can access.
        The ResourceProxy checks capabilities before allowing resource fetch.

        Access Control Flow:
            1. Player calls fetch_resource("mcp://server/resource")
            2. ResourceProxy checks if Player has required capability
            3. If capability missing → ProxyResult.fail("ACCESS_DENIED")

        Returns:
            List of capability tags (copy to prevent modification)

        Override Example:
            def get_capabilities(self) -> List[str]:
                base = super().get_capabilities()
                if self._is_premium_user:
                    base.append("premium_data")
                return base
        """
        return self._capabilities.copy()

    # =========================================================================
    #                     PERSONA LAYER (SOLE INFRASTRUCTURE ACCESS)
    # =========================================================================
    # Player accesses ALL infrastructure through Persona - no direct proxy access.
    #
    # Benefits of this design:
    # 1. COMPLETE DECOUPLING: Player code is 100% domain logic
    # 2. SINGLE INTERFACE: One set_persona() instead of four attach_*_proxy()
    # 3. TESTABILITY: Mock one Persona instead of four proxies
    # =========================================================================

    @property
    def persona(self) -> Optional["PlayerPersona"]:
        """
        Get the attached PlayerPersona (sole infrastructure interface).

        Returns:
            PlayerPersona if attached, None otherwise
        """
        return self._persona

    def set_persona(self, persona: "PlayerPersona") -> None:
        """
        Attach a PlayerPersona as the sole infrastructure interface.

        Args:
            persona: The PlayerPersona instance to attach

        Example:
            player = MyPlayer(config)
            persona = PlayerPersona(
                player,
                storage_proxy=StorageProxy(),
                resource_proxy=ResourceProxy(),
            )
            player.set_persona(persona)

            # Player uses Persona for all infrastructure
            data = await player.persona.fetch_resource("mcp://market/prices")
        """
        self._persona = persona

    # =========================================================================
    #                           LIFECYCLE
    # =========================================================================
    # Three-phase lifecycle: Initialize → Running → Shutdown
    #
    # Phase 1: INITIALIZE
    #   - Called once before simulation starts
    #   - Set up internal resources, load models, etc.
    #   - Proxies should be attached BEFORE this call
    #
    # Phase 2: RUNNING
    #   - Main simulation loop (turn() called repeatedly)
    #   - State changes through perceive/decide/act cycle
    #
    # Phase 3: SHUTDOWN
    #   - Called once when simulation ends
    #   - Clean up resources, persist final state
    # =========================================================================

    async def initialize(self) -> None:
        """
        Initialize the Player for simulation.

        Called once before the simulation loop begins. Override this to:
            - Load ML models
            - Initialize connections
            - Set up internal data structures

        Note:
            Client should be attached BEFORE calling initialize().
            This method can use Client if attached.

        Override Example:
            async def initialize(self) -> None:
                await super().initialize()
                self._model = await self._load_model()
                self.state.set_custom("model_loaded", True)
        """
        self._is_initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown the Player after simulation.

        Called once when simulation ends. Override this to:
            - Persist final state
            - Close connections
            - Release resources

        Override Example:
            async def shutdown(self) -> None:
                await self.client.checkpoint(label="final")
                await super().shutdown()
        """
        self._is_running = False

    # =========================================================================
    #              CORE BEHAVIORAL CONTRACT (ABSTRACT METHODS)
    # =========================================================================
    # These three methods define the Player's decision-making process.
    # Subclasses MUST implement all three.
    #
    # Decision Cycle:
    #
    #     ┌─────────────────────────────────────────────────────────┐
    #     │  PERCEIVE                                               │
    #     │    Input: Observation from environment                  │
    #     │    Output: None (side-effect: update internal state)   │
    #     └─────────────────────────────────────────────────────────┘
    #                              │
    #                              ▼
    #     ┌─────────────────────────────────────────────────────────┐
    #     │  DECIDE                                                 │
    #     │    Input: Internal state (implicit)                    │
    #     │    Output: Decision payload (what to do)               │
    #     └─────────────────────────────────────────────────────────┘
    #                              │
    #                              ▼
    #     ┌─────────────────────────────────────────────────────────┐
    #     │  ACT                                                    │
    #     │    Input: Decision payload                             │
    #     │    Output: Action (sent to environment)                │
    #     └─────────────────────────────────────────────────────────┘
    #
    # Why Three Separate Methods?
    # - SEPARATION OF CONCERNS: Each method has single responsibility
    # - TESTABILITY: Can test decision logic without environment
    # - EXTENSIBILITY: Can override single phase without touching others
    # - DEBUGGING: Clear breakpoints for each phase
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
        information from the environment. It should NOT make decisions.

        Args:
            observation: The observation data from environment
            prev_result: Result from the previous step (None for first step).
                         Use this to access previous action/decision for
                         multi-step reasoning.

        Implementation Guidelines:
            1. Extract relevant information from observation.data
            2. Optionally use prev_result for multi-step context
            3. Update internal state via self.state.set_custom()
            4. DO NOT return anything (side-effect only)
            5. DO NOT make decisions here (that's decide()'s job)

        Example:
            async def perceive(
                self,
                observation: Observation,
                prev_result: Optional[StepResult] = None,
            ) -> None:
                market_data = observation.data["market"]
                self.state.set_custom("current_prices", market_data)

                # Use previous step result if available
                if prev_result is not None:
                    self.state.set_custom("last_action", prev_result.action)
        """
        raise NotImplementedError

    @abstractmethod
    async def decide(self) -> PayloadType:
        """
        Make a decision based on current internal state.

        This method contains the core decision-making logic. It reads
        the internal state and determines what action to take.

        Returns:
            Decision payload that will be passed to act().
            This is NOT yet an Action - just the decision parameters.

        Implementation Guidelines:
            1. Read state via self.state.get_custom()
            2. Apply decision logic (rules, ML model, optimization)
            3. Return decision parameters (dict, array, etc.)
            4. DO NOT create Action here (that's act()'s job)

        Example:
            async def decide(self) -> Dict[str, Any]:
                prices = self.state.get_custom("current_prices")

                # Simple momentum strategy
                if prices["trend"] == "up":
                    return {"action": "buy", "quantity": 100}
                else:
                    return {"action": "hold", "quantity": 0}
        """
        raise NotImplementedError

    @abstractmethod
    async def act(self, decision_payload: PayloadType) -> Action:
        """
        Execute the decision and produce an Action.

        This method transforms the decision payload into a concrete
        Action that can be sent to the environment.

        Args:
            decision_payload: The output from decide()

        Returns:
            Action object ready for environment execution

        Implementation Guidelines:
            1. Determine action_type from decision_payload
            2. Create Action with appropriate payload
            3. Set source_id to self.identity
            4. Add any metadata needed for execution

        Example:
            async def act(self, decision: Dict[str, Any]) -> Action:
                return Action(
                    action_type=decision["action"],
                    payload={
                        "quantity": decision["quantity"],
                        "limit_price": decision["price"]
                    },
                    source_id=self.identity,
                    metadata={"strategy": "momentum"}
                )
        """
        raise NotImplementedError

    # =========================================================================
    #                        MAIN EXECUTION
    # =========================================================================

    async def step(
        self,
        observation: Observation,
        prev_result: Optional["StepResult"] = None,
    ) -> "StepResult":
        """
        Execute one atomic step: perceive → decide → act.

        This is the fundamental unit of Player execution. Each step:
        1. Processes an observation (perceive)
        2. Makes a decision (decide)
        3. Produces an action (act)

        The turn() method calls step() multiple times to execute
        multiple steps within a single turn, passing each step's result
        to the next step.

        Args:
            observation: The current observation from environment
            prev_result: Result from the previous step (None for first step)

        Returns:
            StepResult containing:
                - decision_payload: Raw output from decide()
                - action: The Action to be executed
                - tick_step_count: Which step this is
                - tick_step_duration_ms: Duration of this step

        Note:
            This method is typically NOT overridden. Override the three
            abstract methods (perceive, decide, act) instead.
        """
        # Start step timing
        self.state.step_tick_start()

        # Phase 1: Update internal state based on observation and prev result.
        await self.perceive(observation, prev_result)

        # Phase 2: Apply decision logic to generate action parameters.
        decision_payload = await self.decide()

        # Phase 3: Transform decision payload into a concrete Action.
        action = await self.act(decision_payload)

        # Update internal state tracking
        self.state.update_step(observation, action)

        # End step timing
        self.state.step_tick_end()

        return StepResult(
            decision_payload=decision_payload,
            action=action,
            tick_step_count=self.state.step_count,
            tick_step_duration_ms=self.state.step_last_duration_ms,
        )

    def prepare_observation(
        self,
        conductor_notify: Dict[str, Any],
        round_num: int,
    ) -> Observation:
        """
        Prepare the Observation for this turn.

        This method constructs the Observation object from raw inputs.
        Override to customize how the Player interprets incoming data.

        Args:
            conductor_notify: Notification dict from Conductor
            round_num: Current simulation round number

        Returns:
            Observation with local perception and conductor signals
        """
        return Observation(
            local=LocalObservation(data={}),
            conductor_notify=conductor_notify,
            round=round_num,
        )

    async def turn(
        self,
        conductor_notify: Dict[str, Any],
        round_num: int,
        num_steps: int = 1,
    ) -> "TurnResult":
        """
        Execute a turn consisting of multiple steps.

        In the hierarchical execution model:
        - Simulator: round (orchestrates all entities)
        - Player: turn (contains multiple steps)  <-- THIS METHOD
        - Player: step (one perceive-decide-act cycle)
        - Conductor: cycle (receive-analyze-coordinate)

        This is the main entry point called by PlayerPersona each round.
        It first prepares the observation, then executes multiple steps
        in sequence.

        Example:
            result = await player.turn(conductor_notify, round_num, num_steps=3)
            for step_result in result.step_results:
                logger.debug("Step %d: %s", step_result.tick_step_count, step_result.action)

        Args:
            conductor_notify: Notification dict from Conductor
            round_num: Current simulation round number
            num_steps: Number of steps to execute in this turn (default: 1)

        Returns:
            TurnResult containing:
                - step_results: List of StepResult from each step
                - final_action: The last action produced
                - tick_turn_count: The turn number
                - tick_turn_duration_ms: Total duration of this turn
                - tick_step_count: Number of steps executed
        """
        # Prepare observation (Player's responsibility)
        observation = self.prepare_observation(conductor_notify, round_num)

        # Start turn timing
        self.state.turn_tick_start()

        step_results: List[StepResult] = []
        current_observation = observation
        prev_result: Optional[StepResult] = None

        # Execute multiple steps within this turn
        for _ in range(num_steps):
            step_result = await self.step(current_observation, prev_result)
            step_results.append(step_result)

            # Update for next iteration
            prev_result = step_result
            current_observation = self._update_observation_for_next_step(
                current_observation, step_result
            )

        # Update turn count
        self.state.turn_count += 1

        # End turn timing
        self.state.turn_tick_end()

        return TurnResult(
            step_results=step_results,
            final_action=step_results[-1].action if step_results else None,
            tick_turn_count=self.state.turn_count,
            tick_turn_duration_ms=self.state.turn_last_duration_ms,
            tick_turn_total_duration_ms=self.state.turn_total_duration_ms,
            tick_step_count=len(step_results),
        )

    def _update_observation_for_next_step(
        self,
        current_observation: Observation,
        step_result: "StepResult",
    ) -> Observation:
        """
        Update observation for the next step based on the previous action.

        Override this method to implement multi-step dynamics where each
        step's observation depends on the previous step's action.

        Default behavior: Return the same observation unchanged.

        Args:
            current_observation: The observation used in the previous step
            step_result: The result from the previous step

        Returns:
            The observation to use for the next step
        """
        return current_observation

    # =========================================================================
    #                      MESSAGE HANDLING
    # =========================================================================

    def get_pending_messages(self) -> List["Message"]:
        """
        Get and clear pending messages from inbox.

        Messages are accumulated in the inbox via on_message() callback.
        This method retrieves all pending messages and clears the inbox.

        Returns:
            List of pending Message objects (inbox is cleared)

        Usage:
            Typically called at the start of decide() to incorporate
            messages into decision-making:

            async def decide(self) -> Dict[str, Any]:
                messages = self.get_pending_messages()
                for msg in messages:
                    if msg.message_type == MessageType.COORDINATION:
                        self._apply_coordination(msg.payload)
                # ... rest of decision logic
        """
        messages = self.state._message_inbox.copy()
        self.state._message_inbox.clear()
        return messages

    # =========================================================================
    #                          UTILITY
    # =========================================================================

    def get_state(self) -> PlayerState:
        """
        Get the private state container.

        This provides direct access to the PlayerState object.
        Use with caution - this bypasses the save_state/load_state
        protocol methods.

        Returns:
            The internal PlayerState object

        Note:
            Primarily for internal use and testing.
            Prefer save_state()/load_state() for persistence.
        """
        return self.state

    def in_group(self, tag: str) -> bool:
        """
        Check if this Player belongs to a specific group.

        Groups enable:
            - Targeted message broadcasting
            - Scoped coordination decisions
            - Filtering in queries

        Args:
            tag: Group tag to check

        Returns:
            True if Player belongs to the group

        Example:
            if player.in_group("market_makers"):
                # Apply market maker-specific logic
                pass
        """
        return tag in self.group_tags

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Player(id={self.identity}, groups={self.group_tags})"
