"""
MASim Communication Module.

Provides message types, protocols, and routing for cross-component communication.
"""

from masim.communication.base import (
    # Type aliases
    PayloadType,
    # Enums
    MessageType,
    MessagePriority,
    # Core types
    Message,
    ProtocolOutbound,
    RouteInfo,
    # Protocols
    BaseProtocol,
    JsonProtocol,
    # Router
    MessageRouter,
    # Message builders
    build_observation_message,
    build_action_message,
    build_coordination_message,
    build_peer_message,
)

__all__ = [
    "PayloadType",
    "MessageType",
    "MessagePriority",
    "Message",
    "ProtocolOutbound",
    "RouteInfo",
    "BaseProtocol",
    "JsonProtocol",
    "MessageRouter",
    "build_observation_message",
    "build_action_message",
    "build_coordination_message",
    "build_peer_message",
]
