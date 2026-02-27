"""General Persona Implementation for MASim Framework.

This module provides the concrete Persona implementations that wrap
Player entities with infrastructure coordination.

For abstract definitions and documentation, see base.py.

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor)
                          │
                          └──► BasePlayer (internal, hidden)

Key Design Principles:
    1. ENCAPSULATION: Persona OWNS and hides Player
    2. FACADE PATTERN: Persona aggregates all proxies + domain logic
    3. SINGLE INTERFACE: Simulator only sees Persona's operate()
    4. INFRASTRUCTURE: All observability, storage, communication via Persona
    5. TOPOLOGY-DRIVEN: Message passing based on connection topology

Message Passing Architecture:
    Players send/receive messages through topology-defined connections.
    No role-based execution order - players wait for expected messages
    in their pool before processing.

    ┌─────────┐  send_to  ┌─────────┐  send_to  ┌─────────┐
    │Player A │ ────────► │Player B │ ────────► │Player C │
    └────┬────┘           └────┬────┘           └────┬────┘
         │                     │                     │
         │ ◄── receive_msg ────┼── receive_msg ──►   │
         │                     │                     │
         ▼                     ▼                     ▼
     [pool ready?]         [pool ready?]         [pool ready?]
         │                     │                     │
         ▼                     ▼                     ▼
     [process]             [process]             [process]
"""

import asyncio
import time
from datetime import datetime

import ray
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

from masim.persona.base import BasePersona
from masim.communication.base import Message
from masim.player.base import Inbound
from masim.utils.topology import TopologyGraph
from masim.proxy.base import (
    StorageConfig,
    SendReceiveConfig,
    ResourceConfig,
    MonitoringConfig,
)
from masim.proxy.general import (
    StorageProxy,
    SendReceiveProxy,
    ResourceProxy,
    MonitoringProxy,
)

if TYPE_CHECKING:
    from masim.player.base import (
        BasePlayer,
        PlayerConfig,
        Action,
        StepResult,
        TurnResult,
        PayloadType,
    )


# =============================================================================
#                        PLAYER PERSONA
# =============================================================================


class PlayerPersona(BasePersona):
    """
    Persona for Player entities - the primary interface Simulator uses.

    PlayerPersona OWNS and HIDES the BasePlayer instance. Simulator
    interacts only with PlayerPersona's public methods:
        - initialize(): Set up the Player
        - operate(observation, num_steps): Execute Player's turn
        - shutdown(): Clean up resources
        - get_state_snapshot(): Get state for monitoring

    The internal BasePlayer is completely hidden from Simulator.

    Execution Hierarchy:
        Simulator.round() ──► PlayerPersona.operate()
                                    │
                                    └──► Player.turn() (for loop of steps)
                                               │
                                               └──► Player.step() (perceive→decide→act)
    """

    # =========================================================================
    #                        LIFECYCLE
    # =========================================================================

    async def initialize(self) -> None:
        """Initialize the Persona and its internal Player."""
        if self.is_initialized:
            return

        # Inject storage record_path into player config extras
        # So player can use HistoryBuffer with persona's storage path
        proxy_config = self.config["proxy"]
        storage_record_path = proxy_config["storage"]["record_path"]
        if "extras" not in self.player_config.__dict__:
            self.player_config.extras = {}
        self.player_config.extras["record_path"] = storage_record_path

        # Create the internal Player instance
        self.player = self.player_class(self.player_config)
        await self.player.initialize()

        # Initialize proxies from config
        await self._initialize_proxies()

        self.is_initialized = True

    async def _initialize_proxies(self) -> None:
        """Initialize all proxies from proxy config."""
        proxy_config = self.config["proxy"]

        self.storage = StorageProxy(StorageConfig(**proxy_config["storage"]))
        self.monitoring = MonitoringProxy(
            MonitoringConfig(**proxy_config["monitoring"])
        )
        self.communication = SendReceiveProxy(
            SendReceiveConfig(**proxy_config["communication"])
        )
        self.resource = ResourceProxy(ResourceConfig(**proxy_config["resource"]))

    async def shutdown(self) -> None:
        """
        Shutdown the Persona and its internal Player.

        Called by Simulator during teardown phase.
        """
        if not self.player:
            return

        # Shutdown the Player
        await self.player.shutdown()

        # Log shutdown
        step_count = self.player.state.step_count if self.player else 0
        if self.monitoring:
            await self.monitoring.log_event(
                "player_shutdown",
                {"player_id": self.identity, "steps_completed": step_count},
            )

    # =========================================================================
    #                    MAIN INTERFACE (What Simulator Calls)
    # =========================================================================

    async def operate(
        self,
        round_num: int,
        **kwargs,
    ) -> "TurnResult":
        """
        Execute the Player's turn operation.

        Waits until Player.is_received_ready() returns True, then
        delegates to the hidden Player.turn().

        Args:
            round_num: Current simulation round number
            **kwargs: Additional parameters (e.g., level) passed to Player

        Returns:
            TurnResult from internal Player
        """
        if not self.player:
            raise RuntimeError("PlayerPersona not initialized")

        # Start timing
        self.operate_start_time = time.perf_counter()
        self.current_round = round_num
        if self.monitoring:
            await self.monitoring.start_timer("operate_duration")

        # Wait until Player has received expected inbounds
        while not self.player.is_received_ready(round_num, **kwargs):
            await asyncio.sleep(0.01)

        # Delegate to internal Player.turn() (HIDDEN from Simulator)
        turn_result = await self.player.turn(round_num, **kwargs)

        # NOTE: Message dispatch is handled by Simulator.
        # Simulator calls collect_outbounds() to gather outbounds,
        # then dispatches via CommunicationChannel.encode_and_deliver().

        # Record turn result via StorageProxy
        self.storage.record_turn_result(
            player_id=self.identity,
            round_num=round_num,
            turn_result=turn_result,
        )

        # Record timing metric only (data already stored above)
        if self.monitoring:
            duration = await self.monitoring.stop_timer("operate_duration")
            await self.monitoring.record_metric(
                "operate_completed",
                {
                    "player_id": self.identity,
                    "round_num": round_num,
                    "duration_ms": duration,
                },
            )

        return turn_result

    # =========================================================================
    #                    STATE ACCESS
    # =========================================================================

    def get_state_snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of Player state for monitoring.

        Used by Simulator for debugging/monitoring, NOT for domain logic.
        """
        if not self.player:
            return {"player_id": self.identity, "initialized": False}

        state = self.player.state
        return {
            "player_id": self.identity,
            "initialized": True,
            "turn_count": state.turn_count,
            "step_count": state.step_count,
            "turn_metrics": state.get_turn_metrics(),
            "step_metrics": state.get_step_metrics(),
            "custom_state": state.custom_state,
        }

    def save_state(self) -> Dict[str, Any]:
        """Get persistable state from internal Player."""
        if not self.player:
            return {}
        return self.player.save_state()

    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state to internal Player."""
        if self.player:
            self.player.load_state(state)

    # =========================================================================
    #                    OUTBOUND COLLECTION
    # =========================================================================

    def collect_outbounds(self) -> List[Dict[str, Any]]:
        """
        Collect all raw outbounds declared by Player.

        Collects pending outbounds from Player state and returns them
        with sender/target info for Simulator to build Messages via channel.

        Returns:
            List of dicts with keys: outbound, sender_id, target_ids, round_num
        """
        if not self.player:
            return []

        if not self.topology:
            return []

        # Collect and clear outbounds from Player state
        outbounds = self.player.pending_outbounds.copy()
        self.player.pending_outbounds.clear()

        # Get targets from topology
        targets = self.topology.get_targets(self.identity)

        result = []
        for outbound in outbounds:
            result.append(
                {
                    "outbound": outbound,
                    "sender_id": self.identity,
                    "target_ids": targets,
                    "round_num": self.current_round,
                }
            )

        return result

    # =========================================================================
    #                    TOPOLOGY & MESSAGE PASSING
    # =========================================================================

    def set_topology(self, topology_config: Optional[Dict[str, Any]]) -> None:
        """
        Set the topology configuration using NetworkX graph.

        Creates a TopologyGraph from config, extracts targets and senders
        for this player.

        Args:
            topology_config: Full topology config dict from topology.yml
        """
        self.topology = TopologyGraph(topology_config)

        if self.player:
            # Set targets (who this player can send to)
            targets = self.topology.get_targets(self.identity)
            self.player.topology_targets = targets

        # Set expected senders from topology sources
        self.setup_expected_senders()

    def set_peer_handles(
        self,
        handles: Dict[str, ray.actor.ActorHandle],
    ) -> None:
        """
        Set Ray actor handles for peer communication.

        Only stores handles for targets defined in topology connections.
        Called by Simulator after all actors are created.

        Args:
            handles: Dict mapping player_id -> Ray actor handle (all players)
        """
        if not self.topology:
            self.peer_handles = {}
            return

        # Only keep handles for targets in our topology
        targets = self.topology.get_targets(self.identity)
        self.peer_handles = {
            target_id: handles[target_id]
            for target_id in targets
            if target_id in handles
        }

    def receive_message(self, message: Message) -> None:
        """
        Receive a message from another player.

        Flow: encoded message → channel decode → Message → convert → Inbound

        This is called remotely by other PlayerPersona actors.
        The Message has already been decoded from wire format by the channel.
        Persona converts it to Inbound and injects to Player.

        Args:
            message: The received Message object (already decoded from channel)
        """
        # Record received message immediately
        self.storage.record_message(
            player_id=self.identity,
            round_num=self.current_round,
            message=message,
            direction="received",
        )

        # Convert Message → Inbound and inject to Player
        if self.player:
            inbound = self.convert_message_to_inbound(message)
            self.player.on_inbound(inbound)

    def convert_message_to_inbound(self, message: Message) -> Inbound:
        """
        Convert channel Message to Player-ready Inbound.

        Simply wraps the Message with reception metadata.

        Args:
            message: Message object from channel

        Returns:
            Inbound for Player consumption
        """
        return Inbound(
            message=message,
            time_received=datetime.now().isoformat(),
        )

    # =========================================================================
    #                    EXPECTED SENDERS SETUP
    # =========================================================================

    def setup_expected_senders(self) -> None:
        """
        Derive expected_senders from topology senders and set on Player.

        Called during initialization after topology is set.
        """
        if not self.player:
            return

        if self.topology:
            senders = self.topology.get_senders(self.identity)
            self.player.expected_senders = set(senders)
        else:
            self.player.expected_senders = set()
