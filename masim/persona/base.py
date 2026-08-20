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
from typing import Any, Dict, List, Optional, Tuple, Type, TYPE_CHECKING

import ray

from masim.utils.topology import TopologyGraph

if TYPE_CHECKING:
    from masim.proxy.general import (
        SendReceiveProxy,
        StorageProxy,
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
        self.message_proxy: Optional["SendReceiveProxy"] = None
        self.storage: Optional["StorageProxy"] = None
        self.monitoring: Optional["MonitoringProxy"] = None

        # Lifecycle flag
        self.is_initialized: bool = False

        # Operate timing
        self.operate_start_time: Optional[float] = None

        # Topology — stored as pre-computed local slice (targets/senders lists),
        # not as a full TopologyGraph. Populated by set_topology() from the Simulator.
        # The full graph lives only in the Simulator; actors hold only their local slice.
        self.topology: Optional[TopologyGraph] = (
            None  # retained for type-checking compat
        )
        self._topology_initialized: bool = False
        self._topology_targets: List[str] = []  # player IDs this actor can send to
        self._topology_senders: List[str] = []  # player IDs that can send to this actor

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
    ) -> Tuple["TurnResult", List[Dict[str, Any]]]:
        """
        Execute the Player's turn operation.

        Args:
            round_num: Current simulation round number
            **kwargs: Additional parameters (e.g., level)

        Returns:
            Tuple of (TurnResult, pending_infos) where pending_infos is a list
            of dicts with keys: info, sender_id, target_ids, round_num.
            Bundling both values in a single return keeps message dispatch to a
            single IPC round-trip per persona per turn.
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
    def set_topology(self, local_slice: Optional[Dict[str, Any]]) -> None:
        """Set the local topology slice for message routing."""
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
    #                    EXPECTED SENDERS SETUP
    # =========================================================================

    @abstractmethod
    def setup_expected_senders(self) -> None:
        """
        Derive expected_senders from topology and set on Player.

        Called during initialization after topology is set.
        """
        ...
