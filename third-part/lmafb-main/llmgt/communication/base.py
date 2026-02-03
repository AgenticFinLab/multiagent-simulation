"""
This module provides message structures and protocol interfaces for encoding/decoding business messages
into wire-level packages.
"""

from datetime import datetime
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Protocol,
    runtime_checkable,
    Type,
    Optional,
    Union,
)


@dataclass
class M2IMessage:
    """
    The message base: Market -> Investor.
    """

    # Market ID of the message
    market_id: str
    # Investor ID to be sent (None for broadcast)
    investor_id: Optional[str] = None
    # Decision made by the market based on the current information
    decision_content: Any = None
    # Market rule that the investor should follow
    rule: str = ""
    # Additional information
    additions: Dict[str, Any] = field(default_factory=dict)
    # Time for creating the message
    time_stamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class I2MMessage:
    """
    The message base: Investor -> Market.

    Represents a message sent from an Investor entity to a Market entity.
    This message typically contains investor decisions, responses to market
    rules, and additional information relevant to market operations.
    """

    # Send by which investor
    investor_id: str
    market_id: str
    # Decision made by the investor
    decision_content: Any = None
    # Additional information
    additions: Dict[str, Any] = field(default_factory=dict)
    # Time for creating the message
    time_stamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProtocolOutbound:
    """
    The protocol-level outbound (wire/courier), which is an intermediate carrier used by the protocol/transport layer.

    This class represents the wire-format message that is actually transmitted
    over the network or communication channel. It encapsulates the business
    message with routing information and protocol metadata.
    """

    # Routing/meta info, e.g. "market::<market_id> -> investor::<investor_id>
    head: str
    # data is a JSON-formatted string.
    data: str
    # Protocol meta info, e.g. "codec=json;checksum=<hex>"
    tail: str


@runtime_checkable
class BaseCommProtocol(Protocol):
    """
    The common knobs shared by protocols.

    This protocol defines the interface that all communication protocols must implement
    to handle encoding and decoding of business messages. It provides a standardized
    way to convert between high-level business messages (I2MMessage, M2IMessage) and
    low-level protocol packages (ProtocolOutbound) suitable for network transmission.
    """

    message_type: Type[Any]
    protocol_config: Dict[str, Any]

    @abstractmethod
    def encode(
        self, messages: Iterable[Union[I2MMessage, M2IMessage]]
    ) -> List[ProtocolOutbound]:
        """
        Encode one or more investor business messages into protocol-level outbound packages.

        This method takes high-level business messages and converts them into wire-format
        packages suitable for transmission. It handles serialization, routing information
        generation, and protocol metadata attachment.
        """
        raise NotImplementedError

    @abstractmethod
    def decode(
        self, outbounds: Iterable[ProtocolOutbound]
    ) -> List[Union[I2MMessage, M2IMessage]]:
        """
        Decode protocol-level outbound packages into business messages.

        This method takes wire-format packages received from the network and converts
        them back into high-level business messages. It handles deserialization,
        routing information parsing, and protocol metadata validation.
        """
        raise NotImplementedError
