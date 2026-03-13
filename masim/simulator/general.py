"""General Simulator implementation for the MASim framework.

This module provides ready-to-use concrete implementations:
- ensure_ray(): Initialize Ray cluster
- get_actor_name(): Construct deterministic actor names
- load_class(): Dynamic class loading from module path
- GeneralSimulator: Full-featured simulator with Ray integration

For abstract base classes, see `base.py`.

Architectural Note:
    The Simulator is a system-level orchestrator. All agents are Players,
    with some having role='coordinator' for multi-agent coordination.

    The framework supports three modes:
    1. Zero coordinators: Pure peer-to-peer simulation
    2. One coordinator: Traditional hierarchical coordination
    3. Multiple coordinators: Multi-level coordination hierarchy

    Execution flow with coordinator(s):
    1. COORDINATOR_NOTIFY: Coordinator sends initial messages to players
    2. PLAYER_DECISION: All regular players execute in parallel
    3. COORDINATOR_COLLECT: Coordinators collect player responses
    4. COORDINATOR_BROADCAST: Coordinators broadcast results

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
import os
from typing import Any, Dict, List, Optional

import ray

from masim.simulator.base import (
    BaseSimulator,
    SimulationConfig,
    SimulatorStatus,
    RoundPhase,
)
from masim.player.base import PlayerConfig
from masim.persona.general import PlayerPersona
from masim.communication.general import GeneralCommunicationChannel
from masim.proxy.general import build_message_from_info
from masim.utils.topology import TopologyGraph

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
        entity_id: Entity identifier (player_id)

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
    - Flexible coordinator support (zero, one, or multiple)

    The Simulator is a system-level orchestrator:
    - All agents are Players with perceive/decide/act pattern
    - Players with role='coordinator' execute first and orchestrate others
    - Regular players respond to coordinator notifications

    Coordinator Flow (per round):
        1. COORDINATOR_NOTIFY: Coordinator(s) run perceive/decide/act to send init messages
        2. PLAYER_DECISION: Regular players run in parallel, respond to notifications
        3. COORDINATOR_PROCESS: Coordinator(s) collect and process responses
        4. COORDINATOR_BROADCAST: Coordinator(s) broadcast final results

    No Coordinator Mode:
        When no coordinator is configured, the Simulator sends default notifications
        and all players run in parallel without centralized coordination.

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
        # Initialize communication channel from config
        comm_config = config.communication
        self.communication = GeneralCommunicationChannel(comm_config)
        logger.info("GeneralSimulator initialized: %s", self.simulation_id)

    # =========================================================================
    # Ray Actor Management
    # =========================================================================

    def _launch_player_personas(self) -> Dict[str, ray.actor.ActorHandle]:
        """
        Create and launch PlayerPersonas as Ray actors directly from config.

        All players are equal - topology defines their communication targets.
        No role-based separation; each player sends to their topology targets.

        Returns:
            Dict mapping player_id -> Ray actor handle
        """
        ensure_ray(self.config.ray)
        handles = {}

        RemotePlayerPersona = ray.remote(PlayerPersona)

        for player_id, player_cfg in self.config.players.items():
            player_class = load_class(player_cfg["class"])
            player_config = PlayerConfig(
                name=player_cfg["name"], **player_cfg["config"]
            )

            actor_name = get_actor_name(self.config.setting["name"], player_id)
            handle = RemotePlayerPersona.options(
                name=actor_name,
                lifetime="detached",
                namespace=self.config.ray["namespace"],
            ).remote(
                player_class=player_class,
                player_config=player_config,
                persona_config=player_cfg["persona"],
            )

            handles[player_id] = handle
            logger.info("    Launched: %s", actor_name)

        return handles

    # =========================================================================
    # Simulation Lifecycle
    # =========================================================================

    async def setup(self) -> None:
        """
        Set up the simulation: create and launch Persona Ray actors.

        All players are equal - topology defines their communication.
        """
        logger.info("Setting up simulation: %s", self.simulation_id)

        # Initialize Ray
        ensure_ray(self.config.ray)

        # Build topology graph for execution ordering
        self.topology = TopologyGraph(self.config.topology)

        # Launch all PlayerPersonas (topology-driven, no role separation)
        self.player_persona_handles = self._launch_player_personas()

        # Initialize all Persona actors
        init_futures = [
            h.initialize.remote() for h in self.player_persona_handles.values()
        ]
        ray.get(init_futures)

        # Setup topology connections for message passing
        self._setup_topology()

        logger.info("    Total players: %d", len(self.player_persona_handles))
        self.status = SimulatorStatus.READY
        logger.info("    Setup complete")

    def _setup_topology(self) -> None:
        """
        Configure topology for all players.

        Passes full topology config and peer handles to each Persona.
        Each Persona extracts its own targets from the topology.

        Also saves the initial topology diagram as round 0 (before simulation starts).
        """
        logger.info("    Setting up topology...")

        # Pass topology config and peer handles to each persona
        for _, handle in self.player_persona_handles.items():
            ray.get(handle.set_topology.remote(self.config.topology))
            ray.get(handle.set_peer_handles.remote(self.player_persona_handles))

        # Save initial topology diagram as round 0 (before simulation starts)
        diagrams_dir = os.path.join(self.config.setting["record_path"], "diagrams")
        self.topology.save_round_diagram(diagrams_dir, round_num=0)

    def phase_execute(
        self,
        round_num: int,
        level_handles: Dict[str, ray.actor.ActorHandle],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        PHASE 1: EXECUTE - Players run operate() in parallel.

        Submits operate() calls to all players via Ray .remote().
        Returns immediately - actual execution is parallel.

        Args:
            round_num: Current round number
            level_handles: Dict of player_id -> actor handle to execute
            **kwargs: Additional parameters (e.g., level) passed to operate()

        Returns:
            Dict with futures and ref_to_player for phase_collect()
        """
        self.current_phase = RoundPhase.EXECUTING

        operate_futures = {}
        ref_to_player = {}
        for player_id, handle in level_handles.items():
            future = handle.operate.remote(round_num, **kwargs)
            operate_futures[player_id] = future
            ref_to_player[future] = player_id

        return {
            "futures": operate_futures,
            "ref_to_player": ref_to_player,
        }

    def phase_collect(self, execute_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        PHASE 2: COLLECT - Wait for all operate() to complete.

        Gathers TurnResults from all players in this level.

        Args:
            execute_result: Output from phase_execute() containing futures

        Returns:
            Dict with turn_results mapping player_id -> TurnResult
        """
        futures = execute_result["futures"]
        ref_to_player = execute_result["ref_to_player"]

        turn_results = {}
        pending_refs = list(futures.values())

        while pending_refs:
            ready_refs, pending_refs = ray.wait(
                pending_refs, num_returns=1, timeout=0.1
            )
            for ref in ready_refs:
                turn_result = ray.get(ref)
                player_id = ref_to_player[ref]
                turn_results[player_id] = turn_result

        return {
            "turn_results": turn_results,
            "pending_count": 0,
        }

    def phase_dispatch(
        self,
        level_handles: Dict[str, ray.actor.ActorHandle],
    ) -> None:
        """
        PHASE 3: DISPATCH - Encode Info→Message→SimPacket via CommunicationChannel.

        Architecture (Proxy-Centric Design):

        SEND (collect from proxy):
            Simulator → persona.collect_pending_infos()
                       → persona.message_proxy.dequeue_infos()  [proxy dequeues]
                       → returns [{info, sender_id, target_ids, round_num}]
            Simulator → build_message_from_info(info)  [proxy helper, builds Message]

        RECEIVE (dispatch via channel → proxy):
            Simulator → channel.encode_and_deliver(messages, handles)
                       → target_persona.receive_message(decoded_message)
                       → persona.message_proxy.handle_incoming(message)  [proxy→Info]

        When target persona.operate() is called:
            proxy.get_received_senders()                   [proxy provides data]
            player.is_received_ready(received_senders)     [player decides]
            proxy.get_received_infos()                     [proxy dequeues]
            player.receive_info(info)                      [single delivery]

        Ownership boundaries:
            Simulator owns Channel (encoding, routing, logging)
            Persona owns Proxy (queuing, readiness tracking)

        This ensures Level N messages arrive before Level N+1 starts.

        Args:
            level_handles: Dict of player_id -> actor handle for this level
        """
        # Step 1: Collect Info units from all players in this level
        collect_refs = []
        for handle in level_handles.values():
            ref = handle.collect_pending_infos.remote()
            collect_refs.append(ref)

        # Get all collected Info unit lists
        all_info_lists = ray.get(collect_refs) if collect_refs else []

        # Step 2: Build Messages from Info units via build_message_from_info()
        # (proxy-layer helper — NOT a Channel method)
        all_messages = []
        for info_list in all_info_lists:
            for info_data in info_list:
                info = info_data["info"]
                sender_id = info_data["sender_id"]
                target_ids = info_data["target_ids"]
                round_num = info_data["round_num"]

                for target_id in target_ids:
                    message = build_message_from_info(
                        info=info,
                        sender_id=sender_id,
                        target_id=target_id,
                        round_num=round_num,
                    )
                    all_messages.append(message)

        # Step 3: Dispatch via CommunicationChannel
        if all_messages:
            dispatch_refs = self.communication.encode_and_deliver(
                messages=all_messages,
                handles=self.player_persona_handles,
            )
            # Wait for all messages to be delivered
            if dispatch_refs:
                ray.get(dispatch_refs)

    async def run_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute one simulation round with level-based execution ordering.

        ┌─────────────────────────────────────────────────────────────────────┐
        │                    ROUND EXECUTION FLOW                             │
        ├─────────────────────────────────────────────────────────────────────┤
        │  For each level (Level 0 → Level 1 → ... → Level N):               │
        │                                                                     │
        │  1. EXECUTE: Players run operate() in parallel                     │
        │              └─► Waits for is_received_ready() before turn()        │
        │              └─► perceive() → decide() → act()                     │
        │              └─► Received Info units delivered via proxy.get_received_infos() │
        │              └─► Info units declared in decide() via outbound_messages │
        │                                                                     │
        │  2. COLLECT: Wait for all operate() to complete                    │
        │              └─► Gather TurnResults from all players               │
        │                                                                     │
        │  3. DISPATCH: Encode Info→Message→SimPacket, deliver to targets│
        │              └─► build_message_from_info(info) → Message               │
        │              └─► channel.encode(Message) → SimPacket → ray.remote    │
        │              └─► handle_incoming(Message) queues Info in receive_queue│
        │                                                                     │
        │  Then proceed to next level...                                     │
        └─────────────────────────────────────────────────────────────────────┘

        Args:
            round_num: Current round number (1-indexed)

        Returns:
            Round results containing round, round_clock, execution_levels
        """
        self.round_clock.tick_start()
        self.current_round = round_num

        execution_levels = self.topology.get_execution_levels()

        for level, level_players in enumerate(execution_levels):
            level_handles = {
                pid: self.player_persona_handles[pid]
                for pid in level_players
                if pid in self.player_persona_handles
            }

            # ─────────────────────────────────────────────────────────────────
            # PHASE 1: EXECUTE - Players run operate() in parallel
            # ─────────────────────────────────────────────────────────────────
            execute_result = self.phase_execute(round_num, level_handles, level=level)

            # ─────────────────────────────────────────────────────────────────
            # PHASE 2: COLLECT - Wait for all operate() to complete
            # ─────────────────────────────────────────────────────────────────
            self.phase_collect(execute_result)

            # ─────────────────────────────────────────────────────────────────
            # PHASE 3: DISPATCH - Encode Info→Message→SimPacket, deliver to targets
            # ─────────────────────────────────────────────────────────────────
            self.phase_dispatch(level_handles)

        # ─────────────────────────────────────────────────────────────────────
        # PHASE 4: RECORD - Save topology diagram (rate-limited to reduce I/O)
        # ─────────────────────────────────────────────────────────────────────────
        save_interval = self.config.setting["save_diagram_interval"]
        if save_interval > 0 and round_num % save_interval == 0:
            diagrams_dir = os.path.join(self.config.setting["record_path"], "diagrams")
            self.topology.save_round_diagram(diagrams_dir, round_num=round_num)

        # Finalize round
        self.round_clock.tick_end()
        self.current_phase = RoundPhase.COMPLETE

        round_results = {
            "round": round_num,
            "round_clock": self.round_clock,
            "execution_levels": execution_levels,
        }
        self.history.append(round_results)

        return round_results

    async def run(self) -> List[Dict[str, Any]]:
        """
        Run the complete simulation.

        Returns:
            List of recent round results (from bounded history deque)
        """
        logger.info("Starting simulation: %s", self.simulation_id)
        self.status = SimulatorStatus.RUNNING

        # NOTE: Don't accumulate all_results in memory - use self.history (HistoryBuffer)
        # Full history is already persisted via HistoryBuffer cold storage
        for round_num in range(1, self.config.setting["total_rounds"] + 1):
            logger.info(
                "    Round %d/%d", round_num, self.config.setting["total_rounds"]
            )

            await self.run_round(round_num)

            logger.debug("        Round %d complete", round_num)

        self.status = SimulatorStatus.TERMINATED
        logger.info("Simulation completed successfully")

        # Return recent history (from hot storage)
        return self.history.recent

    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        logger.info("Shutting down simulation: %s", self.simulation_id)

        # Shutdown all Persona actors
        shutdown_futures = []
        for handle in self.player_persona_handles.values():
            shutdown_futures.append(handle.shutdown.remote())

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
            "player_count": len(self.player_persona_handles),
            "round_clock": self.round_clock.to_dict(),
        }

    def get_player_handle(self, player_id: str) -> Optional[ray.actor.ActorHandle]:
        """Get Ray actor handle for a specific player."""
        if player_id not in self.player_persona_handles:
            return None
        return self.player_persona_handles[player_id]
