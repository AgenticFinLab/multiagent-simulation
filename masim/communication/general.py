"""General Communication implementation for the MASim framework.

This module provides a simple, intuitive implementation of CommunicationChannel:
- GeneralCommunicationChannel: JSON-based message dispatch and recording

For abstract base class and message formats, see `base.py`.
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from masim.communication.base import CommunicationChannel, Message


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

    def encode_message(self, message: Message) -> str:
        """
        Encode Message to wire format (JSON string).

        Args:
            message: Message object to encode

        Returns:
            JSON string representation for transmission
        """
        return json.dumps(message.to_dict(), default=str)

    def decode_message(self, data: str) -> Message:
        """
        Decode wire format (JSON string) back to Message.

        Args:
            data: JSON string from transmission

        Returns:
            Reconstructed Message object
        """
        message_dict = json.loads(data)
        return Message.from_dict(message_dict)

    def record_encoded_message(self, encoded_message: str) -> None:
        """
        Record an encoded message with size and timestamp.

        Args:
            encoded_message: JSON string from encode_message()
        """
        timestamp = datetime.now()
        record = {
            "timestamp": timestamp.isoformat(),
            "size_bytes": len(encoded_message.encode("utf-8")),
            "encoded": encoded_message,
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
                # 1. Encode to wire format
                encoded = self.encode_message(message)

                # 2. Record the encoded message
                self.record_encoded_message(encoded)

                # 3. Decode from wire format (simulates receiving end)
                decoded_message = self.decode_message(encoded)

                # 4. Deliver to target
                target_handle = handles[recipient_id]
                ref = target_handle.receive_message.remote(decoded_message)
                refs.append(ref)

        return refs

    def shutdown(self) -> None:
        """Shutdown the channel and release resources."""
