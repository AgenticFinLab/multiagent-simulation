"""MASim Communication Module.

Provides message types and channel for cross-component communication.

base.py exports:
    - PayloadType, MessageType, MessagePriority (types/enums)
    - Message (core dataclass)
    - CommunicationChannel (abstract base class with message building methods)

general.py exports:
    - GeneralCommunicationChannel (concrete implementation)
"""

from masim.communication.base import (
    # Type aliases
    PayloadType,
    # Enums
    MessageType,
    MessagePriority,
    # Core dataclass
    Message,
    # Abstract base class
    CommunicationChannel,
)

from masim.communication.general import (
    # Concrete channel implementation
    GeneralCommunicationChannel,
)

__all__ = [
    # base.py - Types
    "PayloadType",
    "MessageType",
    "MessagePriority",
    "Message",
    "CommunicationChannel",
    # general.py - Channel
    "GeneralCommunicationChannel",
]
