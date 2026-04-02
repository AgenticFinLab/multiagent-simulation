"""MASim Communication Module.

Provides the channel wire type and channel for cross-component communication.

base.py exports:
    - SimPacket (channel wire envelope dataclass)
    - CommunicationChannel (abstract base class)

general.py exports:
    - GeneralCommunicationChannel (concrete implementation)

Note: Message, MessageType, MessagePriority are now in masim.proxy
      (proximity principle — they are proxy-layer types).
"""

from masim.communication.base import (
    # Channel wire type
    SimPacket,
    # Abstract base class
    CommunicationChannel,
)

from masim.communication.general import (
    # Concrete channel implementation
    GeneralCommunicationChannel,
)

__all__ = [
    # base.py - Wire type
    "SimPacket",
    "CommunicationChannel",
    # general.py - Channel
    "GeneralCommunicationChannel",
]
