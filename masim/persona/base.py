"""MASim Persona Layer - Base Classes and Interfaces

The Persona is the PRIMARY EXTERNAL INTERFACE for simulation entities.
Simulator interacts ONLY with Persona - Player is hidden as internal detail.

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor)
                          │
                          └──► BasePlayer (internal, hidden)

For concrete implementations, see general.py.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TYPE_CHECKING

import ray

from masim.utils.topology import TopologyGraph

if TYPE_CHECKING:
    from masim.proxy.base import (
        SendReceiveProxy,
        StorageProxy,
        ResourceProxy,
        MonitoringProxy,
    )
    from masim.communication.base import Message
    from masim.player.base import BasePlayer, PlayerConfig, TurnResult


# =============================================================================
#                          BASE PERSONA
# =============================================================================


class BasePersona(ABC):
    """
    Abstract base class for Persona - the interface Simulator uses.

    All methods that Simulator or other Personas call must be declared here.
    Concrete implementation is in general.py (PlayerPersona).
    """

    def __init__(
        self,
        player_class: Type["BasePlayer"],
        player_config: "PlayerConfig",
        persona_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize BasePersona with Player class and configuration.

        Args:
            player_class: The Player class to instantiate
            player_config: Configuration for the Player
            persona_config: Optional Persona-specific configuration
        """
        # Configuration
        self.config: Dict[str, Any] = persona_config or {}

        # Store class and config for deferred Player creation
        self.player_class: Type["BasePlayer"] = player_class
        self.player_config: "PlayerConfig" = player_config

        # Identity (extracted from config for direct access)
        self.identity: str = player_config.identity

        # Internal Player instance (HIDDEN from Simulator)
        self.player: Optional["BasePlayer"] = None

        # Proxy references
        self.communication: Optional["SendReceiveProxy"] = None
        self.storage: Optional["StorageProxy"] = None
        self.resource: Optional["ResourceProxy"] = None
        self.monitoring: Optional["MonitoringProxy"] = None

        # Lifecycle flag
        self.is_initialized: bool = False

        # Operate timing
        self.operate_start_time: Optional[float] = None

        # Topology graph for message routing
        self.topology: Optional[TopologyGraph] = None

        # Peer actor handles for direct message passing
        self.peer_handles: Dict[str, ray.actor.ActorHandle] = {}

        # Current round number for message recording
        # Round 0 = setup (before simulation), Round 1+ = actual rounds
        self.current_round: int = 0

    # =========================================================================
    #                        LIFECYCLE
    # =========================================================================

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the Persona and its internal Player."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the Persona and release resources."""
        ...

    # =========================================================================
    #                    MAIN INTERFACE (Called by Simulator)
    # =========================================================================

    @abstractmethod
    async def operate(
        self,
        round_num: int,
        **kwargs,
    ) -> "TurnResult":
        """
        Execute the Player's turn operation.

        Args:
            round_num: Current simulation round number
            **kwargs: Additional parameters (e.g., level)

        Returns:
            TurnResult from internal Player
        """
        ...

    # =========================================================================
    #                    STATE ACCESS
    # =========================================================================

    @abstractmethod
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of Player state for monitoring."""
        ...

    @abstractmethod
    def save_state(self) -> Dict[str, Any]:
        """Get persistable state from internal Player."""
        ...

    @abstractmethod
    def load_state(self, state: Dict[str, Any]) -> None:
        """Restore state to internal Player."""
        ...

    # =========================================================================
    #                    TOPOLOGY & MESSAGE PASSING
    # =========================================================================

    @abstractmethod
    def set_topology(self, topology_config: Optional[Dict[str, Any]]) -> None:
        """Set the topology configuration for message routing."""
        ...

    @abstractmethod
    def set_peer_handles(self, handles: Dict[str, ray.actor.ActorHandle]) -> None:
        """Set Ray actor handles for peer communication."""
        ...

    @abstractmethod
    def receive_message(self, message: "Message") -> None:
        """Receive a message from another player (called remotely)."""
        ...

    # =========================================================================
    #                    MESSAGE DISPATCH (Called by Simulator)
    # =========================================================================

    @abstractmethod
    def collect_outbounds(self) -> List[Dict[str, Any]]:
        """
        Collect all raw outbounds declared by Player.

        Called by Simulator to gather outbound messages for dispatch
        via CommunicationChannel.

        Returns:
            List of dicts with keys: outbound, sender_id, target_ids, round_num
        """
        ...

    # =========================================================================
    #                    EXPECTED SENDERS SETUP
    # =========================================================================

    @abstractmethod
    def setup_expected_senders(self) -> None:
        """
        Derive expected_senders from topology and set on Player.

        Called during initialization after topology is set.
        """
        ...
