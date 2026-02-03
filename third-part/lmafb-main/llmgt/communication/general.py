"""
This module implements the GeneralCommunication class, providing basic communication
functionality using the base communication protocols.
"""

import json
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Type


from llmgt.communication.base import (
    BaseCommProtocol,
    ProtocolOutbound,
    I2MMessage,
    M2IMessage,
)


class GeneralI2MProtocol(BaseCommProtocol):
    """
    The definition of how to encode/decode business messages from an investor into a protocol-level outbound package
    and back.
    """

    message_type: Type[Any] = I2MMessage

    def __init__(self):
        self.protocol_config: Dict[str, Any] = {"codec": "json"}

    def encode(self, messages: Iterable[I2MMessage]) -> List[ProtocolOutbound]:
        """
        Encode one or more investor business messages into protocol-level outbound packages.
        """
        out: List[ProtocolOutbound] = []
        # Convert m (an M2IMessage object) to a dictionary for:
        # Packaging it into a structure like {"msg_type": "M2I", "payload": payload}
        # Then serialize it into a string and place it in ProtocolOutbound.data
        for m in messages:
            # payload = field dictionary converted from business message (M2IMessage/I2MMessage)
            payload = asdict(m)
            head = f"investor::{m.investor_id} -> market::{m.market_id}"
            data_str = json.dumps(
                {"msg_type": "I2M", "payload": payload}, separators=(",", ":")
            )
            tail = f"codec={self.protocol_config.get('codec', 'json')}"
            out.append(ProtocolOutbound(head=head, data=data_str, tail=tail))
        return out

    def decode(self, outbounds: Iterable[ProtocolOutbound]) -> List[I2MMessage]:
        """
        Decode ProtocolOutbounds into a list of I2MMessages.
        """
        msgs: List[I2MMessage] = []
        for outbound in outbounds:
            try:
                data = json.loads(outbound.data or "{}")
            except json.JSONDecodeError:
                continue
            if data.get("msg_type") != "I2M":
                continue
            payload = data.get("payload", {}) or {}
            msgs.append(I2MMessage(**payload))
        return msgs


class GeneralM2IProtocol(BaseCommProtocol):
    """
    This is the definition of how to encode/decode business messages from a market into protocol-level outbound packages
    and back.
    """

    message_type: Type[Any] = M2IMessage

    def __init__(self):
        self.protocol_config: Dict[str, Any] = {"codec": "json"}

    def encode(self, messages: Iterable[M2IMessage]) -> List[ProtocolOutbound]:
        """
        Encode market business messages into protocol outbounds using [Head]-[Data]-[Tail].
        """
        out: List[ProtocolOutbound] = []
        codec = self.protocol_config.get("codec", "json")
        for m in messages:
            payload = asdict(m)
            dst = m.investor_id or "broadcast"
            head = f"market::{m.market_id} -> investor::{dst}"
            data_str = json.dumps(
                {"msg_type": "M2I", "payload": payload}, separators=(",", ":")
            )
            tail = f"codec={codec}"
            out.append(ProtocolOutbound(head=head, data=data_str, tail=tail))
        return out

    def decode(self, outbounds: Iterable[ProtocolOutbound]) -> List[M2IMessage]:
        """
        Decode ProtocolOutbounds into a list of M2IMessages.
        """
        msgs: List[M2IMessage] = []
        for outbound_packet in outbounds:
            try:
                data = json.loads(outbound_packet.data or "{}")
            except json.JSONDecodeError:
                continue
            if data.get("msg_type") != "M2I":
                continue
            payload = data.get("payload", {}) or {}
            msgs.append(M2IMessage(**payload))
        return msgs
