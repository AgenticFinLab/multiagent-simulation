"""General Simulator implementation for the MASim framework.

This module provides ready-to-use concrete implementations:
- ensure_ray(): Initialize Ray cluster
- get_actor_name(): Construct deterministic actor names
- load_class(): Dynamic class loading from module path
- GeneralSimulator: Full-featured simulator with Ray integration

For abstract base classes, see `base.py`.

Architectural Note:
    The Simulator is a system-level orchestrator. It does NOT generate
    observations or produce any domain-specific data. Observations come
    from the Conductor (which coordinates the simulation domain).

Usage:
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

import logging
import importlib
from typing import Any, Dict, List, Optional

import ray

from masim.simulator.base import (
    BaseSimulator,
    SimulationConfig,
    SimulatorStatus,
    RoundPhase,
)
from masim.player.base import Action, Observation, PlayerConfig
from masim.conductor.base import ConductorConfig
from masim.persona.general import PlayerPersona, ConductorPersona
from masim.persona.base import PersonaConfig

# Module logger
logger = logging.getLogger("masim.simulator")


# =============================================================================
# Ray Utilities
# =============================================================================


def ensure_ray(ray_config: Dict[str, Any]) -> None:
    """
    Initialize Ray cluster; reconnect if namespace differs.

    Args:
        ray_config: Ray configuration dict from YAML (ray.*)

    This function handles three scenarios:
    1. Ray not initialized → Initialize with config
    2. Ray initialized with same namespace → Do nothing
    3. Ray initialized with different namespace → Shutdown and reinitialize
    """
    init_kwargs = {
        "namespace": ray_config["namespace"],
    }

    if "logging_level" in ray_config:
        level_str = ray_config["logging_level"]
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
        }
        init_kwargs["logging_level"] = level_map[level_str]

    if "address" in ray_config and ray_config["address"]:
        init_kwargs["address"] = ray_config["address"]
    if "num_cpus" in ray_config and ray_config["num_cpus"] is not None:
        init_kwargs["num_cpus"] = ray_config["num_cpus"]
    if "num_gpus" in ray_config and ray_config["num_gpus"] is not None:
        init_kwargs["num_gpus"] = ray_config["num_gpus"]
    if "runtime_env" in ray_config and ray_config["runtime_env"]:
        init_kwargs["runtime_env"] = ray_config["runtime_env"]

    if ray.is_initialized():
        current_ns = ray.get_runtime_context().namespace
        if current_ns == ray_config["namespace"]:
            return
        ray.shutdown()

    ray.init(**init_kwargs)


def get_actor_name(prefix: str, entity_id: str) -> str:
    """
    Construct a deterministic Ray actor name.

    Args:
        prefix: Actor name prefix (usually simulation_id)
        entity_id: Entity identifier (player_id or conductor_id)

    Returns:
        Actor name in format "{prefix}::{entity_id}"
    """
    return f"{prefix}::{entity_id}"


def load_class(path: str) -> type:
    """
    Load a class from module path string.

    Args:
        path: Class path in format "module.submodule:ClassName" or
              "module.submodule.ClassName"

    Returns:
        The loaded class

    Raises:
        ImportError: If module cannot be imported
        AttributeError: If class not found in module
    """
    if ":" in path:
        module_path, cls_name = path.split(":", 1)
    else:
        module_path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, cls_name)


# =============================================================================
# General Simulator (Concrete Implementation)
# =============================================================================


class GeneralSimulator(BaseSimulator):
    """
    Concrete implementation of BaseSimulator with full Ray integration.

    This class provides:
    - Ray cluster initialization and management
    - Direct Persona creation as Ray actors from config (no intermediate instances)
    - Simulation lifecycle orchestration (setup, run_round, run, shutdown)
    - History management and status tracking

    The Simulator is a system-level orchestrator:
    - It does NOT generate observations (that's Conductor's responsibility)
    - It does NOT interpret actions (that's Environment's responsibility)
    - It ONLY orchestrates the flow between components

    Example:
        yaml_config = load_config("configs/Demo/simulation.yml")
        sim_config = SimulationConfig(**yaml_config)
        simulator = GeneralSimulator(sim_config)
        await simulator.setup()
        results = await simulator.run()
    """

    def __init__(self, config: SimulationConfig):
        """
        Initialize the general simulator.

        Args:
            config: Simulation configuration
        """
        super().__init__(config)
        logger.info("GeneralSimulator initialized: %s", self.simulation_id)

    # =========================================================================
    # Ray Actor Management
    # =========================================================================

    def _launch_player_personas(self) -> Dict[str, ray.actor.ActorHandle]:
        """
        Create and launch PlayerPersonas as Ray actors directly from config.

        Reads config.players, dynamically loads player classes, and creates
        Ray actors in a single pass - no intermediate local instances.

        Returns:
            Dict of player_id -> Ray actor handle
        """
        ensure_ray(self.config.ray)
        handles = {}

        RemotePlayerPersona = ray.remote(PlayerPersona)
        persona_config = PersonaConfig(
            auto_checkpoint=self.config.setting["auto_checkpoint"],
            debug_mode=self.config.setting["debug_mode"],
        )

        for player_id, player_cfg in self.config.players.items():
            # Load player class dynamically
            player_class = load_class(player_cfg["class"])

            # Build PlayerConfig
            cfg = player_cfg["config"]
            player_config = PlayerConfig(
                name=player_cfg["name"],
                identity=cfg["identity"],
                group_tags=cfg["group_tags"],
                extras=cfg["extras"],
            )

            # Create Ray actor directly
            actor_name = get_actor_name(self.config.setting["name"], player_id)
            handle = RemotePlayerPersona.options(
                name=actor_name,
                lifetime="detached",
                namespace=self.config.ray["namespace"],
            ).remote(
                player_class=player_class,
                player_config=player_config,
                persona_config=persona_config,
            )

            handles[player_id] = handle
            logger.info("    Launched PlayerPersona: %s", actor_name)

        return handles

    def _launch_conductor_persona(self) -> Optional[ray.actor.ActorHandle]:
        """
        Create and launch ConductorPersona as Ray actor directly from config.

        Reads config.conductor, dynamically loads conductor class, and creates
        a Ray actor in a single pass - no intermediate local instance.

        Returns:
            Ray actor handle, or None if no conductor configured
        """
        if not self.config.conductor:
            return None

        ensure_ray(self.config.ray)

        RemoteConductorPersona = ray.remote(ConductorPersona)
        persona_config = PersonaConfig(
            auto_checkpoint=self.config.setting["auto_checkpoint"],
            debug_mode=self.config.setting["debug_mode"],
        )

        conductor_cfg = self.config.conductor

        # Load conductor class dynamically
        conductor_class = load_class(conductor_cfg["class"])

        # Build ConductorConfig
        cfg = conductor_cfg["config"]
        conductor_config = ConductorConfig(
            identity=cfg["identity"],
            coordination_mode=cfg["coordination_mode"],
            extras=cfg["extras"],
        )

        # Create Ray actor directly
        actor_name = get_actor_name(
            self.config.setting["name"], conductor_config.identity
        )
        handle = RemoteConductorPersona.options(
            name=actor_name,
            lifetime="detached",
            namespace=self.config.ray["namespace"],
        ).remote(
            conductor_class=conductor_class,
            conductor_config=conductor_config,
            persona_config=persona_config,
        )

        logger.info("    Launched ConductorPersona: %s", actor_name)
        return handle

    # =========================================================================
    # Simulation Lifecycle
    # =========================================================================

    async def setup(self) -> None:
        """
        Set up the simulation: create and launch Persona Ray actors.

        Creates Ray actors directly from config - no intermediate local instances.
        """
        logger.info("Setting up simulation: %s", self.simulation_id)

        # Initialize Ray
        ensure_ray(self.config.ray)

        # Launch PlayerPersonas directly from config
        self._player_persona_handles = self._launch_player_personas()

        # Launch ConductorPersona directly from config (if configured)
        self._conductor_persona_handle = self._launch_conductor_persona()

        if self._conductor_persona_handle:
            # Register all players with conductor
            for player_id in self._player_persona_handles:
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
        logger.info("    Setup complete")

    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute one simulation round.

        A round is the highest-level execution unit in the hierarchy:
        - Round (Simulator) → Operate (PlayerPersona) → Cycle (ConductorPersona)

        The Simulator orchestrates the flow but does NOT generate observations.
        Observations come from the Conductor (domain coordinator).

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

        # Phase 1: Conductor notifies Players of round state
        self.current_phase = RoundPhase.NOTIFICATION
        if self._conductor_persona_handle is None:
            raise RuntimeError("Conductor is required for player notification")

        # Conductor notifies all registered players with round state
        notifications = ray.get(
            self._conductor_persona_handle.notify.remote(
                round_num, list(self._player_persona_handles.keys())
            )
        )

        # Phase 2: PlayerPersonas execute operate()
        self.current_phase = RoundPhase.PLAYER_DECISION
        operate_futures = {}
        for player_id, notif_dict in notifications.items():
            if player_id in self._player_persona_handles:
                # Create Observation from notification and call persona.operate()
                # All required keys must be present in notif_dict
                if "data" not in notif_dict:
                    raise KeyError(f"notif_dict for {player_id} must have 'data' key")
                if "source_id" not in notif_dict:
                    raise KeyError(
                        f"notif_dict for {player_id} must have 'source_id' key"
                    )
                observation = Observation(
                    data=notif_dict["data"],
                    source_id=notif_dict["source_id"],
                    observation_id=(
                        notif_dict["observation_id"]
                        if "observation_id" in notif_dict
                        else None
                    ),
                    target_id=(
                        notif_dict["target_id"]
                        if "target_id" in notif_dict
                        else player_id
                    ),
                    step=notif_dict["step"] if "step" in notif_dict else round_num,
                    metadata=notif_dict["metadata"] if "metadata" in notif_dict else {},
                )
                # num_steps can be configured per-player in notif_dict
                if "num_steps" not in notif_dict:
                    raise KeyError(
                        f"notif_dict for {player_id} must have 'num_steps' key"
                    )
                num_steps = notif_dict["num_steps"]
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

        # Phase 3: ConductorPersona collects response_pool and executes cycle()
        if self._conductor_persona_handle:
            self.current_phase = RoundPhase.COORDINATION

            # Collect final actions from all turns and send to Conductor (response_pool)
            actions = []
            for tr in turn_results.values():
                if tr["final_action"]:
                    action_dict = tr["final_action"]
                    # Validate required keys
                    if "action_type" not in action_dict:
                        raise KeyError("action_dict must have 'action_type' key")
                    if "payload" not in action_dict:
                        raise KeyError("action_dict must have 'payload' key")
                    if "source_id" not in action_dict:
                        raise KeyError("action_dict must have 'source_id' key")
                    action = Action(
                        action_type=action_dict["action_type"],
                        payload=action_dict["payload"],
                        source_id=action_dict["source_id"],
                        action_id=(
                            action_dict["action_id"]
                            if "action_id" in action_dict
                            else None
                        ),
                        metadata=(
                            action_dict["metadata"] if "metadata" in action_dict else {}
                        ),
                    )
                    actions.append(action)

            ray.get(self._conductor_persona_handle.receive_responses.remote(actions))

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
        logger.info("Starting simulation: %s", self.simulation_id)
        self.status = SimulatorStatus.RUNNING

        all_results = []

        for round_num in range(1, self.config.setting["total_rounds"] + 1):
            logger.info(
                "    Round %d/%d", round_num, self.config.setting["total_rounds"]
            )

            round_result = await self.run_round(round_num)
            all_results.append(round_result)

            logger.debug("        Round %d complete", round_num)

        self.status = SimulatorStatus.TERMINATED
        logger.info("Simulation completed successfully")

        return all_results

    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        logger.info("Shutting down simulation: %s", self.simulation_id)

        # Shutdown all Persona actors
        shutdown_futures = []
        for handle in self._player_persona_handles.values():
            shutdown_futures.append(handle.shutdown.remote())
        if self._conductor_persona_handle:
            shutdown_futures.append(self._conductor_persona_handle.shutdown.remote())

        ray.get(shutdown_futures)

        self.status = SimulatorStatus.TERMINATED
        logger.info("    Shutdown complete")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_round_history(self, round_num: int) -> Optional[Dict[str, Any]]:
        """Get historical data for a specific round."""
        for record in self.history:
            if "round" in record and record["round"] == round_num:
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
            "total_rounds": self.config.setting["total_rounds"],
            "player_count": len(self._player_persona_handles),
            "has_conductor": self._conductor_persona_handle is not None,
            "round_clock": self.round_clock.to_dict(),
        }

    def get_player_handle(self, player_id: str) -> Optional[ray.actor.ActorHandle]:
        """Get Ray actor handle for a specific player."""
        if player_id not in self._player_persona_handles:
            return None
        return self._player_persona_handles[player_id]

    def get_conductor_handle(self) -> Optional[ray.actor.ActorHandle]:
        """Get Ray actor handle for the conductor."""
        return self._conductor_persona_handle
