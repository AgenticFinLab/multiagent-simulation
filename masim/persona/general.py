"""General Persona Implementation for MASim Framework.

This module provides the concrete Persona implementations that wrap
Player entities with infrastructure coordination.

For abstract definitions and documentation, see base.py.

Architecture:
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  SIMULATOR (owns CommunicationChannel)                                  │
    │   • channel.encode_and_deliver() → persona.receive_message()           │
    │   • persona.collect_pending_infos() → build_message_from_info(Info)   │
    └─────────────────────────────────────────────────────────────────────────┘
                                    │
                     [via Ray remote calls only]
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  PERSONA (Ray Actor) - Simulator's only interface                      │
    │   • Owns Player (hidden from Simulator)                               │
    │   • Owns SendReceiveProxy (self.message_proxy)                        │
    ├─────────────────────────────────────────────────────────────────────────┤
    │  OUTBOUND FLOW:                                                        │
    │    Player.turn() → Info(payload) [player layer]                       │
    │    Persona → proxy.enqueue_info(info)                                │
    │    Simulator → persona.collect_pending_infos()                        │
    │    Simulator → build_message_from_info(info) → Message                │
    │    Simulator → channel.encode(Message) → SimPacket → ray.remote       │
    │                                                                        │
    │  INBOUND FLOW:                                                         │
    │    SimPacket → channel.decode() → Message                             │
    │    Simulator → persona.receive_message(Message)                       │
    │             → proxy.handle_incoming(Message) [proxy builds Info, queues]│
    │    Persona.operate() → proxy.get_received_senders()  [data]          │
    │                     → player.is_received_ready()  [decision]         │
    │                     → proxy.get_received_infos() → Info               │
    │                     → player.receive_info(info)                      │
    └─────────────────────────────────────────────────────────────────────────┘
                                    │
                           [after all expected senders]
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────────┐
    │  PLAYER (internal, never seen by Simulator)                            │
    │   • decide() → outbound_messages                                      │
    │   • receive_info(info) → reads in perceive() via Observation.inbounds│
    └─────────────────────────────────────────────────────────────────────────┘

Key Design Principles:
    1. ENCAPSULATION: Persona OWNS and hides Player
    2. PROXY OWNERSHIP: SendReceiveProxy is SINGLE source of truth for I/O
    3. CHANNEL ISOLATION: Proxy cannot access Channel (Simulator-owned)
    4. SINGLE DELIVERY: Info units delivered to Player ONCE (in operate())
    5. TOPOLOGY-DRIVEN: Expected senders derived from topology graph
    6. THREE-LAYER MODEL: Info (player) → Message (proxy) → SimPacket (channel)
"""

import asyncio
import time

import ray
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

from masim.persona.base import BasePersona
from masim.proxy.base import Message
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
        self.message_proxy = SendReceiveProxy(
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

        Flow:
            1. Wait until Player.is_received_ready() returns True
               (Player owns readiness decision; proxy provides received_senders data)
            2. Deliver all pending Info units from proxy to Player
            3. Execute Player.turn() (perceive → decide → act)
            4. Extract pending Info units from Player and queue to proxy
            5. Return TurnResult

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

        level = kwargs.get("level", 0)

        # Wait until Player decides it has received enough Info units
        # Proxy provides DATA (which senders arrived), Player owns the DECISION
        while not self.player.is_received_ready(
            round_num,
            self.message_proxy.get_received_senders(),
            level=level,
        ):
            await asyncio.sleep(0.01)

        # Deliver from proxy to Player (single delivery point)
        pending_infos = self.message_proxy.get_received_infos()
        for info in pending_infos:
            self.player.receive_info(info)

        # Delegate to internal Player.turn() (HIDDEN from Simulator)
        turn_result = await self.player.turn(round_num, **kwargs)

        # Extract Info units from Player and queue to proxy
        # Player stores pending Info in pending_info after decide()
        infos = self.player.pending_info.copy()
        self.player.pending_info.clear()
        for info in infos:
            self.message_proxy.enqueue_info(info)

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
    #                    INFO COLLECTION (Simulator calls this)
    # =========================================================================

    def collect_pending_infos(self) -> List[Dict[str, Any]]:
        """
        Collect all queued Info units from proxy for Simulator dispatch.

        Called by Simulator via persona.collect_pending_infos().
        Returns Info units with sender/target info for channel processing.

        Returns:
            List of dicts with keys: info, sender_id, target_ids, round_num
        """
        if not self.topology:
            return []

        # Dequeue Info units from proxy (owned by Persona)
        infos = self.message_proxy.dequeue_infos()

        # Get targets from topology
        targets = self.topology.get_targets(self.identity)

        result = []
        for info in infos:
            result.append(
                {
                    "info": info,
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
        Receive a message delivered by Simulator via CommunicationChannel.

        Called by Simulator: channel.encode_and_deliver() → persona.receive_message()
        Delegates entirely to SendReceiveProxy - proxy is SINGLE owner of inbound state.

        Inbound delivery flow:
            Simulator → persona.receive_message() → proxy.handle_incoming()
            Persona.operate() → proxy.get_received_infos() → player.receive_info()

        Args:
            message: The decoded Message object from channel
        """
        # Log the received message
        self.storage.record_message(
            player_id=self.identity,
            round_num=self.current_round,
            message=message,
            direction="received",
        )

        # Queue to proxy - proxy is SINGLE source of truth for received Info
        # Player receives Info units only in operate() via get_received_infos()
        self.message_proxy.handle_incoming(message)

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
