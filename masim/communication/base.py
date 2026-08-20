"""Base Communication module for the Multi-Agent Simulation (MASim) framework.

This module owns the wire-layer types (SimPacket, Message + enums) and the
CommunicationChannel abstract base class. For concrete implementations, see
`general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Enums:
    MessageType          - OBSERVATION, ACTION, COORDINATION, PEER, SYSTEM, BROADCAST
    MessagePriority      - LOW, NORMAL, HIGH, CRITICAL

Dataclasses:
    Message              - Routed message: sender_id, recipient_id, payload
    SimPacket            - Channel wire envelope: encoded Message + transmission metadata

Abstract Classes:
    CommunicationChannel - Channel base class: encode, decode, dispatch

================================================================================
                         DESIGN PHILOSOPHY
================================================================================

Three-layer message model (definitions live with the wire layer that carries them):
    Info      (player/base.py)         - Player-layer content: pure payload, no routing
    Message   (this file)              - Routed message: adds sender_id / recipient_id
    SimPacket (this file)              - Channel wire envelope: encoded Message on wire

CommunicationChannel responsibility: SimPacket ONLY.
    encode_message(Message) → SimPacket   [routed → wire]
    decode_message(SimPacket) → Message   [wire → routed]

Building a Message from an Info unit is handled by build_message_from_info()
in `masim/communication/general.py`, called by the Simulator in phase_dispatch.

Dependency direction (correct after layer-inversion fix):
    communication/base.py  → defines Message + enums (this file, no upward imports)
    proxy/*                → CONSUMES Message from communication.base
    simulator/*            → CONSUMES Message from communication.base

================================================================================
                    COMMUNICATION CHANNEL FLOW
================================================================================

    Simulator
        │
        │  1. collect_outbound_messages() from all Personas
        │  2. build_message_from_info(Info) → Message   [communication helper]
        │
        ▼
    CommunicationChannel.encode_and_deliver(messages, handles)
        │
        ├── 3. encode(Message) → SimPacket  [wire format]
        │
        ├── 4. record(SimPacket) for persistence
        │
        └── 5. decode(SimPacket) → Message, send via actor_handle.receive_message.remote()
        │
        ▼
    Target Persona receives Message
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

import numpy as np

from lmbase.utils.tools import BlockBasedStoreManager


# =============================================================================
# Message-layer types (owned by communication layer)
# =============================================================================


PayloadType = Union[Dict[str, Any], np.ndarray, bytes, List[Any]]


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


@dataclass
class Message:
    """
    Routed message on the communication layer.

    Built by the Simulator (via build_message_from_info) from an Info unit;
    adds routing metadata (sender_id, recipient_id, timestamp, priority) so
    the Channel can encode it to a SimPacket for wire transmission.

    Flow:
        Info (player layer)
          → Message (routed, built by build_message_from_info)
          → SimPacket (channel wire, encoded by CommunicationChannel)
          → decode → Message (restored)
          → handle_incoming() → Info (player layer, routing stripped)

    Attributes:
        message_type: Category of message
        sender_id:    ID of the sending component
        payload:      Message content (must be serializable)
        recipient_id: Target recipient (None for broadcast)
        timestamp:    ISO format timestamp
        priority:     Message delivery priority
        extras:       Additional context
    """

    message_type: MessageType
    sender_id: str
    payload: PayloadType
    recipient_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: MessagePriority = MessagePriority.NORMAL
    extras: Dict[str, Any] = field(default_factory=dict)

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        payload_data = self.payload
        if isinstance(self.payload, np.ndarray):
            payload_data = self.payload.tolist()
        return {
            "message_type": self.message_type.name,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": payload_data,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
            "extras": self.extras,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create Message from dictionary."""
        return cls(
            message_type=MessageType[data["message_type"]],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            priority=MessagePriority(data["priority"]),
            extras=data["extras"],
        )


# =============================================================================
# SimPacket: Channel Wire Envelope
# =============================================================================


@dataclass
class SimPacket:
    """
    Channel-layer wire envelope — the encoded form of a Message for transmission.

    CommunicationChannel encodes Message → SimPacket before sending,
    and decodes SimPacket → Message on receipt.

    Attributes:
        encoded:    Serialized message content (JSON string)
        sender_id:  Sender ID (for routing without full decode)
        recipient_id: Recipient ID (for routing without full decode)
        timestamp:  Encoding timestamp (ISO format)
    """

    encoded: str
    sender_id: str
    recipient_id: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# Communication Channel (Abstract Base Class)
# =============================================================================


class CommunicationChannel(ABC):
    """
    Abstract base class for communication channels.

    A CommunicationChannel is the wire transport layer that the Simulator
    uses to transmit messages between Personas. It is responsible for:

    1. **Encoding**: Convert proxy-layer Message → SimPacket (wire format)
    2. **Recording**: Persist SimPackets for debugging/replay
    3. **Decoding**: Convert SimPacket → proxy-layer Message
    4. **Dispatching**: Send Messages to target actors via Ray

    NOTE: Building a Message from an Info unit is NOT this class's concern.
    That is done by build_message_from_info() in proxy/general.py.

    Lifecycle:
        1. Simulator creates CommunicationChannel with config
        2. During each round, Simulator calls channel.encode_and_deliver(messages, handles)
        4. On simulation end, Simulator calls channel.shutdown()

    Subclasses must implement:
        - encode_message(): Message → SimPacket
        - decode_message(): SimPacket → Message
        - encode_and_deliver(): Full send pipeline
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
        # Whether to persist encoded messages to disk.
        # Set false for large-scale runs (N > ~100 players) to avoid high write volume.
        self.record_messages: bool = config["record_messages"]

        # Initialize message store
        os.makedirs(self.storage_path, exist_ok=True)
        self.message_store = BlockBasedStoreManager(
            folder=self.storage_path,
            file_format="json",
            block_size=config["message_block_size"],
        )

    # =========================================================================
    #                    ABSTRACT METHODS (Must implement)
    # =========================================================================

    @abstractmethod
    def encode_message(self, message: "Message") -> "SimPacket":
        """
        Encode proxy-layer Message to SimPacket (wire envelope).

        Args:
            message: Proxy-layer Message to encode

        Returns:
            SimPacket containing serialized content + routing metadata
        """
        raise NotImplementedError

    @abstractmethod
    def decode_message(self, packet: "SimPacket") -> "Message":
        """
        Decode SimPacket back to proxy-layer Message.

        Args:
            packet: SimPacket from transmission

        Returns:
            Reconstructed Message object
        """
        raise NotImplementedError

    @abstractmethod
    def encode_and_deliver(
        self,
        messages: List["Message"],
        handles: Dict[str, Any],
    ) -> List[Any]:
        """
        Encode, record, and deliver messages to target actors.

        This is the main entry point called by Simulator. Implementations
        should:
        1. encode_message(Message) → SimPacket  [wire format]
        2. record_encoded_message(SimPacket) → persist to storage
        3. decode_message(SimPacket) → Message  [proxy layer restored]
        4. Send decoded Message to target actor via Ray remote call

        Args:
            messages: List of proxy-layer Message objects to send
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
