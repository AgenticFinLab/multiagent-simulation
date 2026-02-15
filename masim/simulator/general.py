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
from typing import Any, Dict, List, Optional, Tuple

import ray

from masim.simulator.base import (
    BaseSimulator,
    SimulationConfig,
    SimulatorStatus,
    RoundPhase,
)
from masim.player.base import Action, PlayerConfig
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

    def phase_notification(self, round_num: int) -> Dict[str, Dict[str, Any]]:
        """
        Phase 1: Conductor notifies Players of round state.

        Args:
            round_num: Current round number

        Returns:
            Notifications dict mapping player_id -> notification dict
        """
        self.current_phase = RoundPhase.NOTIFICATION
        if self._conductor_persona_handle is None:
            raise RuntimeError("Conductor is required for player notification")

        notifications = ray.get(
            self._conductor_persona_handle.notify.remote(
                round_num, list(self._player_persona_handles.keys())
            )
        )
        return notifications

    def phase_player_decision(
        self, round_num: int, notifications: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 2: Submit PlayerPersona operate() calls in parallel.

        This phase only SUBMITS tasks - collection happens in phase_coordination
        to enable streaming to Conductor.

        Args:
            round_num: Current round number
            notifications: Notifications from conductor

        Returns:
            Dict containing:
                - futures: Dict mapping player_id -> Ray ObjectRef
                - ref_to_player: Dict mapping ObjectRef -> player_id (reverse lookup)
        """
        self.current_phase = RoundPhase.PLAYER_DECISION

        # =================================================================
        # PARALLEL EXECUTION via Ray - Submit Phase
        # =================================================================
        # .remote() returns immediately - all players START executing in parallel
        operate_futures = {}
        ref_to_player = {}
        for player_id, notif_dict in notifications.items():
            if player_id in self._player_persona_handles:
                future = self._player_persona_handles[player_id].operate.remote(
                    notif_dict, round_num, notif_dict["num_steps"]
                )
                operate_futures[player_id] = future
                ref_to_player[future] = player_id

        return {
            "futures": operate_futures,
            "ref_to_player": ref_to_player,
        }

    def phase_coordination(
        self,
        player_decision_result: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Any]:
        """
        Phase 3: Delegate response collection and coordination to ConductorPersona.

        ConductorPersona owns the streaming collection logic:
        - Uses ray.wait() to collect results as they arrive
        - Streams each result to internal Conductor
        - Conductor decides when to proceed via ready_responses()

        This enables Conductor-controlled policies:
        - Quorum-based processing (proceed after K responses)
        - Timeout-based processing (proceed after N seconds)
        - First-responder processing (proceed after 1 response)

        Args:
            player_decision_result: Output from phase_player_decision containing futures

        Returns:
            Tuple of (collection_result, cycle_result):
                - collection_result: Dict with turn_results, pending_count
                - cycle_result: CycleResult from Conductor.cycle()
        """
        if self._conductor_persona_handle is None:
            return {"turn_results": {}, "pending_count": 0}, None

        self.current_phase = RoundPhase.COORDINATION

        futures = player_decision_result["futures"]
        ref_to_player = player_decision_result["ref_to_player"]

        # Delegate streaming collection to ConductorPersona
        # Conductor controls when to proceed via ready_responses()
        collection_result: Dict[str, Any] = ray.get(
            self._conductor_persona_handle.collect_responses.remote(
                futures, ref_to_player
            )
        )

        # Conductor executes coordination cycle
        cycle_result = ray.get(self._conductor_persona_handle.cycle.remote())

        return collection_result, cycle_result

    def phase_broadcast(
        self,
        collection_result: Dict[str, Any],
        cycle_result: Any,
    ) -> None:
        """
        Phase 4: Broadcast coordination result to Players.

        Uses Conductor.prepare_broadcast() to customize what message
        is sent to each Player. This allows domain-specific broadcast
        content without changing the broadcast mechanism.

        Args:
            collection_result: Dict with turn_results from phase_coordination
            cycle_result: CycleResult from Conductor.cycle()
        """
        if self._conductor_persona_handle is None or cycle_result is None:
            return

        self.current_phase = RoundPhase.BROADCAST

        # Get customized broadcast message from Conductor
        broadcast_msg = ray.get(
            self._conductor_persona_handle.prepare_broadcast.remote(cycle_result)
        )

        # Broadcast to PlayerPersonas (only those that responded)
        coord_futures = []
        for player_id in collection_result["turn_results"].keys():
            if player_id in self._player_persona_handles:
                coord_futures.append(
                    self._player_persona_handles[player_id].receive_coordination.remote(
                        broadcast_msg
                    )
                )
        if coord_futures:
            ray.get(coord_futures)

    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute one simulation round.

        A round is the highest-level execution unit in the hierarchy:
        - Round (Simulator) -> Operate (PlayerPersona) -> Cycle (ConductorPersona)

        The Simulator orchestrates the flow but does NOT generate observations.
        Observations come from the Conductor (domain coordinator).

        Streaming Response Collection:
        - Players execute in parallel
        - Results stream to Conductor as they arrive
        - Conductor decides when to proceed (quorum, timeout, etc.)

        Args:
            round_num: Current round number (1-indexed)

        Returns:
            Round results containing:
            - turn_results: Dict of player_id -> TurnResult summary
            - coordination: Conductor's coordination decision (if any)
            - pending_count: Players still pending when Conductor proceeded
            - round_clock: Timing metrics for this round
        """
        self.round_clock.tick_start()
        self.current_round = round_num

        # Phase 1: Conductor notifies Players
        notifications = self.phase_notification(round_num)

        # Phase 2: Submit player operate() calls (parallel, non-blocking)
        player_decision_result = self.phase_player_decision(round_num, notifications)

        # Phase 3: Stream results to Conductor, Conductor decides when to proceed
        collection_result, cycle_result = self.phase_coordination(
            player_decision_result
        )

        # Phase 4: Broadcast coordination result to Players
        self.phase_broadcast(collection_result, cycle_result)

        # Finalize round
        self.round_clock.tick_end()
        self.current_phase = RoundPhase.COMPLETE

        round_results = {
            **collection_result,
            "cycle_result": cycle_result,
            "round": round_num,
            "round_clock": self.round_clock,
        }
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
