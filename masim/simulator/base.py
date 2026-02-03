"""Base Simulator module for the Multi-Agent Simulation (MASim) framework.

This module provides:
- SimulationConfig: Configuration for simulation setup
- BaseSimulator: Top-level orchestrator for multi-agent simulations

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
│  L2       │  ConductorPersona │  cycle    │  receive→analyze→coordinate│
└─────────────────────────────────────────────────────────────────────────┘

Each level has an ExecutionClock for temporal tracking.
"""

import os
import uuid
import time
import logging
import importlib
from enum import Enum, auto
from pathlib import Path
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Tuple

import ray

from masim.player.base import Action, Observation, BasePlayer, PlayerConfig, TurnResult
from masim.conductor.base import BaseConductor, ConductorConfig
from masim.persona.base import PlayerPersona, ConductorPersona, PersonaConfig


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
    1. OBSERVATION: Environment generates observations for all Players
    2. PLAYER_DECISION: All PlayerPersonas execute operate()
    3. COORDINATION: ConductorPersona executes cycle()
    4. EXECUTION: Actions are executed in the environment
    5. COMPLETE: Round finishes, results recorded
    """

    OBSERVATION = auto()
    PLAYER_DECISION = auto()
    COORDINATION = auto()
    EXECUTION = auto()
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
class RayConfig:
    """Configuration for Ray cluster connection."""

    namespace: str = "masim"
    address: Optional[str] = None
    num_cpus: Optional[int] = None
    num_gpus: Optional[int] = None
    runtime_env: Dict[str, Any] = field(default_factory=dict)
    logging_level: int = logging.INFO


@dataclass
class SimulationConfig:
    """
    Configuration for simulation initialization.

    Attributes:
        simulation_id: Unique identifier (auto-generated if None)
        ray_config: Ray cluster configuration
        total_rounds: Total number of simulation rounds
        actor_prefix: Prefix for Ray actor names
        storage_dir: Directory for simulation artifacts
        entry_limit: Max history entries to keep in memory
        persona_config: Configuration for all Personas
        extras: Domain-specific configuration
    """

    ray_config: RayConfig = field(default_factory=RayConfig)
    total_rounds: int = 100
    actor_prefix: str = "masim"
    storage_dir: Optional[str] = None
    entry_limit: int = 100
    persona_config: Optional[PersonaConfig] = None
    extras: Dict[str, Any] = field(default_factory=dict)
    simulation_id: Optional[str] = None

    def __post_init__(self):
        if self.simulation_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            self.simulation_id = f"sim_{timestamp}_{unique_id}"


# =============================================================================
# Ray Utilities
# =============================================================================


def ensure_ray(config: RayConfig) -> None:
    """Initialize Ray cluster; reconnect if namespace differs."""
    init_kwargs = {
        "namespace": config.namespace,
        "logging_level": config.logging_level,
    }

    if config.address:
        init_kwargs["address"] = config.address
    if config.num_cpus is not None:
        init_kwargs["num_cpus"] = config.num_cpus
    if config.num_gpus is not None:
        init_kwargs["num_gpus"] = config.num_gpus
    if config.runtime_env:
        init_kwargs["runtime_env"] = config.runtime_env

    if ray.is_initialized():
        try:
            current_ns = ray.get_runtime_context().namespace
            if current_ns == config.namespace:
                return
        except Exception:
            pass
        ray.shutdown()

    ray.init(**init_kwargs)


def get_actor_name(prefix: str, entity_id: str) -> str:
    """Construct a deterministic Ray actor name."""
    return f"{prefix}::{entity_id}"


def load_class(path: str) -> type:
    """Load a class from "module.submodule:ClassName" or "module.submodule.ClassName"."""
    if ":" in path:
        module_path, cls_name = path.split(":", 1)
    else:
        module_path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, cls_name)


# =============================================================================
# Base Simulator
# =============================================================================


class BaseSimulator(ABC):
    """
    Abstract base class for simulation orchestration.

    The Simulator is the top-level controller that:
    - Initializes and manages Ray cluster
    - Creates and manages Personas as Ray actors
    - Orchestrates the simulation lifecycle
    - Manages message routing between components
    - Handles environment interaction

    IMPORTANT: Simulator interacts ONLY with Personas.
    Player/Conductor are completely hidden as internal details.

    Subclasses must implement:
    - create_player_personas(): Create PlayerPersona instances
    - create_conductor_persona(): Create ConductorPersona instance (optional)
    - generate_observations(): Generate observations from environment
    - execute_actions(): Execute actions in environment
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
        self.current_phase: RoundPhase = RoundPhase.OBSERVATION

        # Hierarchical execution clock for round-level timing.
        self.round_clock: ExecutionClock = ExecutionClock()

        # Ray actor handles for Personas (NOT Player/Conductor!)
        self._player_persona_handles: Dict[str, ray.actor.ActorHandle] = {}
        self._conductor_persona_handle: Optional[ray.actor.ActorHandle] = None

        # History management
        self.history = deque(maxlen=config.entry_limit)

        # Storage setup
        if config.storage_dir:
            self.storage_dir = Path(config.storage_dir)
        else:
            self.storage_dir = Path(f"./simulation_results/{self.simulation_id}")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logging.info(f"[MASIM] Initialized simulator with ID: {self.simulation_id}")

    # =========================================================================
    # Ray Actor Management (Personas)
    # =========================================================================

    def _launch_player_personas(
        self,
        personas: Dict[str, PlayerPersona],
    ) -> Dict[str, ray.actor.ActorHandle]:
        """
        Launch PlayerPersonas as Ray actors.

        Args:
            personas: Dict of player_id -> PlayerPersona instance

        Returns:
            Dict of player_id -> Ray actor handle
        """
        ensure_ray(self.config.ray_config)
        handles = {}

        # Create Ray actor class from PlayerPersona
        RemotePlayerPersona = ray.remote(PlayerPersona)

        for player_id, persona in personas.items():
            actor_name = get_actor_name(self.config.actor_prefix, player_id)

            # Re-create persona as Ray actor with same config
            handle = RemotePlayerPersona.options(
                name=actor_name,
                lifetime="detached",
                namespace=self.config.ray_config.namespace,
            ).remote(
                player_class=persona._player_class,
                player_config=persona._player_config,
                persona_config=persona._config,
            )

            handles[player_id] = handle
            logging.info(f"[MASIM] Launched PlayerPersona actor: {actor_name}")

        return handles

    def _launch_conductor_persona(
        self,
        persona: ConductorPersona,
    ) -> ray.actor.ActorHandle:
        """
        Launch ConductorPersona as Ray actor.

        Args:
            persona: ConductorPersona instance

        Returns:
            Ray actor handle
        """
        ensure_ray(self.config.ray_config)

        RemoteConductorPersona = ray.remote(ConductorPersona)
        actor_name = get_actor_name(self.config.actor_prefix, persona.identity)

        handle = RemoteConductorPersona.options(
            name=actor_name,
            lifetime="detached",
            namespace=self.config.ray_config.namespace,
        ).remote(
            conductor_class=persona._conductor_class,
            conductor_config=persona._conductor_config,
            persona_config=persona._config,
        )

        logging.info(f"[MASIM] Launched ConductorPersona actor: {actor_name}")
        return handle

    # =========================================================================
    # Abstract Methods (to be implemented by subclasses)
    # =========================================================================

    @abstractmethod
    def create_player_personas(self) -> Dict[str, PlayerPersona]:
        """
        Create PlayerPersona instances.

        Subclasses implement this to create Personas with appropriate
        Player classes and configurations.

        Returns:
            Dict of player_id -> PlayerPersona instance

        Example:
            def create_player_personas(self) -> Dict[str, PlayerPersona]:
                personas = {}
                for player_id, cfg in self.config.extras["players"].items():
                    persona = PlayerPersona(
                        player_class=MyPlayer,
                        player_config=PlayerConfig(identity=player_id, **cfg),
                        persona_config=self.config.persona_config,
                    )
                    personas[player_id] = persona
                return personas
        """
        raise NotImplementedError

    @abstractmethod
    def create_conductor_persona(self) -> Optional[ConductorPersona]:
        """
        Create ConductorPersona instance.

        Returns:
            ConductorPersona instance or None if no coordination needed

        Example:
            def create_conductor_persona(self) -> Optional[ConductorPersona]:
                return ConductorPersona(
                    conductor_class=MyConductor,
                    conductor_config=ConductorConfig(identity="conductor"),
                    persona_config=self.config.persona_config,
                )
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_observations(
        self,
        round_num: int,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate observations for all PlayerPersonas from the environment.

        Args:
            round_num: Current simulation round

        Returns:
            Dict of player_id -> observation_dict
        """
        raise NotImplementedError

    @abstractmethod
    async def execute_actions(
        self,
        actions: Dict[str, Dict[str, Any]],
        round_num: int,
    ) -> Any:
        """
        Execute Player actions in the environment.

        Args:
            actions: Dict of player_id -> action_dict
            round_num: Current simulation round

        Returns:
            Environment state or result
        """
        raise NotImplementedError

    # =========================================================================
    # Simulation Lifecycle
    # =========================================================================

    async def setup(self) -> None:
        """
        Set up the simulation: create Persona actors and initialize.

        The Simulator creates Personas (which internally create Player/Conductor)
        and launches them as Ray actors.
        """
        logging.info(f"[MASIM] Setting up simulation {self.simulation_id}")

        # Initialize Ray
        ensure_ray(self.config.ray_config)

        # Create and launch PlayerPersonas
        player_personas = self.create_player_personas()
        self._player_persona_handles = self._launch_player_personas(player_personas)

        # Create and launch ConductorPersona (if configured)
        conductor_persona = self.create_conductor_persona()
        if conductor_persona:
            self._conductor_persona_handle = self._launch_conductor_persona(
                conductor_persona
            )

            # Register all players with conductor
            for player_id in self._player_persona_handles.keys():
                ray.get(
                    self._conductor_persona_handle.register_player.remote(player_id)
                )

        # Initialize all Persona actors
        init_futures = [
            h.initialize.remote() for h in self._player_persona_handles.values()
        ]
        if self._conductor_persona_handle:
            init_futures.append(self._conductor_persona_handle.initialize.remote())
        ray.get(init_futures)

        self.status = SimulatorStatus.READY
        logging.info(f"[MASIM] Simulation setup complete")

    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute one simulation round.

        A round is the highest-level execution unit in the hierarchy:
        - Round (Simulator) → Operate (PlayerPersona) → Cycle (ConductorPersona)

        Internally, PlayerPersona.operate() calls Player.turn() which loops
        through multiple step() calls, but Simulator only sees the final TurnResult.

        Args:
            round_num: Current round number (1-indexed)

        Returns:
            Round results containing:
            - turn_results: Dict of player_id → TurnResult summary
            - coordination: Conductor's coordination decision (if any)
            - environment_result: Result of action execution
            - round_clock: Timing metrics for this round
        """
        # Start round timing
        self.round_clock.tick_start()

        self.current_round = round_num
        round_results = {
            "round": round_num,
            "turn_results": {},
            "coordination": None,
        }

        # Phase 1: Generate observations
        self.current_phase = RoundPhase.OBSERVATION
        observations = await self.generate_observations(round_num)

        # Phase 2: PlayerPersonas execute operate()
        self.current_phase = RoundPhase.PLAYER_DECISION
        operate_futures = {}
        for player_id, obs_dict in observations.items():
            if player_id in self._player_persona_handles:
                # Create Observation and call persona.operate()
                observation = Observation(
                    data=obs_dict.get("data", {}),
                    source_id=obs_dict.get("source_id", "environment"),
                    observation_id=obs_dict.get("observation_id"),
                    target_id=obs_dict.get("target_id", player_id),
                    step=obs_dict.get("step", round_num),
                    metadata=obs_dict.get("metadata", {}),
                )
                # num_steps can be configured per-player in obs_dict
                num_steps = obs_dict.get("num_steps", 1)
                future = self._player_persona_handles[player_id].operate.remote(
                    observation, num_steps
                )
                operate_futures[player_id] = future

        # Collect turn results
        turn_results = {}
        for player_id, future in operate_futures.items():
            turn_result = ray.get(future)
            # Convert TurnResult to dict for serialization
            turn_results[player_id] = {
                "turn_count": turn_result.tick_turn_count,
                "step_count": turn_result.tick_step_count,
                "duration_ms": turn_result.tick_turn_duration_ms,
                "final_action": (
                    turn_result.final_action.to_dict()
                    if turn_result.final_action
                    else None
                ),
                "step_results": [
                    {
                        "decision_payload": sr.decision_payload,
                        "action": sr.action.to_dict(),
                        "step_count": sr.tick_step_count,
                    }
                    for sr in turn_result.step_results
                ],
            }
        round_results["turn_results"] = turn_results

        # Phase 3: ConductorPersona executes cycle()
        if self._conductor_persona_handle:
            self.current_phase = RoundPhase.COORDINATION

            # Collect final actions from all turns and send to Conductor
            actions = []
            for tr in turn_results.values():
                if tr["final_action"]:
                    action_dict = tr["final_action"]
                    action = Action(
                        action_type=action_dict.get("action_type", ""),
                        payload=action_dict.get("payload", {}),
                        source_id=action_dict.get("source_id", ""),
                        action_id=action_dict.get("action_id"),
                        metadata=action_dict.get("metadata", {}),
                    )
                    actions.append(action)

            ray.get(self._conductor_persona_handle.receive_actions.remote(actions))

            # Conductor executes coordination cycle
            cycle_result = ray.get(self._conductor_persona_handle.cycle.remote())
            round_results["coordination"] = cycle_result.to_dict()

            # Broadcast coordination decision to PlayerPersonas
            # Note: We send just the decision dict, not the full CycleResult
            coord_futures = []
            for handle in self._player_persona_handles.values():
                coord_futures.append(
                    handle.receive_coordination.remote(
                        round_results["coordination"]["decision"]
                    )
                )
            ray.get(coord_futures)

        # Phase 4: Execute actions in environment
        self.current_phase = RoundPhase.EXECUTION
        actions_for_env = {
            pid: tr["final_action"]
            for pid, tr in turn_results.items()
            if tr["final_action"]
        }
        env_result = await self.execute_actions(actions_for_env, round_num)
        round_results["environment_result"] = env_result

        # End round timing and record
        self.round_clock.tick_end()
        round_results["round_clock"] = self.round_clock.to_dict()

        self.current_phase = RoundPhase.COMPLETE
        self.history.append(round_results)

        return round_results

    async def run(self) -> List[Dict[str, Any]]:
        """
        Run the complete simulation.

        Returns:
            List of all round results
        """
        logging.info(f"[MASIM] Starting simulation {self.simulation_id}")
        self.status = SimulatorStatus.RUNNING

        all_results = []

        try:
            for round_num in range(1, self.config.total_rounds + 1):
                logging.info(
                    f"[MASIM] Starting round {round_num}/{self.config.total_rounds}"
                )

                round_result = await self.run_round(round_num)
                all_results.append(round_result)

                logging.info(f"[MASIM] Completed round {round_num}")

            self.status = SimulatorStatus.TERMINATED
            logging.info(f"[MASIM] Simulation completed successfully")

        except Exception as e:
            self.status = SimulatorStatus.ERROR
            logging.error(f"[MASIM] Simulation error: {e}")
            raise

        return all_results

    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        logging.info(f"[MASIM] Shutting down simulation {self.simulation_id}")

        # Shutdown all Persona actors
        shutdown_futures = []
        for handle in self._player_persona_handles.values():
            shutdown_futures.append(handle.shutdown.remote())
        if self._conductor_persona_handle:
            shutdown_futures.append(self._conductor_persona_handle.shutdown.remote())

        ray.get(shutdown_futures)

        self.status = SimulatorStatus.TERMINATED
        logging.info(f"[MASIM] Simulation shutdown complete")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_round_history(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Get historical data for a specific round."""
        for record in self.history:
            if record.get("round") == round_num:
                return record
        return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status including round clock metrics.
        """
        return {
            "simulation_id": self.simulation_id,
            "status": self.status.name,
            "current_round": self.current_round,
            "current_phase": self.current_phase.name,
            "total_rounds": self.config.total_rounds,
            "player_count": len(self._player_persona_handles),
            "has_conductor": self._conductor_persona_handle is not None,
            "round_clock": self.round_clock.to_dict(),
        }
