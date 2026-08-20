"""MASim Communication Module.

Owns the wire-layer types (SimPacket) AND the routed message types
(Message, MessageType, MessagePriority). Communication is the natural home
for these — proxy consumes them, simulator consumes them, but the wire layer
defines them.

base.py exports:
    - MessageType, MessagePriority (enums)
    - Message (routed message dataclass)
    - PayloadType (alias for legal Message.payload types)
    - SimPacket (channel wire envelope dataclass)
    - CommunicationChannel (abstract base class)

general.py exports:
    - GeneralCommunicationChannel (concrete implementation)
    - build_message_from_info (Info → Message adapter, called by Simulator)

Layer inversion note (fixed): previously Message lived in masim/proxy/base.py
and the wire layer imported UP from proxy. Communication now owns those types
directly, and proxy imports DOWN from communication.
"""

from masim.communication.base import (
    # Routed message types (canonical home)
    Message,
    MessageType,
    MessagePriority,
    PayloadType,
    # Channel wire type
    SimPacket,
    # Abstract base class
    CommunicationChannel,
)

from masim.communication.general import (
    # Concrete channel implementation
    GeneralCommunicationChannel,
    # Info → Message adapter (called by Simulator in phase_dispatch)
    build_message_from_info,
)

__all__ = [
    # Message-layer types
    "Message",
    "MessageType",
    "MessagePriority",
    "PayloadType",
    # base.py - Wire type
    "SimPacket",
    "CommunicationChannel",
    # general.py - Channel + helper
    "GeneralCommunicationChannel",
    "build_message_from_info",
]
