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
    SimulationConfig    - Top-level config: setting, ray, players, topology

Abstract Classes:
    BaseSimulator       - Abstract orchestrator with fundamental infrastructure:
                          - Ray actor handles (_player_persona_handles)
                          - History management (deque for round results)
                          - Storage directories (from config.proxy)
                          - Status/phase tracking

                          Abstract methods (must be implemented by subclasses):
                          Ray Actor:   _launch_player_personas()
                          Lifecycle:   setup(), run_round(), run(), shutdown()
                          Utilities:   get_status(), get_round_history(), get_player_handle()

================================================================================
                            ARCHITECTURE
================================================================================

The Simulator interacts ONLY with Personas - Player implementation is hidden.
All agents (including coordinators) use PlayerPersona with role-based execution.

    Simulator
        │
        ├── Coordinator Personas (role='coordinator', execute first)
        │       │
        │       └── PlayerPersona (Ray Actor) ──► BasePlayer
        │
        └── Regular Player Personas (role='player', execute second)
                │
                └── PlayerPersona (Ray Actor) ──► BasePlayer

Key Design Principles:
- Simulator has ZERO knowledge of Player implementation
- All interaction goes through Persona's public interface
- Personas are Ray actors (distributed computing)
- Role-based execution: coordinators first, then regular players

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
│           │  (role=coordinator)│          │  Coordinators run first    │
└───────────┴───────────────────┴───────────┴────────────────────────────┘

Each level has an ExecutionClock for temporal tracking.

================================================================================
                          ROUND EXECUTION FLOW
================================================================================

Simulator.run():
│
└── for round_num in 1..total_rounds:
    │
    ├── Phase 1: COORDINATION (if coordinators exist)
    │   └── coordinator_persona.operate()  # Coordinators run first
    │       └── Returns: TurnResult with coordinator's action
    │
    ├── Phase 2: PLAYER_DECISION
    │   └── player_persona.operate(observation, num_steps)  [parallel]
    │       └── Returns: TurnResult with final_action
    │
    └── Phase 3: COMPLETE
        └── Collect all results, record history

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
from enum import Enum, auto
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import ray
    from ray.actor import ActorHandle
    from masim.persona.base import PlayerPersona


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
    High-level phases within a simulation round.

    Simplified for level-based execution model:
    - PENDING: Round not yet started
    - EXECUTING: Levels being executed (one or more)
    - COMPLETE: All levels finished, results recorded
    """

    PENDING = auto()
    EXECUTING = auto()
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
    - PlayerPersona: StepClock tracks step execution (all players including coordinators)

    Attributes:
        count: Number of completed executions
        start_time: Performance counter timestamp when current execution started
        last_duration_ms: Duration of the most recent completed execution (ms)
        total_duration_ms: Cumulative execution time across all executions (ms)
    """

    # Number of completed executions.
    count_executions: int = 0

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
            self.count_executions += 1
            self.start_time = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize clock state for reporting/logging."""
        return {
            "count_executions": self.count_executions,
            "last_duration_ms": round(self.last_duration_ms, 3),
            "total_duration_ms": round(self.total_duration_ms, 3),
            "avg_duration_ms": (
                round(self.total_duration_ms / self.count_executions, 3)
                if self.count_executions > 0
                else 0.0
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
    """

    setting: Dict[str, Any] = field(default_factory=dict)
    ray: Dict[str, Any] = field(default_factory=dict)
    players: Dict[str, Any] = field(default_factory=dict)
    topology: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)

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

    The Simulator is the top-level controller. It interacts ONLY with Personas.
    For concrete implementation, see GeneralSimulator in general.py.
    """

    def __init__(self, config: SimulationConfig):
        """Initialize the simulator."""
        self.config = config
        self.simulation_id = config.simulation_id

        # Status tracking
        self.status = SimulatorStatus.INITIALIZING
        self.current_round: int = 0
        self.current_phase: RoundPhase = RoundPhase.PENDING

        # Hierarchical execution clock for round-level timing
        self.round_clock: ExecutionClock = ExecutionClock()

        # Ray actor handles for Personas
        self.player_persona_handles: Dict[str, "ActorHandle"] = {}

        # History management for round results
        self.history: deque = deque(maxlen=config.setting["entry_limit"])

    # =========================================================================
    #                    RAY ACTOR MANAGEMENT
    # =========================================================================

    @abstractmethod
    def _launch_player_personas(self) -> Dict[str, "ActorHandle"]:
        """Create and launch PlayerPersonas as Ray actors from config."""
        ...

    # =========================================================================
    #                    LIFECYCLE
    # =========================================================================

    @abstractmethod
    async def setup(self) -> None:
        """Set up simulation: create Persona actors and initialize."""
        ...

    @abstractmethod
    async def run(self) -> List[Dict[str, Any]]:
        """Run the complete simulation. Returns list of round results."""
        ...

    @abstractmethod
    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """Execute one simulation round."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        ...

    # =========================================================================
    #                    ROUND PHASES
    # =========================================================================

    @abstractmethod
    def phase_execute(
        self,
        round_num: int,
        level_handles: Dict[str, "ActorHandle"],
    ) -> Dict[str, Any]:
        """Execute player operate() in parallel for a level."""
        ...

    @abstractmethod
    def phase_collect(self, execute_result: Dict[str, Any]) -> Dict[str, Any]:
        """Collect results from execute phase."""
        ...

    @abstractmethod
    def phase_dispatch(self, level_handles: Dict[str, "ActorHandle"]) -> None:
        """Dispatch outbound messages for a level."""
        ...

    @abstractmethod
    def phase_cleanup(self) -> None:
        """Clear message inboxes after round."""
        ...

    # =========================================================================
    #                    UTILITIES
    # =========================================================================

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        ...

    @abstractmethod
    def get_round_history(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Get results from a specific round."""
        ...

    @abstractmethod
    def get_player_handle(self, player_id: str) -> Optional["ActorHandle"]:
        """Get Ray actor handle for a specific player."""
        ...
