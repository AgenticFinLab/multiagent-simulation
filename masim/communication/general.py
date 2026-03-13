"""General Communication implementation for the MASim framework.

This module provides a simple, intuitive implementation of CommunicationChannel:
- GeneralCommunicationChannel: JSON-based SimPacket encoding, recording, and dispatch

For abstract base class and SimPacket type, see `base.py`.
For Message and proxy-layer types, see `masim.proxy.base`.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from masim.communication.base import CommunicationChannel, SimPacket
from masim.proxy.base import Message


class GeneralCommunicationChannel(CommunicationChannel):
    """
    Concrete communication channel using JSON encoding.

    A simple and intuitive implementation of CommunicationChannel that:
    - Encodes messages as JSON for human-readability
    - Records sent messages using BlockBasedStoreManager
    - Dispatches messages to Ray actors

    Config keys:
        storage_path: Directory for message storage (required)
    """

    def encode_message(self, message: Message) -> SimPacket:
        """
        Encode Message to SimPacket (wire envelope).

        Args:
            message: Proxy-layer Message to encode

        Returns:
            SimPacket with JSON-encoded content and routing metadata
        """
        return SimPacket(
            encoded=json.dumps(message.to_dict(), default=str),
            sender_id=message.sender_id,
            recipient_id=message.recipient_id,
        )

    def decode_message(self, packet: SimPacket) -> Message:
        """
        Decode SimPacket back to proxy-layer Message.

        Args:
            packet: SimPacket from transmission

        Returns:
            Reconstructed Message object
        """
        message_dict = json.loads(packet.encoded)
        return Message.from_dict(message_dict)

    def record_encoded_message(self, packet: SimPacket) -> None:
        """
        Record a SimPacket with size and timestamp.

        Args:
            packet: SimPacket from encode_message()
        """
        timestamp = datetime.now()
        record = {
            "timestamp": timestamp.isoformat(),
            "size_bytes": len(packet.encoded.encode("utf-8")),
            "encoded": packet.encoded,
        }
        savename = f"msg_{timestamp.strftime('%m%d%H%M%S%f')}"
        self.message_store.save(savename=savename, data=record)

    def encode_and_deliver(
        self,
        messages: List[Message],
        handles: Dict[str, Any],
    ) -> List[Any]:
        """
        Encode, record, decode, and deliver messages to target Ray actors.

        Flow:
        1. encode_message() → JSON string (wire format)
        2. record_encoded_message() → persist to storage
        3. decode_message() → reconstruct Message from wire format
        4. Send decoded Message to target actor via Ray remote call

        This simulates a complete wire protocol cycle, validating
        that encode/decode produces equivalent Messages.

        Args:
            messages: List of Message objects to send
            handles: Dict mapping recipient_id -> Ray actor handle

        Returns:
            List of Ray ObjectRefs for delivery tracking
        """
        refs = []
        for message in messages:
            recipient_id = message.recipient_id
            if recipient_id and recipient_id in handles:
                # 1. Encode Message → SimPacket (wire envelope)
                packet = self.encode_message(message)

                # 2. Record the SimPacket
                self.record_encoded_message(packet)

                # 3. Decode SimPacket → Message (proxy layer restored)
                decoded_message = self.decode_message(packet)

                # 4. Deliver to target Persona
                target_handle = handles[recipient_id]
                ref = target_handle.receive_message.remote(decoded_message)
                refs.append(ref)

        return refs

    def shutdown(self) -> None:
        """Shutdown the channel and release resources."""
