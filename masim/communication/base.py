"""Base Communication module for the Multi-Agent Simulation (MASim) framework.

This module provides message formats and the CommunicationChannel base class.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Type Aliases:
    PayloadType          - Union[Dict, np.ndarray, bytes, List]

Enums:
    MessageType          - OBSERVATION, ACTION, COORDINATION, PEER, SYSTEM, BROADCAST
    MessagePriority      - LOW, NORMAL, HIGH, CRITICAL

Dataclasses:
    Message              - Standard message format: type, sender_id, payload, recipient_id

Abstract Classes:
    CommunicationChannel - Channel base class: dispatch, shutdown

================================================================================
                         DESIGN PHILOSOPHY
================================================================================

- All cross-component communication uses standard Message format
- CommunicationChannel is the central abstraction for message transmission
- Concrete implementations (JsonProtocol, etc.) belong in general.py

================================================================================
                    COMMUNICATION CHANNEL FLOW
================================================================================

    Simulator
        │
        │  1. collect_outbound_messages() from all Personas
        │
        ▼
    CommunicationChannel.encode_and_deliver(messages, handles)
        │
        ├── 2. encode(message) via Protocol
        │
        ├── 3. record(message) for persistence
        │
        └── 4. send to target via actor_handle.receive_message.remote()
        │
        ▼
    Target Persona receives message

================================================================================
                          MESSAGE TYPES
================================================================================

    OBSERVATION  - Environment → Players (round state notification)
    ACTION       - Player → Environment (behavioral output)
    COORDINATION - Player → Players (coordination decision broadcast)
    PEER         - Player ↔ Player (direct peer communication)
    SYSTEM       - Framework internal control messages
    BROADCAST    - One-to-many messages
"""

import os
import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import numpy as np

from lmbase.utils.tools import BlockBasedStoreManager


# =============================================================================
# Type Aliases
# =============================================================================

PayloadType = Union[Dict[str, Any], np.ndarray, bytes, List[Any]]


# =============================================================================
# Message Types
# =============================================================================


class MessageType(Enum):
    """Types of messages in the framework."""

    # Environment -> Players
    OBSERVATION = auto()
    # Player -> Environment
    ACTION = auto()
    # Player -> Players (coordination)
    COORDINATION = auto()
    # Player <-> Player
    PEER = auto()
    # Framework internal
    SYSTEM = auto()
    # One-to-many
    BROADCAST = auto()


class MessagePriority(Enum):
    """Priority levels for message delivery."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# =============================================================================
# Core Message Dataclass
# =============================================================================


@dataclass
class Message:
    """
    Standard message format for all cross-component communication.

    All messages transmitted between framework components must use this format
    to ensure serialization compatibility and consistent routing.

    Attributes:
        message_type: Category of message
        sender_id: ID of the sending component
        payload: Message content (must be serializable)
        message_id: Unique identifier
        recipient_id: Target recipient (None for broadcast)
        timestamp: ISO format timestamp
        correlation_id: ID linking related messages
        priority: Message delivery priority
        metadata: Routing and protocol metadata
    """

    message_type: MessageType
    sender_id: str
    payload: PayloadType
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recipient_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._validate_payload()

    def _validate_payload(self) -> None:
        """Ensure payload is serialization-friendly."""
        if self.payload is None:
            return
        if isinstance(self.payload, (dict, list, np.ndarray, bytes)):
            return
        raise TypeError(
            f"Message payload must be dict, list, numpy.ndarray, or bytes. "
            f"Got: {type(self.payload).__name__}"
        )

    def is_broadcast(self) -> bool:
        """Check if this message is a broadcast."""
        return self.recipient_id is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        payload_data = self.payload
        if isinstance(self.payload, np.ndarray):
            payload_data = self.payload.tolist()
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.name,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": payload_data,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "priority": self.priority.value,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create Message from dictionary."""
        if "message_type" not in data:
            raise KeyError("Message data must have 'message_type' key")
        if "sender_id" not in data:
            raise KeyError("Message data must have 'sender_id' key")
        return cls(
            message_id=(
                data["message_id"] if "message_id" in data else str(uuid.uuid4())
            ),
            message_type=MessageType[data["message_type"]],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"] if "recipient_id" in data else None,
            payload=data["payload"] if "payload" in data else {},
            timestamp=(
                data["timestamp"] if "timestamp" in data else datetime.now().isoformat()
            ),
            correlation_id=data["correlation_id"] if "correlation_id" in data else None,
            priority=(
                MessagePriority(data["priority"])
                if "priority" in data
                else MessagePriority.NORMAL
            ),
            metadata=data["metadata"] if "metadata" in data else {},
        )


# =============================================================================
# Communication Channel (Abstract Base Class)
# =============================================================================


class CommunicationChannel(ABC):
    """
    Abstract base class for communication channels.

    A CommunicationChannel is the central message bus that the Simulator
    uses to transmit messages between Personas. It is responsible for:

    1. **Building**: Create Message objects from various sources
    2. **Encoding**: Convert Message objects to wire format
    3. **Recording**: Persist sent messages for debugging/replay
    4. **Dispatching**: Send messages to target actors via Ray

    Lifecycle:
        1. Simulator creates CommunicationChannel with config
        2. During each round, Simulator collects outbound messages from Personas
        3. Simulator calls channel.encode_and_deliver(messages, handles)
        4. On simulation end, Simulator calls channel.shutdown()

    Subclasses must implement:
        - dispatch(): Send messages to target actors
        - shutdown(): Release resources and flush pending data

    Config keys (passed to __init__):
        - storage_path: Directory for message persistence (required)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communication channel.

        Args:
            config: Configuration dict with channel settings
        """
        self.config = config
        self.storage_path = config["storage_path"]

        # Initialize message store
        os.makedirs(self.storage_path, exist_ok=True)
        self.message_store = BlockBasedStoreManager(
            folder=self.storage_path, file_format="json", block_size=500
        )

    # =========================================================================
    #                    MESSAGE BUILDING
    # =========================================================================

    def build_message_from_outbound(
        self,
        outbound: Any,
        sender_id: str,
        target_id: str,
        round_num: int = 0,
    ) -> Message:
        """
        Convert Player's Outbound to wire-ready Message.

        Args:
            outbound: The Outbound object containing payload, content_type, extras
            sender_id: The sender's identity
            target_id: The target's identity
            round_num: Current simulation round

        Returns:
            A fully-configured Message ready for transmission
        """
        payload = {
            "content": outbound.payload,
            "content_type": getattr(outbound, "content_type", None),
            "extras": getattr(outbound, "extras", {}),
        }
        return Message(
            message_type=MessageType.PEER,
            sender_id=sender_id,
            recipient_id=target_id,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            metadata={"round_num": round_num},
        )

    # =========================================================================
    #                    ABSTRACT METHODS (Must implement)
    # =========================================================================

    @abstractmethod
    def encode_message(self, message: Message) -> str:
        """
        Encode Message to wire format (JSON string).

        Args:
            message: Message object to encode

        Returns:
            JSON string representation for transmission
        """
        raise NotImplementedError

    @abstractmethod
    def decode_message(self, data: str) -> Message:
        """
        Decode wire format (JSON string) back to Message.

        Args:
            data: JSON string from transmission

        Returns:
            Reconstructed Message object
        """
        raise NotImplementedError

    @abstractmethod
    def encode_and_deliver(
        self,
        messages: List[Message],
        handles: Dict[str, Any],
    ) -> List[Any]:
        """
        Encode, record, decode, and deliver messages to target actors.

        This is the main entry point called by Simulator. Implementations
        should:
        1. encode_message() → JSON string (wire format)
        2. Record the encoded message to storage
        3. decode_message() → reconstruct Message from wire format
        4. Send decoded Message to target actor via Ray remote call

        Args:
            messages: List of Message objects to send
            handles: Dict mapping recipient_id -> Ray actor handle

        Returns:
            List of Ray ObjectRefs for delivery tracking
        """
        raise NotImplementedError

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the channel and release resources.

        Called by Simulator when simulation ends. Implementations should:
        1. Flush any pending records to disk
        2. Close any open connections
        3. Clear internal state
        """
        raise NotImplementedError
