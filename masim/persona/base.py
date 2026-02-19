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
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import ray

if TYPE_CHECKING:
    from masim.proxy.base import (
        CommunicationProxy,
        StorageProxy,
        ResourceProxy,
        ObservabilityProxy,
    )
    from masim.communication.base import Message
    from masim.player.base import TurnResult


# =============================================================================
#                          BASE PERSONA
# =============================================================================


class BasePersona(ABC):
    """
    Abstract base class for Persona - the interface Simulator uses.

    All methods that Simulator or other Personas call must be declared here.
    Concrete implementation is in general.py (PlayerPersona).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize base Persona with config dict."""
        self.config: Dict[str, Any] = config or {}

        # Proxy references (access directly: self.storage, self.observability, etc.)
        self.communication: Optional["CommunicationProxy"] = None
        self.storage: Optional["StorageProxy"] = None
        self.resource: Optional["ResourceProxy"] = None
        self.observability: Optional["ObservabilityProxy"] = None

        self.is_initialized: bool = False

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
        notification: Dict[str, Any],
        round_num: int,
        num_steps: int = 1,
    ) -> "TurnResult":
        """
        Execute the Player's turn operation.

        Args:
            notification: Notification dict for this round
            round_num: Current simulation round number
            num_steps: Number of steps to execute in this turn

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
    #                    MESSAGE POOL CONTROL
    # =========================================================================

    @abstractmethod
    def is_ready_to_proceed(self) -> bool:
        """Check if player can proceed (all expected messages received)."""
        ...

    @abstractmethod
    def set_expected_senders(self, senders: List[str]) -> None:
        """Set which senders this player expects messages from."""
        ...

    @abstractmethod
    def clear_message_pool(self) -> None:
        """Clear message inbox and reset expected senders."""
        ...
