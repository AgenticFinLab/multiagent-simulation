"""Base Conductor module for the Multi-Agent Simulation (MASim) framework.

This module provides abstract base classes and type definitions ONLY.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Enums:
    DecisionScope        - Scope of coordination: GLOBAL, GROUP, INDIVIDUAL

Dataclasses:
    CoordinationDecision - Behavioral output: decision_type, scope, parameters
    CycleResult          - Result of one cycle: decision, census_size, timing
    ConductorConfig      - Configuration: identity, coordination_mode, extras

Classes:
    ConductorState       - Globally visible state (census, player_registry)
    BaseConductor        - Abstract base class for all Conductor implementations

For concrete implementations, see general.py:
    GeneralConductor     - Configurable coordination logic
    PassThroughConductor - No coordination, passes through
    ThrottlingConductor  - Applies throttling based on activity
    BroadcastConductor   - Broadcasts decisions to all players

================================================================================
                         DESIGN PHILOSOPHY
================================================================================

- Conductor is defined by its behavioral OUTPUT contract: it generates CoordinationDecisions
- Conductor CANNOT directly act on environment - only influences Players indirectly
- Census-based fusion: collects outputs (census) from Players, then analyzes and coordinates
- State is globally visible (unlike Player's private state)

================================================================================
                        CONDUCTOR CONTRACT
================================================================================

Four abstract methods define the Conductor's behavior:

    notify(round_num, player_ids) → Dict[str, Dict]
        Notify players of round state (Conductor → Players)
        Called BEFORE players act

    collect_census(actions) → None
        Gather actions from Players (Players → Conductor)
        Called AFTER players act

    analyze() → Dict[str, Any]
        Process the collected census

    coordinate(analysis_result) → CoordinationDecision
        Produce CoordinationDecision based on analysis

================================================================================
                          EXECUTION FLOW
================================================================================

Conductor is called by ConductorPersona (which is called by Simulator):

Round Flow:
│
├── Phase 1: NOTIFICATION
│   └── ConductorPersona.notify(round_num, player_ids)
│       └── Conductor.notify()  [internal]
│           └── Returns: Dict[player_id → notification_dict]
│
├── Phase 2: PLAYER_DECISION
│   └── (Players act based on notifications)
│
├── Phase 3: COORDINATION
│   ├── ConductorPersona.receive_actions(actions)
│   │   └── Conductor.on_action_received()  # Builds census
│   │
│   └── ConductorPersona.cycle()
│       └── Conductor.cycle()  [internal]
│           ├── collect_census()   ── Clear and process buffered actions
│           ├── analyze()          ── Analyze census and system state
│           └── coordinate()       ── Produce CoordinationDecision
│           └── Returns: CycleResult
│
└── Phase 4: COMPLETE
    └── Broadcast coordination decision to all players

================================================================================
                     HIERARCHICAL EXECUTION MODEL
================================================================================

- Simulator: round (orchestrates all entities)
- PlayerPersona: operate (calls Player.turn internally)
- Player: turn (for loop calling step)
- Player: step (perceive→decide→act)
- ConductorPersona: cycle (calls Conductor.cycle internally)  <-- THIS MODULE
"""

import time
import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from masim.player.base import Action

if TYPE_CHECKING:
    from masim.communication.base import Message
    from masim.persona.base import ConductorPersona


# =============================================================================
# Enums
# =============================================================================


class DecisionScope(Enum):
    """Scope of a coordination decision's effect."""

    GLOBAL = "all"
    GROUP = "group"
    INDIVIDUAL = "entity"


# =============================================================================
# Core Data Types
# =============================================================================


@dataclass
class CoordinationDecision:
    """
    The behavioral output contract for Conductor entities.

    A CoordinationDecision represents a directive that indirectly influences
    system dynamics. Unlike Actions, CoordinationDecisions are NOT directly
    interpreted by the environment.
    """

    decision_type: str
    scope: DecisionScope
    parameters: Dict[str, Any]
    source_id: str
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scope_target: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._validate_scope()

    def _validate_scope(self) -> None:
        if self.scope in (DecisionScope.GROUP, DecisionScope.INDIVIDUAL):
            if not self.scope_target:
                raise ValueError(
                    f"scope_target must be specified for {self.scope.name} scope"
                )

    def get_scope_string(self) -> str:
        if self.scope == DecisionScope.GLOBAL:
            return "all"
        return f"{self.scope.value}:{self.scope_target}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "scope": self.scope.value,
            "scope_target": self.scope_target,
            "parameters": self.parameters,
            "source_id": self.source_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class CycleResult:
    """
    Result container for a Conductor's coordination cycle.

    Similar to StepResult/TurnResult for Player, this encapsulates the
    output of a single coordination cycle.

    Attributes:
        decision: The CoordinationDecision generated
        census_size: Number of Actions collected in the census
        analysis_result: Output from the analyze() phase (for debugging)
        tick_cycle_count: Which cycle this is (1-indexed)
        tick_cycle_duration_ms: Duration of this cycle in milliseconds
    """

    decision: CoordinationDecision
    census_size: int = 0
    analysis_result: Dict[str, Any] = field(default_factory=dict)
    tick_cycle_count: int = 0
    tick_cycle_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.to_dict(),
            "census_size": self.census_size,
            "analysis_result": self.analysis_result,
            "tick_cycle_count": self.tick_cycle_count,
            "tick_cycle_duration_ms": round(self.tick_cycle_duration_ms, 3),
        }


# =============================================================================
# Configuration and State
# =============================================================================


@dataclass
class ConductorConfig:
    """
    Configuration for Conductor initialization.

    Note:
        Proxy configuration is NOT here - it belongs to Persona, which manages
        all proxy infrastructure. Conductors focus purely on coordination logic.
    """

    identity: str
    coordination_mode: str = "centralized"
    extras: Dict[str, Any] = field(default_factory=dict)


class ConductorState:
    """
    State container for Conductor entities.

    Unlike PlayerState, ConductorState is GLOBALLY VISIBLE.
    Other components can query Conductor state for transparency.

    Key Concepts:
    - census: Aggregated data collected from Players (Actions buffer)
    - cycle: One complete notify→collect→analyze→coordinate sequence

    In the hierarchical execution model:
    - cycle_count: Number of coordination cycles completed
    - cycle_clock: Timing metrics for cycle execution
    """

    def __init__(self):
        # Number of coordination cycles completed.
        # Incremented after each successful cycle execution.
        self.cycle_count: int = 0

        # Registry of Players known to this Conductor.
        # Maps player_id → metadata for coordination targeting.
        self.player_registry: Dict[str, Dict[str, Any]] = {}

        # Census: Actions collected from Players during current round.
        # "Census" emphasizes this is aggregated data from multiple Players.
        # Cleared at start of each coordination cycle.
        self.census: List[Action] = []

        # History of all CoordinationDecisions generated.
        # Used for analysis and debugging.
        self.decision_history: List[CoordinationDecision] = []

        # Flexible key-value store for domain-specific state.
        self.custom_state: Dict[str, Any] = {}

        # Queue for incoming messages from other entities.
        self._message_inbox: List["Message"] = []

        # Execution clock for cycle-level timing.
        # Tracks: count, start_time, last_duration_ms, total_duration_ms.
        self.cycle_clock_start: Optional[float] = None
        self.cycle_last_duration_ms: float = 0.0
        self.cycle_total_duration_ms: float = 0.0

    def register_player(self, player_id: str, metadata: Dict[str, Any] = None) -> None:
        self.player_registry[player_id] = metadata or {}

    def unregister_player(self, player_id: str) -> None:
        self.player_registry.pop(player_id, None)

    def add_to_census(self, action: Action) -> None:
        """Add an action to the census."""
        self.census.append(action)

    def clear_census(self) -> List[Action]:
        """Clear and return the current census."""
        actions = self.census.copy()
        self.census.clear()
        return actions

    def record_decision(self, decision: CoordinationDecision) -> None:
        """Record a decision and update cycle metrics."""
        self.decision_history.append(decision)
        self.cycle_count += 1

    def cycle_tick_start(self) -> None:
        """Mark the start of a cycle execution."""
        self.cycle_clock_start = time.perf_counter()

    def cycle_tick_end(self) -> None:
        """Mark the end of a cycle and calculate duration."""
        if self.cycle_clock_start is not None:
            elapsed = time.perf_counter() - self.cycle_clock_start
            self.cycle_last_duration_ms = elapsed * 1000.0
            self.cycle_total_duration_ms += self.cycle_last_duration_ms
            self.cycle_clock_start = None

    def to_snapshot(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "player_count": len(self.player_registry),
            "player_ids": list(self.player_registry.keys()),
            "census_size": len(self.census),
            "decisions_made": len(self.decision_history),
            "cycle_last_duration_ms": round(self.cycle_last_duration_ms, 3),
            "cycle_total_duration_ms": round(self.cycle_total_duration_ms, 3),
            "custom_state": self.custom_state.copy(),
        }


# =============================================================================
# Base Conductor Class
# =============================================================================


class BaseConductor(ABC):
    """
    Abstract base class for all Conductor entities.

    A Conductor is defined by its behavioral contract: it receives Action
    streams from Players and generates CoordinationDecisions that indirectly
    influence system dynamics.

    Implements ObservableEntity Protocol:
    - identity: Unique identifier
    - on_message(): Callback for message receipt
    - save_state(): Return persistable state (globally visible)
    - load_state(): Restore from persisted state
    - get_capabilities(): Return capability tags for resource access
    - get_system_metrics(): Return system-level metrics (Conductor-specific)

    Role Boundary Verification:
    1. Remove Conductor → System degrades to non-coordinated mode (still runnable)
    2. Conductor output is interpreted by Players as behavior adjustment signals
    3. Conductor state is globally visible (no private state)

    Contract Constraint:
    - Conductor MUST NOT generate outputs that directly act on environment

    Proxy Design:
    - Proxies are explicitly attached (not auto-created)
    - All proxy operations support graceful degradation
    """

    def __init__(self, config: ConductorConfig):
        self._identity: str = config.identity
        self.coordination_mode: str = config.coordination_mode
        self.config: ConductorConfig = config
        self._state: ConductorState = ConductorState()

        # Capability tags for resource access control (via Client)
        if "capabilities" in config.extras:
            self._capabilities: List[str] = config.extras["capabilities"].copy()
        else:
            self._capabilities: List[str] = []

        # Lifecycle flags
        self._is_initialized: bool = False
        self._is_running: bool = False

        # Persona layer reference (SOLE infrastructure interface)
        # Conductor has NO direct proxy references - all infra via Persona
        self._persona: Optional["ConductorPersona"] = None

    # =========================================================================
    # ObservableEntity Protocol Implementation
    # =========================================================================

    @property
    def identity(self) -> str:
        """Unique identifier for the entity."""
        return self._identity

    def on_message(self, message: "Message") -> None:
        """
        Callback when a message is received via CommunicationProxy.
        """
        self._state._message_inbox.append(message)

    def save_state(self) -> Dict[str, Any]:
        """
        Return state that should be persisted by StorageProxy.

        For Conductor, this includes global coordination state.
        Uses 'cycle_count' per hierarchical execution terminology.
        """
        return {
            "cycle_count": self._state.cycle_count,
            "player_registry": self._state.player_registry.copy(),
            "custom_state": self._state.custom_state.copy(),
            # Note: decision_history may be too large; subclass can override
        }

    # Alias for backward compatibility
    def get_saveable_state(self) -> Dict[str, Any]:
        """Alias for save_state() for backward compatibility."""
        return self.save_state()

    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Restore state from persisted data.

        Supports both 'cycle_count' (new) and 'round_count' (legacy) for compatibility.

        Raises:
            KeyError: If required keys are missing from state
        """
        # Support both new and legacy key names
        if "cycle_count" in state:
            self._state.cycle_count = state["cycle_count"]
        elif "round_count" in state:
            self._state.cycle_count = state["round_count"]
        else:
            raise KeyError("State must contain 'cycle_count' or 'round_count'")

        self._state.player_registry = state["player_registry"].copy()
        self._state.custom_state = state["custom_state"].copy()

    def get_capabilities(self) -> List[str]:
        """
        Return capability tags for ResourceProxy access control.

        Conductor typically has broader resource access than Players.
        """
        return self._capabilities.copy()

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Return system-level metrics (Conductor-specific, for ObservabilityProxy).

        This is only available on Conductor, not Player (access control boundary).
        Uses 'cycle_count' per hierarchical execution terminology.
        """
        return {
            "cycle_count": self._state.cycle_count,
            "player_count": len(self._state.player_registry),
            "census_size": len(self._state.census),
            "total_decisions": len(self._state.decision_history),
            "cycle_last_duration_ms": round(self._state.cycle_last_duration_ms, 3),
            "cycle_total_duration_ms": round(self._state.cycle_total_duration_ms, 3),
        }

    # =========================================================================
    # Persona Layer (SOLE Infrastructure Interface)
    # =========================================================================

    @property
    def persona(self) -> Optional["ConductorPersona"]:
        """Get the attached ConductorPersona (sole infrastructure interface)."""
        return self._persona

    def set_persona(self, persona: "ConductorPersona") -> None:
        """
        Attach a ConductorPersona as the sole infrastructure interface.

        Args:
            persona: The ConductorPersona instance to attach
        """
        self._persona = persona

    # =========================================================================
    # Player Management
    # =========================================================================

    def register_player(self, player_id: str, metadata: Dict[str, Any] = None) -> None:
        """Register a Player with this Conductor."""
        self._state.register_player(player_id, metadata)

    def unregister_player(self, player_id: str) -> None:
        """Unregister a Player from this Conductor."""
        self._state.unregister_player(player_id)

    def get_registered_players(self) -> List[str]:
        """Get list of registered Player IDs."""
        return list(self._state.player_registry.keys())

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def initialize(self) -> None:
        """Initialize the Conductor. Can be overridden by subclasses."""
        self._is_initialized = True

    async def shutdown(self) -> None:
        """Shutdown the Conductor. Can be overridden by subclasses."""
        self._is_running = False

    # =========================================================================
    # Core Behavioral Contract (Abstract)
    # =========================================================================

    @abstractmethod
    def notify(
        self,
        round_num: int,
        player_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Notify players of round state (Conductor → Players).

        This is the outbound communication from Conductor to Players.
        The Conductor decides what each player should "see" this round.

        Args:
            round_num: Current simulation round
            player_ids: List of player IDs to notify

        Returns:
            Dict of player_id -> notification_dict with required keys:
            - data: Dict of data for the player
            - source_id: Source entity ID (typically self.identity)
            - num_steps: Number of steps for this turn
        """
        raise NotImplementedError

    @abstractmethod
    async def collect_census(self, actions: List[Action]) -> None:
        """
        Collect census from player actions (Players → Conductor).

        This is the inbound data collection from Players.
        "Census" emphasizes aggregation from multiple sources.

        Args:
            actions: List of Actions collected from all Players
        """
        raise NotImplementedError

    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """Analyze the collected census and system state."""
        raise NotImplementedError

    @abstractmethod
    async def coordinate(self, analysis_result: Dict[str, Any]) -> CoordinationDecision:
        """Generate a CoordinationDecision based on analysis."""
        raise NotImplementedError

    # =========================================================================
    # Main Execution (Cycle)
    # =========================================================================

    async def cycle(self) -> "CycleResult":
        """
        Execute one complete coordination cycle.

        In the hierarchical execution model:
        - Simulator: round (orchestrates all entities)
        - PlayerPersona: operate (calls Player.turn internally)
        - Player: turn (for loop calling step)
        - Player: step (perceive→decide→act)
        - Conductor: cycle (collect→analyze→coordinate)  <-- THIS METHOD

        The cycle consists of three phases:
        1. collect_census(): Process Actions collected from Players
        2. analyze(): Examine system state and census
        3. coordinate(): Generate a CoordinationDecision

        Note: notify() is called BEFORE the cycle, at round start.

        Returns:
            CycleResult containing:
                - decision: The CoordinationDecision generated
                - census_size: Number of actions in the census
                - analysis_result: Output from analyze phase
                - tick_cycle_count: Cycle number
                - tick_cycle_duration_ms: Cycle duration
        """
        # Start cycle timing
        self._state.cycle_tick_start()

        # Phase 1: Collect census (clear and process buffered actions)
        actions = self._state.clear_census()
        census_size = len(actions)
        await self.collect_census(actions)

        # Phase 2: Analyze census and system state
        analysis_result = await self.analyze()

        # Phase 3: Generate coordination decision
        decision = await self.coordinate(analysis_result)

        # Validate and record
        self._validate_decision(decision)
        self._state.record_decision(decision)

        # End cycle timing
        self._state.cycle_tick_end()

        return CycleResult(
            decision=decision,
            census_size=census_size,
            analysis_result=analysis_result,
            tick_cycle_count=self._state.cycle_count,
            tick_cycle_duration_ms=self._state.cycle_last_duration_ms,
        )

    def _validate_decision(self, decision: CoordinationDecision) -> None:
        """Validate that decision conforms to behavioral contract."""
        prohibited_types = {
            "move",
            "navigate",
            "execute",
            "compute_direct",
            "environment_action",
        }
        if decision.decision_type.lower() in prohibited_types:
            raise ValueError(
                f"CoordinationDecision type '{decision.decision_type}' violates "
                f"behavioral contract: Conductor cannot generate environment actions."
            )

    # =========================================================================
    # Census Intake (from Players)
    # =========================================================================

    def on_action_received(self, action: Action) -> None:
        """Callback for when an Action is pushed from a Player."""
        self._state.add_to_census(action)

    async def on_action_received_async(self, action: Action) -> None:
        """Async callback for action receipt."""
        self._state.add_to_census(action)

    # =========================================================================
    # State Access (Globally Visible)
    # =========================================================================

    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of Conductor state (globally visible)."""
        return self._state.to_snapshot()

    def get_decision_history(self) -> List[CoordinationDecision]:
        """Get the history of CoordinationDecisions."""
        return self._state.decision_history.copy()

    # =========================================================================
    # Message Handling
    # =========================================================================

    def get_pending_messages(self) -> List["Message"]:
        """Get and clear pending messages from inbox."""
        messages = self._state._message_inbox.copy()
        self._state._message_inbox.clear()
        return messages

    def __repr__(self) -> str:
        return f"Conductor(id={self.identity}, mode={self.coordination_mode})"
