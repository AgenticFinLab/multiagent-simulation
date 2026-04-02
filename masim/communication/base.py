"""Base Communication module for the Multi-Agent Simulation (MASim) framework.

This module provides the channel wire type and the CommunicationChannel base class.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Dataclasses:
    SimPacket            - Channel wire envelope: encoded Message + transmission metadata

Abstract Classes:
    CommunicationChannel - Channel base class: encode, decode, dispatch

================================================================================
                         DESIGN PHILOSOPHY
================================================================================

Three-layer message model (types defined close to their layer):
    Info      (player/base.py)  - Player-layer content: pure payload, no routing
    Message   (proxy/base.py)   - Proxy-layer: adds sender_id, recipient_id, routing
    SimPacket (here)            - Channel wire envelope: encoded Message for transmission

CommunicationChannel responsibility: SimPacket ONLY.
    encode_message(Message) → SimPacket   [bridges proxy → wire]
    decode_message(SimPacket) → Message   [bridges wire → proxy]

Building a Message from an Info unit is NOT a Channel concern —
it is handled by build_message_from_info() in proxy/general.py,
called by the Simulator in phase_dispatch.

================================================================================
                    COMMUNICATION CHANNEL FLOW
================================================================================

    Simulator
        │
        │  1. collect_outbound_messages() from all Personas
        │  2. build_message_from_info(Info) → Message  [proxy helper]
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
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from lmbase.utils.tools import BlockBasedStoreManager

if TYPE_CHECKING:
    from masim.proxy.base import Message


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
