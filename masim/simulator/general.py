"""General Simulator implementation for the MASim framework.

This module provides the concrete GeneralSimulator with full Ray integration.

Utility functions are in utils/:
    masim.utils.ray_utils  → ensure_ray(), get_actor_name()
    masim.utils.config     → load_class()

For abstract base classes, see `simulator/base.py`.

Extension hooks (override in subclass for customization):
    update_topology(round_num)
        Called at the start of every round. Default: no-op (static topology).
        Override to rewire agents, add/remove edges, or switch between
        feedforward and feedback configurations.
        After any mutation: call topology.invalidate_levels_cache() +
        _update_actor_topology_slices() to push new topology slices AND
        updated peer handles to all affected actors.

Round execution (for each topology level):
    Phase 1 EXECUTE: Submit persona.operate(round_num, level=N) in parallel
                     → returns (TurnResult, pending_infos) tuple
    Phase 2 COLLECT: ray.get all operate futures → gather TurnResults + pending_infos
    Phase 3 DISPATCH: build_message_from_info → channel.encode_and_deliver
                      → target.receive_message [Ray remote, blocks until complete]
    Phase 4 RECORD:  save_round_diagram (rate-limited by save_diagram_interval)

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

import copy
import logging
import json
import os
import re
import tempfile
from typing import Any, Dict, List, Optional

import ray

from masim.simulator.base import (
    BaseSimulator,
    BaseSimulationRunner,
    SimulationConfig,
    SimulatorStatus,
    RoundPhase,
)
from masim.player.base import PlayerConfig
from masim.persona.general import PlayerPersona
from masim.communication.general import GeneralCommunicationChannel
from masim.proxy.general import build_message_from_info
from masim.utils.topology import TopologyGraph
from masim.utils.ray_utils import ensure_ray, get_actor_name
from masim.utils.config import load_class

# Module logger
logger = logging.getLogger("masim.simulator")


# =============================================================================
# General Simulator (Concrete Implementation)
# =============================================================================


class GeneralSimulator(BaseSimulator):
    """
    Concrete implementation of BaseSimulator with full Ray integration.

    Provides:
    - Ray cluster initialization and management via utils/ray_utils.py
    - Persona creation as Ray actors from YAML config (dynamic class loading via utils/config.py)
    - Level-ordered simulation execution (setup, run_round, run, shutdown)
    - History management (HistoryBuffer) and status tracking
    - Topology update hook: override update_topology() for dynamic rewiring

    All agents are Players (including coordinators). Topology levels determine
    execution order — Level 0 nodes run first; each level waits for the previous
    level's phase_dispatch to complete before starting phase_execute.

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

        # simulation.yml exposes these settings, but they used to be ignored.
        # Ray therefore applied its defaults (no restart and no task retry), so
        # a single transient actor/RPC failure aborted the whole simulation.
        actor_options = copy.deepcopy(self.config.ray.get("actor_options") or {})
        supported_actor_options = {
            "max_restarts",
            "max_task_retries",
            "max_concurrency",
        }
        unknown_options = set(actor_options) - supported_actor_options
        if unknown_options:
            raise ValueError(
                "Unsupported ray.actor_options: %s"
                % ", ".join(sorted(unknown_options))
            )

        for player_id, player_cfg in self.config.players.items():
            player_class = load_class(player_cfg["class"])
            config_data = copy.deepcopy(player_cfg["config"])
            if self.config.knowledge:
                extras = config_data.setdefault("extras", {})
                extras.setdefault("knowledge", copy.deepcopy(self.config.knowledge))
            player_config = PlayerConfig(
                name=player_cfg["name"], **config_data
            )

            actor_name = get_actor_name(self.config.setting["name"], player_id)
            handle = RemotePlayerPersona.options(
                **actor_options,
                num_cpus=0,  # I/O-bound actors: don't reserve CPU scheduling slots
                name=actor_name,
                lifetime="detached",
                namespace=self.config.ray["namespace"],
            ).remote(
                player_class=player_class,
                player_config=player_config,
                persona_config=player_cfg["persona"],
            )

            handles[player_id] = handle
            logger.debug("    Launched: %s", actor_name)

        logger.info("    Launched %d actor(s)", len(handles))
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

        Step 1: set_topology — sends each actor only its LOCAL topology slice
                {targets: [...], senders: [...]} instead of the full connections
                dict. Reduces IPC payload from O(N) per actor to O(targets+senders)
                per actor, eliminating O(N²) total transfer at large N.

        Step 2: set_peer_handles — sends each actor only the Ray handles for its
                topology targets (pre-filtered subset, not the full player dict).

        Both steps submit all remote calls concurrently and wait with a single ray.get().
        Step 1 must complete on all actors before Step 2 is submitted,
        because set_peer_handles may reference topology-derived state inside the actor.

        Also saves the initial topology diagram as round 0 (before simulation starts).
        """
        logger.info("    Setting up topology...")

        # Step 1: send each actor only its own local topology slice
        # (targets = who it sends to, senders = who sends to it)
        topology_futures = []
        for player_id, h in self.player_persona_handles.items():
            local_slice = {
                "targets": self.topology.get_targets(player_id),
                "senders": self.topology.get_senders(player_id),
            }
            topology_futures.append(h.set_topology.remote(local_slice))
        ray.get(topology_futures)

        # Step 2: send each actor only its target handles (pre-filtered subset)
        peer_futures = []
        for player_id, h in self.player_persona_handles.items():
            targets = self.topology.get_targets(player_id)
            target_handles = {
                t: self.player_persona_handles[t]
                for t in targets
                if t in self.player_persona_handles
            }
            peer_futures.append(h.set_peer_handles.remote(target_handles))
        ray.get(peer_futures)

        # Save initial topology diagram as round 0 (before simulation starts)
        diagrams_dir = os.path.join(self.config.setting["record_path"], "diagrams")
        self.topology.save_round_diagram(diagrams_dir, round_num=0)

    def _update_actor_topology_slices(
        self,
        player_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Push updated topology slices AND peer handles to actor(s) after a topology mutation.

        Called by subclasses that override update_topology() to push new
        {targets, senders} slices to affected actors via set_topology.remote(),
        then push updated peer handle subsets via set_peer_handles.remote().

        Both steps must complete before the next round's level execution starts,
        so that actors' _topology_targets, _topology_senders, expected_senders,
        AND peer_handles all reflect the new topology.

        Args:
            player_ids: List of player IDs whose slices need updating.
                        If None, all actors are updated (full refresh).
                        For a targeted edge addition A→B, pass ["player_a", "player_b"]
                        since both actors' sender/target lists change.

        Example (from a subclass update_topology override)::

            def update_topology(self, round_num: int) -> None:
                if round_num == 10:
                    self.topology.graph.add_edge("player_1", "player_2")
                    self.topology.invalidate_levels_cache()
                    # Pass both affected players: player_1's targets grew,
                    # player_2's senders grew — and player_1 needs player_2's handle.
                    self._update_actor_topology_slices(["player_1", "player_2"])
        """
        if player_ids is None:
            player_ids = list(self.player_persona_handles.keys())

        # Step 1: push new {targets, senders} slices to all affected actors
        topology_futures = []
        for pid in player_ids:
            if pid not in self.player_persona_handles:
                continue
            h = self.player_persona_handles[pid]
            local_slice = {
                "targets": self.topology.get_targets(pid),
                "senders": self.topology.get_senders(pid),
            }
            topology_futures.append(h.set_topology.remote(local_slice))

        if topology_futures:
            ray.get(topology_futures)

        # Step 2: push updated peer handle subsets (needed for new target edges)
        # Only actors whose targets changed need new handles, but we update all
        # affected actors for safety (set_peer_handles is idempotent).
        peer_futures = []
        for pid in player_ids:
            if pid not in self.player_persona_handles:
                continue
            h = self.player_persona_handles[pid]
            targets = self.topology.get_targets(pid)
            target_handles = {
                t: self.player_persona_handles[t]
                for t in targets
                if t in self.player_persona_handles
            }
            peer_futures.append(h.set_peer_handles.remote(target_handles))

        if peer_futures:
            ray.get(peer_futures)

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

        Gathers TurnResults AND pending Info lists from all players in this level.

        operate() returns a (TurnResult, pending_infos) tuple, so a single ray.get()
        retrieves both the result and the pending Info units — eliminating the
        separate collect_pending_infos() IPC wave that previously followed.

        Args:
            execute_result: Output from phase_execute() containing futures

        Returns:
            Dict with:
              turn_results: player_id -> TurnResult
              all_info_lists: flat list-of-lists, one inner list per actor,
                              each element is a dict {info, sender_id, target_ids, round_num}
        """
        futures = execute_result["futures"]
        ref_to_player = execute_result["ref_to_player"]

        # Single ray.get(): each result is (TurnResult, List[Dict])
        refs = list(futures.values())
        all_results = ray.get(refs)

        turn_results = {}
        all_info_lists = []
        for ref, (turn_result, info_list) in zip(refs, all_results):
            player_id = ref_to_player[ref]
            turn_results[player_id] = turn_result
            all_info_lists.append(info_list)

        return {
            "turn_results": turn_results,
            "all_info_lists": all_info_lists,
            "pending_count": 0,
        }

    def phase_dispatch(
        self,
        all_info_lists: List[List[Dict[str, Any]]],
    ) -> None:
        """
        PHASE 3: DISPATCH - Encode Info→Message→SimPacket via CommunicationChannel.

        Architecture (Proxy-Centric Design):

        SEND (from bundled operate() return value — no separate IPC wave):
            phase_collect() unpacks (TurnResult, pending_infos) from each operate() call.
            pending_infos is passed here directly as all_info_lists.

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
            all_info_lists: Output from phase_collect()["all_info_lists"].
                            Each element is a list of Info dicts from one actor:
                            [{info, sender_id, target_ids, round_num}, ...]
        """
        # Build Messages from Info units via build_message_from_info()
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

        # Dispatch via CommunicationChannel
        if all_messages:
            dispatch_refs = self.communication.encode_and_deliver(
                messages=all_messages,
                handles=self.player_persona_handles,
            )
            # Wait for all messages to be delivered before next level starts
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
        │              └─► Checks is_received_ready() — logs warning if False │
        │              └─► perceive() → decide() → act()                     │
        │              └─► Received Info units delivered via proxy.get_received_infos() │
        │              └─► Info units declared in decide() via pending_info   │
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

        # Extension hook: subclasses may mutate self.topology here for dynamic topologies.
        # Default implementation is a no-op (static topology).
        # After any mutation, the subclass must also call self.topology.invalidate_levels_cache()
        # and self._update_actor_topology_slices() to propagate changes to actors.
        self.update_topology(round_num)

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
            # operate() returns (TurnResult, pending_infos) — both collected here
            # ─────────────────────────────────────────────────────────────────
            collect_result = self.phase_collect(execute_result)

            # ─────────────────────────────────────────────────────────────────
            # PHASE 3: DISPATCH - Encode Info→Message→SimPacket, deliver to targets
            # Uses pending_infos bundled into phase_collect result (no extra IPC wave)
            # ─────────────────────────────────────────────────────────────────
            self.phase_dispatch(collect_result["all_info_lists"])

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

        # This marker is written only after every execution level and message
        # dispatch completed.  It is intentionally simulator-owned instead of
        # inferred from scenario-specific folders such as ``records/market``.
        self._write_resume_checkpoint(
            self.config.setting["record_path"], round_num
        )

        return round_results

    async def run(self) -> List[Dict[str, Any]]:
        """
        Run the complete simulation, resuming from the last completed round
        if on-disk data already exists (Option A: skip-round resume).

        Resume behaviour:
        - Scans record_path for existing batch data to find the highest
          completed round N.
        - Starts the loop from round N+1, skipping rounds 1..N entirely.
        - WARNING: actor custom_state (cash, position, etc.) is re-initialised
          from config defaults, not restored from disk. This is correct for
          coordinators (their state is rebuilt from inbound orders each round)
          but means LLM investor portfolios restart from initial values.
          Use this only when the remaining rounds are independent of the
          exact portfolio state at round N (e.g. price-driven strategies).

        Returns:
            List of recent round results (from bounded history deque)
        """
        logger.info("Starting simulation: %s", self.simulation_id)
        self.status = SimulatorStatus.RUNNING

        total_rounds = self.config.setting["total_rounds"]
        record_path = self.config.setting["record_path"]

        # Detect already-completed rounds from on-disk data
        start_round = self._detect_resume_round(record_path) + 1
        if start_round > 1:
            logger.info(
                "    Resume detected: %d round(s) already on disk, starting from round %d",
                start_round - 1,
                start_round,
            )
        if start_round > total_rounds:
            logger.info(
                "    All %d rounds already completed. Nothing to run.", total_rounds
            )
            self.status = SimulatorStatus.TERMINATED
            return self.history.recent

        # NOTE: Don't accumulate all_results in memory - use self.history (HistoryBuffer)
        # Full history is already persisted via HistoryBuffer cold storage
        for round_num in range(start_round, total_rounds + 1):
            logger.info("    Round %d/%d", round_num, total_rounds)

            await self.run_round(round_num)

            logger.debug("        Round %d complete", round_num)

        # Flush remaining items (hot deque + pending_cold) to disk so that
        # load_rounds() and count_experiment_rounds() see the complete dataset.
        self.history.flush()

        self.status = SimulatorStatus.TERMINATED
        logger.info("Simulation completed successfully")

        # Return recent history (from hot storage)
        return self.history.recent

    @staticmethod
    def _detect_resume_round(record_path: str) -> int:
        """
        Scan record_path for the highest completed round number.

        Uses the market coordinator's turns/ directory (turn_block_N.json),
        where each entry contains a round_num field — one entry per round.
        Falls back to scanning HistoryBuffer cold files (batch_XXXXXXXX_XXXXXXXX.json)
        under record_path/market/ if turns data is absent.
        Returns 0 if no data is found.
        """
        checkpoint_path = os.path.join(record_path, ".masim-progress.json")
        try:
            with open(checkpoint_path, encoding="utf-8") as checkpoint_file:
                checkpoint = json.load(checkpoint_file)
            completed_round = int(checkpoint["completed_round"])
            if completed_round >= 0:
                return completed_round
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            pass

        # Compatibility recovery for EchoChamber runs created before the
        # progress marker existed.  The environment receives the final-level
        # actions; the largest persisted round is therefore the last round
        # that made it through the simulation pipeline.
        environment_messages = os.path.join(record_path, "environment", "messages")
        recovered_round = GeneralSimulator._max_persisted_message_round(
            environment_messages
        )
        if recovered_round:
            logger.info(
                "    Recovered completed round %d from environment messages",
                recovered_round,
            )
            return recovered_round

        market_path = os.path.join(record_path, "market")
        if not os.path.isdir(market_path):
            return 0

        # Primary: read turn_block_*.json files in market/turns/
        turns_path = os.path.join(market_path, "turns")
        if os.path.isdir(turns_path):
            max_round = 0
            for fname in os.listdir(turns_path):
                if not (fname.startswith("turn_block_") and fname.endswith(".json")):
                    continue
                try:
                    with open(os.path.join(turns_path, fname)) as f:
                        block = json.load(f)
                    for record in block.values():
                        rn = (
                            record.get("round_num")
                            if isinstance(record, dict)
                            else None
                        )
                        if rn is not None:
                            max_round = max(max_round, int(rn))
                except Exception:
                    pass
            if max_round > 0:
                return max_round

        # Fallback: count entries in HistoryBuffer cold files under market/*/
        # File naming: batch_{start:08d}_{end:08d}.json  (HistoryBuffer cold storage)
        # File naming: batch_block_N.json                (BlockBasedStoreManager)
        max_round = 0
        for store_name in os.listdir(market_path):
            store_path = os.path.join(market_path, store_name)
            if not os.path.isdir(store_path) or store_name in ("turns", "messages"):
                continue
            total = 0
            for fname in os.listdir(store_path):
                # HistoryBuffer: batch_00000000_00000049.json
                m = re.match(r"batch_(\d{8})_(\d{8})\.json", fname)
                if m:
                    batch_end = int(m.group(2))  # 0-based end index
                    total = max(total, batch_end + 1)
                # BlockBasedStoreManager: batch_block_N.json
                m2 = re.match(r"batch_block_(\d+)\.json", fname)
                if m2:
                    try:
                        with open(os.path.join(store_path, fname)) as f:
                            entries = json.load(f)
                        block_idx = int(m2.group(1))
                        block_size = 50
                        total = max(total, block_idx * block_size + len(entries))
                    except Exception:
                        pass
            max_round = max(max_round, total)
        return max_round

    @staticmethod
    def _max_persisted_message_round(messages_path: str) -> int:
        """Return the largest round in persisted message blocks."""
        if not os.path.isdir(messages_path):
            return 0
        max_round = 0
        for fname in os.listdir(messages_path):
            if not (fname.startswith("msg_block_") and fname.endswith(".json")):
                continue
            try:
                with open(
                    os.path.join(messages_path, fname), encoding="utf-8"
                ) as message_file:
                    block = json.load(message_file)
                for record in block.values():
                    if isinstance(record, dict) and record.get("round_num") is not None:
                        max_round = max(max_round, int(record["round_num"]))
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                continue
        return max_round

    @staticmethod
    def _write_resume_checkpoint(record_path: str, round_num: int) -> None:
        """Atomically persist the latest fully completed round."""
        os.makedirs(record_path, exist_ok=True)
        checkpoint_path = os.path.join(record_path, ".masim-progress.json")
        fd, temporary_path = tempfile.mkstemp(
            prefix=".masim-progress-", suffix=".tmp", dir=record_path
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as checkpoint_file:
                json.dump({"completed_round": int(round_num)}, checkpoint_file)
                checkpoint_file.flush()
                os.fsync(checkpoint_file.fileno())
            os.replace(temporary_path, checkpoint_path)
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

    async def shutdown(self) -> None:
        """Shutdown simulation and release resources."""
        logger.info("Shutting down simulation: %s", self.simulation_id)

        # Flush remaining round-result history to disk.  SimulationRunner calls
        # run_round() individually (bypassing GeneralSimulator.run()), so the
        # in-run() flush may never execute.  Calling flush() here guarantees
        # data integrity regardless of the execution path.  The method is
        # idempotent — a double call (from run() + shutdown()) is harmless.
        self.history.flush()

        # Personas use detached lifetime, so invoking their shutdown method does
        # not terminate the actor process.  Always kill them afterwards; leaving
        # detached actors around leaks workers and IPC resources across runs and
        # is especially damaging to Ray's Plasma store on Windows.
        handles = list(self.player_persona_handles.values())
        ray_healthy = self._local_ray_control_plane_alive()
        try:
            if ray_healthy:
                shutdown_futures = []
                for handle in handles:
                    try:
                        shutdown_futures.append(handle.shutdown.remote())
                    except Exception as exc:
                        logger.warning("Could not request actor shutdown: %s", exc)

                # Resolve independently so one unavailable actor cannot prevent
                # healthy actors from completing their own cleanup.
                for future in shutdown_futures:
                    try:
                        ray.get(future)
                    except Exception as exc:
                        logger.warning("Actor cleanup did not complete: %s", exc)
        finally:
            if ray_healthy:
                for handle in handles:
                    try:
                        ray.kill(handle, no_restart=True)
                    except Exception as exc:
                        logger.debug("Actor was already unavailable during kill: %s", exc)
                ray.shutdown()
            elif ray.is_initialized():
                # Submitting actor RPCs after the local GCS has died blocks for
                # Ray's 60-second reconnect timeout and can end in a Windows
                # native access violation.  At this point there is no control
                # plane left with which to perform graceful actor cleanup.
                logger.warning(
                    "Ray GCS is unavailable; skipping remote cleanup to avoid "
                    "the reconnect/access-violation failure path"
                )
            self.player_persona_handles.clear()
            self.status = SimulatorStatus.TERMINATED

        logger.info("    Shutdown complete")

    @staticmethod
    def _local_ray_control_plane_alive() -> bool:
        """Best-effort, non-RPC health check for a locally started Ray GCS."""
        if not ray.is_initialized():
            return False
        try:
            from ray._private import worker
            from ray._private.ray_constants import PROCESS_TYPE_GCS_SERVER

            node = worker._global_node
            if node is None:
                # A remote Ray cluster has no local GCS process to inspect.
                return True
            return any(
                process_type == PROCESS_TYPE_GCS_SERVER
                for process_type, _process in node.live_processes()
            )
        except Exception:
            # Keep compatibility with Ray releases whose private process
            # bookkeeping differs; normal graceful cleanup remains preferable.
            return True

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


# =============================================================================
# General Simulation Runner + CLI Entry
# =============================================================================


class GeneralSimulationRunner(BaseSimulationRunner):
    """Scenario runner paired with :class:`GeneralSimulator`.

    Handles the full lifecycle of a Ray-backed simulation run driven from
    a YAML config: knowledge preflight (when needed), simulator setup, round
    execution, and shutdown. Used both by CLI shims (via the module-level
    :func:`run` convenience function) and by programmatic callers.

    Programmatic usage::

        from masim.simulator.general import GeneralSimulationRunner

        runner = GeneralSimulationRunner.from_config(
            "configs/FlashCrash/Rag/simulation.yml"
        )
        await runner.execute()
    """

    def _build_simulator(self, config: SimulationConfig) -> "GeneralSimulator":
        return GeneralSimulator(config)


# ---------------------------------------------------------------------------
# CLI shell — imported by every examples/*/run_*.py shim
# ---------------------------------------------------------------------------

_BANNER_WIDTH = 70


def _print_banner(
    scenario: str,
    variant: str,
    total_rounds: int,
    phenomenon: Optional[str] = None,
    *,
    has_knowledge: bool = False,
) -> None:
    """Print the standard simulation startup banner."""
    sep = "=" * _BANNER_WIDTH
    print(f"\n{sep}")
    if has_knowledge:
        print(f"{scenario} Simulation - {variant} Agents (RAG-Augmented)")
    else:
        print(f"{scenario} Simulation - {variant} Agents")
    print(sep)
    if phenomenon:
        print(f"Phenomenon: {phenomenon}")
    if has_knowledge:
        print("Mode:       RAG-Augmented LLM Decision-Making")
        print("Note:       Documents pre-processed during setup (shared cache).")
    print(f"Rounds:     {total_rounds}")
    print(f"{sep}\n")


def run(
    *,
    scenario: str,
    default_config: str,
    variant: Optional[str] = None,
    phenomenon: Optional[str] = None,
    load_env: bool = True,
) -> None:
    """Universal CLI entry point for :class:`GeneralSimulator` scenarios.

    Every ``examples/{Scenario}/{Variant}/run_*.py`` shim calls this
    function. Knowledge preprocessing is auto-detected from the YAML
    config content — callers never need to choose between different
    runners for Rule / LLM / RuleLLM / Rag variants.

    Parameters
    ----------
    scenario : str
        Human-readable scenario name printed in the banner
        (e.g. ``"FlashCrash"``).
    default_config : str
        Config path used when caller omits ``-c``. Always relative to the
        project root (e.g. ``"configs/FlashCrash/Rag/simulation.yml"``).
    variant : str, optional
        Variant label for the banner. Auto-detected from the config path
        when omitted (e.g. ``.../LLM/simulation.yml`` → ``"LLM"``).
    phenomenon : str, optional
        One-line phenomenon description shown in the banner.
    load_env : bool
        When ``True`` (default), call :func:`dotenv.load_dotenv` before
        any preprocessing. Pass ``False`` only for pure-Rule scenarios
        that require no API keys.
    """
    # Delayed imports: keep base module import free of dotenv / argparse
    # side effects so ``from masim.simulator.general import GeneralSimulator``
    # stays cheap for tests and notebooks.
    import argparse
    import asyncio
    import traceback

    from masim.simulator.base import detect_variant, extract_knowledge_config
    from masim.utils.config import load_config, setup_logging

    if load_env:
        from dotenv import load_dotenv
        load_dotenv()

    setup_logging()

    # ── CLI parsing ──────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description=f"Run {scenario} Simulation")
    parser.add_argument(
        "-c", "--config", type=str, default=default_config,
        help="Path to the simulation YAML config",
    )
    parser.add_argument(
        "-r", "--rounds", type=int, default=None,
        help="Override total_rounds in the config",
    )
    args = parser.parse_args()

    # ── Config load + optional round override ────────────────────────────
    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)
    if args.rounds:
        config.setting["total_rounds"] = args.rounds

    resolved_variant = variant or detect_variant(args.config)
    has_knowledge = extract_knowledge_config(config) is not None

    _print_banner(
        scenario, resolved_variant, config.setting["total_rounds"],
        phenomenon, has_knowledge=has_knowledge,
    )

    # ── Runner lifecycle ─────────────────────────────────────────────────
    runner = GeneralSimulationRunner(config)
    try:
        asyncio.run(runner.execute())
        sep = "=" * _BANNER_WIDTH
        print(f"\n{sep}")
        print(f"Simulation Complete! Rounds: {config.setting['total_rounds']}")
        print(sep)
    except Exception:
        sep = "=" * _BANNER_WIDTH
        print(f"\n{sep}")
        print("SIMULATION FAILED WITH ERROR:")
        print(sep)
        traceback.print_exc()
        raise
