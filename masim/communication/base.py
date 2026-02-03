"""
Base Communication module for the Multi-Agent Simulation (MASim) framework.

This module defines:
- Message types and formats for cross-component communication
- Communication protocols for encoding/decoding messages
- Message routing and addressing abstractions

Design Philosophy:
- All cross-component communication uses standard Message format
- Protocol layer handles serialization (Arrow/JSON compatible)
- Routing is decoupled from message content semantics
- Ray-native transport with zero-copy optimization support
"""

import uuid
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Iterable

import numpy as np


# =============================================================================
# Type Aliases
# =============================================================================

PayloadType = Union[Dict[str, Any], np.ndarray, bytes, List[Any]]


# =============================================================================
# Message Types
# =============================================================================


class MessageType(Enum):
    """Types of messages in the framework."""

    OBSERVATION = auto()  # Environment -> Players
    ACTION = auto()  # Player -> Environment/Conductor
    COORDINATION = auto()  # Conductor -> Players
    PEER = auto()  # Player <-> Player
    SYSTEM = auto()  # Framework internal
    BROADCAST = auto()  # One-to-many


class MessagePriority(Enum):
    """Priority levels for message delivery."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


# =============================================================================
# Core Message Classes
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
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            message_type=MessageType[data["message_type"]],
            sender_id=data["sender_id"],
            recipient_id=data.get("recipient_id"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            correlation_id=data.get("correlation_id"),
            priority=MessagePriority(data.get("priority", 1)),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProtocolOutbound:
    """
    Protocol-level outbound package for wire transmission.

    This is the intermediate carrier used by the protocol/transport layer.
    It encapsulates the business message with routing and protocol metadata.

    Attributes:
        head: Routing/meta info (e.g., "player::id -> conductor::id")
        data: Serialized message data (JSON string)
        tail: Protocol meta info (e.g., "codec=json;checksum=<hex>")
    """

    head: str
    data: str
    tail: str = ""


# =============================================================================
# Protocol Interfaces
# =============================================================================


class BaseProtocol(ABC):
    """
    Abstract base class for communication protocols.

    Protocols handle encoding business messages into wire-format packages
    and decoding them back. This abstraction allows different serialization
    strategies (JSON, Arrow, Protobuf) to be used interchangeably.
    """

    @abstractmethod
    def encode(self, messages: Iterable[Message]) -> List[ProtocolOutbound]:
        """
        Encode business messages into protocol-level outbound packages.

        Args:
            messages: Iterable of Message objects

        Returns:
            List of ProtocolOutbound packages for transmission
        """
        raise NotImplementedError

    @abstractmethod
    def decode(self, outbounds: Iterable[ProtocolOutbound]) -> List[Message]:
        """
        Decode protocol-level packages back into business messages.

        Args:
            outbounds: Iterable of ProtocolOutbound packages

        Returns:
            List of decoded Message objects
        """
        raise NotImplementedError


class JsonProtocol(BaseProtocol):
    """
    JSON-based protocol implementation.

    Simple and human-readable, suitable for debugging and
    interoperability with external systems.
    """

    def __init__(self, pretty: bool = False):
        import json

        self._json = json
        self._pretty = pretty

    def encode(self, messages: Iterable[Message]) -> List[ProtocolOutbound]:
        outbounds = []
        for msg in messages:
            head = f"{msg.sender_id} -> {msg.recipient_id or 'broadcast'}"

            indent = 2 if self._pretty else None
            data = self._json.dumps(msg.to_dict(), indent=indent, default=str)

            tail = f"codec=json;type={msg.message_type.name}"
            outbounds.append(ProtocolOutbound(head=head, data=data, tail=tail))
        return outbounds

    def decode(self, outbounds: Iterable[ProtocolOutbound]) -> List[Message]:
        messages = []
        for outbound in outbounds:
            data = self._json.loads(outbound.data)
            msg = Message.from_dict(data)
            messages.append(msg)
        return messages


# =============================================================================
# Message Routing
# =============================================================================


@dataclass
class RouteInfo:
    """
    Routing information for message delivery.

    Attributes:
        source_id: Sender component ID
        target_id: Recipient component ID (None for broadcast)
        scope: Routing scope (e.g., "all", "group:sensors")
        hops: Number of routing hops (for distributed tracing)
    """

    source_id: str
    target_id: Optional[str] = None
    scope: Optional[str] = None
    hops: int = 0

    def is_broadcast(self) -> bool:
        return self.target_id is None

    def matches_scope(self, entity_tags: List[str]) -> bool:
        """Check if entity matches the routing scope."""
        if self.scope is None or self.scope == "all":
            return True
        if self.scope.startswith("group:"):
            group_tag = self.scope[6:]
            return group_tag in entity_tags
        if self.scope.startswith("entity:"):
            entity_id = self.scope[7:]
            return entity_id == self.target_id
        return True


class MessageRouter:
    """
    Message routing logic for the framework.

    Handles routing decisions based on message metadata and
    entity registrations. Works with Ray actor references for delivery.
    """

    def __init__(self):
        self._entity_registry: Dict[str, Dict[str, Any]] = {}
        self._group_registry: Dict[str, List[str]] = {}

    def register_entity(
        self, entity_id: str, tags: List[str] = None, metadata: Dict[str, Any] = None
    ) -> None:
        """Register an entity for message routing."""
        self._entity_registry[entity_id] = {
            "tags": tags or [],
            "metadata": metadata or {},
        }
        # Update group registry
        for tag in tags or []:
            if tag not in self._group_registry:
                self._group_registry[tag] = []
            if entity_id not in self._group_registry[tag]:
                self._group_registry[tag].append(entity_id)

    def unregister_entity(self, entity_id: str) -> None:
        """Unregister an entity from routing."""
        info = self._entity_registry.pop(entity_id, None)
        if info:
            for tag in info.get("tags", []):
                if tag in self._group_registry:
                    self._group_registry[tag] = [
                        eid for eid in self._group_registry[tag] if eid != entity_id
                    ]

    def resolve_recipients(self, route_info: RouteInfo) -> List[str]:
        """
        Resolve the list of recipient IDs for a route.

        Args:
            route_info: Routing information

        Returns:
            List of entity IDs that should receive the message
        """
        if route_info.target_id:
            # Direct routing
            return (
                [route_info.target_id]
                if route_info.target_id in self._entity_registry
                else []
            )

        # Broadcast/scope-based routing
        recipients = []
        for entity_id, info in self._entity_registry.items():
            if route_info.matches_scope(info.get("tags", [])):
                recipients.append(entity_id)

        return recipients

    def get_entities_by_group(self, group_tag: str) -> List[str]:
        """Get all entity IDs in a group."""
        return self._group_registry.get(group_tag, []).copy()

    def get_all_entities(self) -> List[str]:
        """Get all registered entity IDs."""
        return list(self._entity_registry.keys())


# =============================================================================
# Message Builders (Convenience Functions)
# =============================================================================


def build_observation_message(
    source_id: str,
    observation_data: PayloadType,
    target_id: Optional[str] = None,
    step: Optional[int] = None,
) -> Message:
    """Build an Observation message."""
    return Message(
        message_type=MessageType.OBSERVATION,
        sender_id=source_id,
        recipient_id=target_id,
        payload=observation_data,
        metadata={"step": step} if step else {},
    )


def build_action_message(
    source_id: str,
    action_type: str,
    action_payload: PayloadType,
    target_id: Optional[str] = None,
) -> Message:
    """Build an Action message."""
    return Message(
        message_type=MessageType.ACTION,
        sender_id=source_id,
        recipient_id=target_id,
        payload={"action_type": action_type, "data": action_payload},
    )


def build_coordination_message(
    source_id: str,
    decision_type: str,
    parameters: Dict[str, Any],
    scope: str = "all",
    target_id: Optional[str] = None,
) -> Message:
    """Build a Coordination message."""
    return Message(
        message_type=MessageType.COORDINATION,
        sender_id=source_id,
        recipient_id=target_id,
        payload={
            "decision_type": decision_type,
            "parameters": parameters,
            "scope": scope,
        },
    )


def build_peer_message(
    source_id: str,
    target_id: str,
    content: PayloadType,
    correlation_id: Optional[str] = None,
) -> Message:
    """Build a Peer-to-peer message."""
    return Message(
        message_type=MessageType.PEER,
        sender_id=source_id,
        recipient_id=target_id,
        payload=content,
        correlation_id=correlation_id,
    )
