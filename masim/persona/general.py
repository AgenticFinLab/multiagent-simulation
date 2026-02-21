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

import time
import ray
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from masim.persona.base import BasePersona
from masim.communication.base import Message, build_message_from_outbound
from masim.utils.topology import TopologyGraph
from masim.proxy.base import (
    StorageConfig,
    CommunicationConfig,
    ResourceConfig,
    MonitoringConfig,
)
from masim.proxy.general import (
    StorageProxy,
    CommunicationProxy,
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
        self.communication = CommunicationProxy(
            CommunicationConfig(**proxy_config["communication"])
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
        num_steps: int = 1,
    ) -> "TurnResult":
        """
        Execute the Player's turn operation.

        Internally delegates to the hidden Player.turn().

        Args:
            round_num: Current simulation round number
            num_steps: Number of steps to execute in this turn (default: 1)

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

        # Delegate to internal Player.turn() (HIDDEN from Simulator)
        # Player reads messages from its own inbox via get_pending_messages()
        turn_result = await self.player.turn(round_num, num_steps)

        # NOTE: Message dispatch is NOT done here.
        # Simulator explicitly calls dispatch_outbound_messages() after operate()
        # to control message timing between execution levels.

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
    #                    OUTBOUND MESSAGE DISPATCH
    # =========================================================================

    def dispatch_outbound_messages(self) -> int:
        """
        Dispatch all outbound messages declared by Player.

        Called by Simulator AFTER operate() to explicitly send messages.
        This allows Simulator to control message timing between levels.

        Collects pending outbounds from Player.state and dispatches via topology.
        - Player declares content via Outbound (payload, content_type, extras)
        - Persona collects and dispatches via topology

        IMPORTANT: This method BLOCKS until all messages are delivered.
        This ensures Level N messages arrive before Level N+1 starts executing.

        Returns:
            Total number of messages sent
        """
        if not self.player:
            return 0

        # Collect and clear outbounds from Player state
        outbounds = self.player.pending_outbounds.copy()
        self.player.pending_outbounds.clear()

        # Collect all message delivery futures
        all_refs: List[ray.ObjectRef] = []
        for outbound in outbounds:
            refs = self._send_outbound_async(outbound)
            all_refs.extend(refs)

        # BLOCK until all messages are delivered
        # This ensures intra-round message delivery (Level N → Level N+1)
        if all_refs:
            ray.get(all_refs)

        return len(all_refs)

    def _send_outbound_async(self, outbound: Any) -> List[ray.ObjectRef]:
        """
        Send an Outbound to all topology targets (non-blocking).

        Routing is determined by topology configuration, not by Player.
        Converts content-focused Outbound to wire-ready Message for each target.

        Args:
            outbound: The Outbound object with payload, content_type, extras

        Returns:
            List of Ray ObjectRefs for message delivery (caller must wait)
        """
        if not self.topology:
            return []

        refs: List[ray.ObjectRef] = []
        targets = self.topology.get_targets(self.identity)

        for target_id in targets:
            if target_id in self.peer_handles:
                # Convert Outbound to Message for each target
                message = build_message_from_outbound(
                    outbound=outbound,
                    sender_id=self.identity,
                    target_id=target_id,
                )

                self.storage.record_message(
                    player_id=self.identity,
                    round_num=self.current_round,
                    message=message,
                    direction="sent",
                )

                target_handle = self.peer_handles[target_id]
                # Submit async, collect ref for later waiting
                ref = target_handle.receive_message.remote(message)
                refs.append(ref)

        return refs

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

            # Set expected senders (who this player expects messages from)
            senders = self.topology.get_senders(self.identity)
            self.player.set_expected_senders(senders)

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

        This is called remotely by other PlayerPersona actors.
        Messages are IMMEDIATELY injected to Player via on_message().

        Args:
            message: The received Message object
        """
        # Record received message immediately
        self.storage.record_message(
            player_id=self.identity,
            round_num=self.current_round,
            message=message,
            direction="received",
        )

        # Immediately inject message to Player (NOT store in Persona)
        # Player stores in its own inbox for retrieval via get_pending_messages()
        if self.player:
            self.player.on_message(message)

    # =========================================================================
    #                    MESSAGE READINESS CONTROL
    # =========================================================================

    def has_received_expected_messages(self) -> bool:
        """
        Check if player has received all expected messages.

        Delegates to internal Player's readiness check.
        """
        if not self.player:
            return True
        return self.player.has_received_expected_messages()

    def set_expected_senders(self, senders: List[str]) -> None:
        """
        Set which senders this player expects messages from.

        Delegates to internal Player.
        """
        if self.player:
            self.player.set_expected_senders(senders)

    def clear_message_inbox(self) -> None:
        """
        Clear message inbox after round processing.

        Delegates to internal Player.
        """
        if self.player:
            self.player.clear_message_inbox()
