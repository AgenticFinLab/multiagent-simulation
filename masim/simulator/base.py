"""Base Simulator module for the Multi-Agent Simulation (MASim) framework.

This module provides abstract base classes and type definitions.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Enums:
    SimulatorStatus     - Lifecycle states: INITIALIZING → READY → RUNNING → TERMINATED
    RoundPhase          - Phase within a round: NOTIFICATION → PLAYER_DECISION → COORDINATION → COMPLETE

Dataclasses:
    ExecutionClock      - Hierarchical time tracking for rounds/cycles
    SimulationConfig    - Top-level config: setting, ray, players, conductor, topology

Abstract Classes:
    BaseSimulator       - Abstract orchestrator with fundamental infrastructure:
                          - Ray actor handles (_player_persona_handles, _conductor_persona_handle)
                          - History management (deque for round results)
                          - Storage directories (from config.logging)
                          - Status/phase tracking

                          Abstract methods (must be implemented by subclasses):
                          Ray Actor:   _launch_player_personas(), _launch_conductor_persona()
                          Lifecycle:   setup(), run_round(), run(), shutdown()
                          Utilities:   get_status(), get_round_history(), get_player_handle(),
                                       get_conductor_handle()

================================================================================
                            ARCHITECTURE
================================================================================

The Simulator interacts ONLY with Personas - Player/Conductor are completely
hidden as internal implementation details of their respective Personas.

    Simulator
        │
        ├── PlayerPersona (Ray Actor) ──► BasePlayer (internal, hidden)
        │
        └── ConductorPersona (Ray Actor) ──► BaseConductor (internal, hidden)

Key Design Principles:
- Simulator has ZERO knowledge of Player/Conductor implementation
- All interaction goes through Persona's public interface
- Personas are Ray actors (distributed computing)

================================================================================
                        HIERARCHICAL EXECUTION MODEL
================================================================================

┌─────────────────────────────────────────────────────────────────────────┐
│  Level    │  Entity           │  Term     │  Description               │
├───────────┼───────────────────┼───────────┼────────────────────────────┤
│  L1       │  Simulator        │  round    │  One complete simulation   │
│           │                   │           │  cycle (all personas)      │
├───────────┼───────────────────┼───────────┼────────────────────────────┤
│  L2       │  PlayerPersona    │  operate  │  Simulator-facing interface│
├───────────┼───────────────────┼───────────┼────────────────────────────┤
│  L2       │  ConductorPersona │  cycle    │  notify→collect→analyze   │
│           │                   │           │  →coordinate               │
└───────────┴───────────────────┴───────────┴────────────────────────────┘

Each level has an ExecutionClock for temporal tracking.

================================================================================
                          ROUND EXECUTION FLOW
================================================================================

Simulator.run():
│
└── for round_num in 1..total_rounds:
    │
    ├── Phase 1: NOTIFICATION
    │   └── conductor.notify(round_num, player_ids)  # Conductor → Players
    │       └── Returns: Dict[player_id → notification_dict]
    │
    ├── Phase 2: PLAYER_DECISION
    │   └── player_persona.operate(observation, num_steps)  [parallel]
    │       └── Returns: TurnResult with final_action
    │
    ├── Phase 3: COORDINATION
    │   ├── conductor.receive_responses(responses)  # Players → Conductor
    │   └── conductor.cycle()                    # collect → analyze → coordinate
    │       └── Returns: CycleResult with CoordinationDecision
    │
    └── Phase 4: COMPLETE
        └── Broadcast coordination decision to all players

================================================================================
                              USAGE
================================================================================

    from masim.simulator.general import GeneralSimulator
    from masim.simulator.base import SimulationConfig
    from masim.utils.config import load_config

    yaml_config = load_config("configs/Demo/simulation.yml")
    sim_config = SimulationConfig(**yaml_config)

    simulator = GeneralSimulator(sim_config)
    await simulator.setup()
    results = await simulator.run()
    await simulator.shutdown()
"""

import time
import uuid
import logging
from enum import Enum, auto
from datetime import datetime
from pathlib import Path
from collections import deque
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import ray
    from ray.actor import ActorHandle
    from masim.persona.base import PlayerPersona, ConductorPersona


# =============================================================================
# Status Enums
# =============================================================================


class SimulatorStatus(Enum):
    """Status of the simulator lifecycle."""

    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    TERMINATED = auto()
    ERROR = auto()


class RoundPhase(Enum):
    """
    Phases within a simulation round.

    Each round progresses through these phases in order:
    1. NOTIFICATION: Conductor notifies all Players of round state
    2. PLAYER_DECISION: All PlayerPersonas execute operate()
    3. COORDINATION: ConductorPersona executes cycle()
    4. COMPLETE: Round finishes, results recorded
    """

    NOTIFICATION = auto()
    PLAYER_DECISION = auto()
    COORDINATION = auto()
    COMPLETE = auto()


# =============================================================================
# Execution Clock (Hierarchical Time Tracking)
# =============================================================================


@dataclass
class ExecutionClock:
    """
    Unified time tracking for hierarchical execution model.

    Used at all levels of the execution hierarchy:
    - Simulator: RoundClock tracks round execution
    - PlayerPersona: StepClock tracks step execution
    - ConductorPersona: CycleClock tracks cycle execution

    Attributes:
        count: Number of completed executions
        start_time: Performance counter timestamp when current execution started
        last_duration_ms: Duration of the most recent completed execution (ms)
        total_duration_ms: Cumulative execution time across all executions (ms)
    """

    # Number of completed executions.
    count: int = 0

    # Performance counter timestamp when current execution started.
    start_time: Optional[float] = None

    # Duration of the most recent completed execution in milliseconds.
    last_duration_ms: float = 0.0

    # Cumulative execution time across all executions in milliseconds.
    total_duration_ms: float = 0.0

    def tick_start(self) -> None:
        """Mark the start of an execution."""
        self.start_time = time.perf_counter()

    def tick_end(self) -> None:
        """Mark the end of an execution and update metrics."""
        if self.start_time is not None:
            elapsed = time.perf_counter() - self.start_time
            self.last_duration_ms = elapsed * 1000.0
            self.total_duration_ms += self.last_duration_ms
            self.count += 1
            self.start_time = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize clock state for reporting/logging."""
        return {
            "count": self.count,
            "last_duration_ms": round(self.last_duration_ms, 3),
            "total_duration_ms": round(self.total_duration_ms, 3),
            "avg_duration_ms": (
                round(self.total_duration_ms / self.count, 3) if self.count > 0 else 0.0
            ),
        }


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class SimulationConfig:
    """
    Configuration for simulation initialization.

    Field names match exactly with simulation.yml top-level keys.
    Use **load_config(path) to construct directly from YAML.

    Attributes:
        setting: Simulation settings dict (name, total_rounds, etc.)
        ray: Ray cluster configuration dict
        players: Player configurations dict
        conductor: Conductor configuration dict
        topology: Communication topology dict
        environment: Environment settings dict (dotenv_path, workspace)
        logging: Logging/storage paths dict (checkpoint_path, result_path, etc.)
        simulation_id: Unique identifier (auto-generated if None)
    """

    setting: Dict[str, Any] = field(default_factory=dict)
    ray: Dict[str, Any] = field(default_factory=dict)
    players: Dict[str, Any] = field(default_factory=dict)
    conductor: Dict[str, Any] = field(default_factory=dict)
    topology: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)

    # Auto-generated
    simulation_id: Optional[str] = None

    def __post_init__(self):
        if self.simulation_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            self.simulation_id = f"sim_{timestamp}_{unique_id}"


# =============================================================================
# Base Simulator (Abstract)
# =============================================================================


class BaseSimulator(ABC):
    """
    Abstract base class for simulation orchestration.

    The Simulator is the top-level controller that:
    - Initializes and manages Ray cluster
    - Creates and manages Personas as Ray actors
    - Orchestrates the simulation lifecycle (round → turn → step)
    - Routes messages between components

    IMPORTANT: Simulator is a pure orchestrator.
    - It does NOT execute actions (that's Environment/Conductor domain)
    - It does NOT generate observations (that's Conductor domain)
    - It only coordinates the flow between Personas

    Subclasses must implement:
    - create_player_personas(): Create PlayerPersona instances
    - create_conductor_persona(): Create ConductorPersona instance (optional)

    For a ready-to-use implementation, see `GeneralSimulator` in `general.py`.
    """

    def __init__(self, config: SimulationConfig):
        """
        Initialize the simulator.

        Args:
            config: Simulation configuration
        """
        self.config = config
        self.simulation_id = config.simulation_id

        # Status tracking
        self.status = SimulatorStatus.INITIALIZING
        self.current_round: int = 0
        self.current_phase: RoundPhase = RoundPhase.NOTIFICATION

        # Hierarchical execution clock for round-level timing.
        self.round_clock: ExecutionClock = ExecutionClock()

        # Ray actor handles for Personas (NOT Player/Conductor directly!)
        # Simulator interacts ONLY with Persona actors, never with domain objects.
        self._player_persona_handles: Dict[str, "ActorHandle"] = {}
        self._conductor_persona_handle: Optional["ActorHandle"] = None

        # History management for round results
        self.history: deque = deque(maxlen=config.setting["entry_limit"])

        # Storage directories from logging config (must be specified in config)
        self.storage_dir = Path(config.logging["result_path"]) / self.simulation_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoint_dir = Path(config.logging["checkpoint_path"])
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.logging_dir = Path(config.logging["logging_path"])
        self.logging_dir.mkdir(parents=True, exist_ok=True)

    # Note: generate_observations is NOT a Simulator responsibility.
    # Observations are generated by the Conductor or Environment.
    # The Simulator only orchestrates the flow between components.

    # Note: execute_actions is NOT a Simulator responsibility.
    # The Conductor handles coordination and environment interaction.
    # The Simulator is a pure orchestrator.

    # =========================================================================
    # Ray Actor Management (abstract - implemented in general.py)
    # =========================================================================

    @abstractmethod
    def _launch_player_personas(self) -> Dict[str, "ActorHandle"]:
        """
        Create and launch PlayerPersonas as Ray actors from config.

        Reads config.players, loads player classes dynamically, and creates
        Ray actors directly - no intermediate local instances.

        Returns:
            Dict of player_id -> Ray actor handle
        """
        raise NotImplementedError

    @abstractmethod
    def _launch_conductor_persona(self) -> Optional["ActorHandle"]:
        """
        Create and launch ConductorPersona as Ray actor from config.

        Reads config.conductor, loads conductor class dynamically, and creates
        a Ray actor directly - no intermediate local instance.

        Returns:
            Ray actor handle, or None if no conductor configured
        """
        raise NotImplementedError

    # =========================================================================
    # Lifecycle Methods (abstract - implemented in general.py)
    # =========================================================================

    @abstractmethod
    async def setup(self) -> None:
        """
        Set up the simulation: create Persona actors and initialize.

        The Simulator creates Personas (which internally create Player/Conductor)
        and launches them as Ray actors.
        """
        raise NotImplementedError

    @abstractmethod
    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute one simulation round.

        A round is the highest-level execution unit in the hierarchy:
        - Round (Simulator) → Operate (PlayerPersona) → Cycle (ConductorPersona)

        Args:
            round_num: Current round number (1-indexed)

        Returns:
            Round results dictionary
        """
        raise NotImplementedError

    @abstractmethod
    async def run(self) -> List[Dict[str, Any]]:
        """
        Run the complete simulation.

        Returns:
            List of all round results
        """
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        raise NotImplementedError

    # =========================================================================
    # Utility Methods (abstract)
    # =========================================================================

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status including round clock metrics."""
        raise NotImplementedError

    @abstractmethod
    def get_round_history(self, round_num: int) -> Optional[Dict[str, Any]]:
        """
        Get results from a specific round.

        Args:
            round_num: Round number to retrieve (1-indexed)

        Returns:
            Round results dict, or None if round not found
        """
        raise NotImplementedError

    @abstractmethod
    def get_player_handle(self, player_id: str) -> Optional["ActorHandle"]:
        """
        Get Ray actor handle for a specific player.

        Args:
            player_id: Player identifier

        Returns:
            Ray actor handle, or None if player not found
        """
        raise NotImplementedError

    @abstractmethod
    def get_conductor_handle(self) -> Optional["ActorHandle"]:
        """
        Get Ray actor handle for the conductor.

        Returns:
            Ray actor handle, or None if no conductor
        """
        raise NotImplementedError
