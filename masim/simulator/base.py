"""Base Simulator module for the Multi-Agent Simulation (MASim) framework.

This module provides abstract base classes and type definitions.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Enums:
    SimulatorStatus     - Lifecycle states: INITIALIZING → READY → RUNNING → TERMINATED
    RoundPhase          - Phase within a round: PENDING → EXECUTING → COMPLETE

Dataclasses:
    ExecutionClock      - Hierarchical time tracking for rounds/cycles
    SimulationConfig    - Top-level config: setting, ray, players, topology

Abstract Classes:
    BaseSimulator       - Abstract orchestrator with fundamental infrastructure:
                          - Ray actor handles (player_persona_handles)
                          - History management (HistoryBuffer for round results)
                          - Status/phase tracking

                          Abstract methods (must be implemented by subclasses):
                          Ray Actor:   _launch_player_personas()
                          Lifecycle:   setup(), run_round(), run(), shutdown()
                          Utilities:   get_status(), get_round_history(), get_player_handle()

                          Extension hooks (override in subclass for customization):
                          update_topology(round_num) — called at the start of every round.
                              Default: no-op (static topology).
                              Override to: add/remove edges, rewire agents, switch between
                              feedforward and feedback configurations.
                              After mutation: call topology.invalidate_levels_cache() +
                              _update_actor_topology_slices() to push new slices
                              AND updated peer handles to all affected actors.

================================================================================
                            ARCHITECTURE
================================================================================

The Simulator interacts ONLY with Personas — Player implementation is hidden.
All agents (including coordinators) are Players wrapped in PlayerPersona actors.
Role distinctions (coordinator vs regular player) map to topology level 0 vs 1+.

    Simulator
        │
        ├── Level 0 Personas (topology sources — execute first, e.g. coordinators)
        │       └── PlayerPersona (Ray Actor) ──► BasePlayer
        │
        └── Level 1+ Personas (execute after Level 0, in parallel within a level)
                └── PlayerPersona (Ray Actor) ──► BasePlayer

Key Design Principles:
- Simulator has ZERO knowledge of Player implementation
- All interaction goes through Persona's public interface
- Personas are Ray actors (distributed computing)
- Level-ordered execution: Level N fully completes before Level N+1 starts

================================================================================
                        ROUND EXECUTION FLOW
================================================================================

Simulator.run():
│
└── for round_num in 1..total_rounds:
    │
    ├── update_topology(round_num)      # Extension hook (no-op for static topology)
    │
    ├── for level in topology_levels:
    │   │
    │   ├── Phase 1: EXECUTE
    │   │   └── persona.operate(round_num, level=N)  [parallel for all actors in level]
    │   │       └── Returns: (TurnResult, pending_infos) tuple
    │   │
    │   ├── Phase 2: COLLECT
    │   │   └── ray.get(operate futures) → {player_id: TurnResult} + all pending_infos
    │   │
    │   └── Phase 3: DISPATCH
    │       └── build_message_from_info() → channel.encode_and_deliver()
    │           → target_persona.receive_message()  [Ray remote]
    │           [all deliveries complete before next level's phase_execute starts]
    │
    └── Phase 4: RECORD (rate-limited)
        └── topology.save_round_diagram()  [only if save_diagram_interval matches]

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

import os
import time
import uuid
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from masim.utils.history import HistoryBuffer

if TYPE_CHECKING:
    import ray
    from ray.actor import ActorHandle
    from masim.utils.topology import TopologyGraph
    from masim.communication.general import CommunicationChannel


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
    communication: Dict[str, Any] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)

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
        # Round numbering convention:
        #   - Round 0: Setup phase (before simulation starts)
        #   - Round 1+: Actual simulation rounds
        self.status = SimulatorStatus.INITIALIZING
        self.current_round: int = 0  # Starts at 0 (setup), advances to 1+ during run
        self.current_phase: RoundPhase = RoundPhase.PENDING

        # Hierarchical execution clock for round-level timing
        self.round_clock: ExecutionClock = ExecutionClock()

        # Ray actor handles for Personas
        self.player_persona_handles: Dict[str, "ActorHandle"] = {}

        # History management for round results (hot memory + cold disk)
        history_folder = os.path.join(config.setting["record_path"], "history")
        self.history: HistoryBuffer = HistoryBuffer(
            folder=history_folder,
            entry_limit=config.setting["round_history_limit"],
        )

        # Communication topology (initialized by subclass setup)
        self.topology: Optional["TopologyGraph"] = None

        # Communication channel for message dispatch and recording
        self.communication: Optional["CommunicationChannel"] = None

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
    #                    TOPOLOGY UPDATE HOOK
    # =========================================================================

    def update_topology(self, round_num: int) -> None:
        """
        Extension point: update the topology graph before each round executes.

        Default implementation is a no-op (static topology).

        Override this in a subclass to implement dynamic topologies, e.g.:
        - Rewire edges based on simulation state (agent relationships evolve)
        - Add/remove players mid-simulation
        - Switch between feedback and feedforward configurations

        After mutating self.topology (add_edge / remove_edge), you MUST:
          1. Call self.topology.invalidate_levels_cache() to force BFS recompute.
          2. Call self._update_actor_topology_slices() to push new topology slices
             AND updated peer handles to all affected actors.

        Args:
            round_num: The round number about to be executed (1-indexed)

        Example override::

            def update_topology(self, round_num: int) -> None:
                if round_num == 10:
                    self.topology.graph.add_edge("player_1", "player_2")
                    self.topology.invalidate_levels_cache()
                    self._update_actor_topology_slices()
        """
        # Default: static topology — no mutation, no actor updates needed.
        pass

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
    def phase_dispatch(self, all_info_lists: List[List[Dict[str, Any]]]) -> None:
        """Encode pending Info units → Message → SimPacket and deliver to targets.

        Args:
            all_info_lists: List of per-actor Info lists from phase_collect().
                            Each inner list contains dicts with keys:
                            info, sender_id, target_ids, round_num.
        """
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
