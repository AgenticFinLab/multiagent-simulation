"""General Communication implementation for the MASim framework.

This module provides a simple, intuitive implementation of CommunicationChannel:
- GeneralCommunicationChannel: JSON-based SimPacket encoding, recording, and dispatch
- build_message_from_info():   Info (player layer) → Message (communication layer)

For abstract base class + Message/enum definitions, see `masim/communication/base.py`.
The communication layer OWNS Message and its enums; proxy consumes them.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING

from masim.communication.base import (
    CommunicationChannel,
    Message,
    MessageType,
    SimPacket,
)

if TYPE_CHECKING:
    # Info is defined in the player layer. TYPE_CHECKING avoids a runtime
    # circular import while still giving IDEs / mypy the correct hint.
    from masim.player.base import Info


# =============================================================================
#                     BUILD MESSAGE HELPER
# =============================================================================


def build_message_from_info(
    info: "Info",
    sender_id: str,
    target_id: str,
    round_num: int = 0,
) -> Message:
    """
    Convert a player-layer Info unit into a routed communication-layer Message.

    This is the ONLY place where Info → Message conversion happens.
    Called by Simulator in phase_dispatch after collecting outbound Info units.

    The Info payload is wrapped in a content envelope so the routed Message
    carries structured metadata alongside the raw content::

        payload = {"content": info.payload,
                   "content_type": info.content_type,
                   "extras": info.extras}

    On the receive side, SendReceiveProxy.handle_incoming() unpacks this envelope
    back into an Info unit for the target player.

    Args:
        info:       The Info unit produced by the sending Player
        sender_id:  Identity of the sending Persona
        target_id:  Identity of the receiving Persona
        round_num:  Current simulation round (stored in extras)

    Returns:
        Message ready for CommunicationChannel.encode_and_deliver()
    """
    payload = {
        "content": info.payload,
        "content_type": info.content_type,
        "extras": info.extras,
    }
    return Message(
        message_type=MessageType.PEER,
        sender_id=sender_id,
        recipient_id=target_id,
        payload=payload,
        timestamp=datetime.now().isoformat(),
        extras={"round_num": round_num},
    )


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
        2. record_encoded_message() → persist to storage (skipped if record_messages=False)
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
            # Fail-loud: silent drops here would let messages disappear
            # without any downstream indication, and every metric that
            # depends on message counts would silently drift.
            if not recipient_id:
                raise ValueError(
                    "encode_and_deliver: message has empty recipient_id "
                    f"(sender_id={message.sender_id!r}, payload_type="
                    f"{getattr(message, 'payload', None)!r}). Every message "
                    "MUST target a concrete recipient."
                )
            if recipient_id not in handles:
                raise KeyError(
                    f"encode_and_deliver: recipient_id={recipient_id!r} not "
                    f"in registered actor handles (known="
                    f"{sorted(handles.keys())}). Silent drop would erase "
                    "the message with no downstream indication; fix the "
                    "routing / registration bug at the caller instead."
                )
            # 1. Encode Message → SimPacket (wire envelope)
            packet = self.encode_message(message)

            # 2. Record the SimPacket (skipped at scale when record_messages=False)
            if self.record_messages:
                self.record_encoded_message(packet)

            # 3. Decode SimPacket → Message (proxy layer restored)
            decoded_message = self.decode_message(packet)

            # 4. Deliver to target Persona
            target_handle = handles[recipient_id]
            ref = target_handle.receive_message.remote(decoded_message)
            refs.append(ref)

        return refs

    def shutdown(self) -> None:
        """Shutdown the channel: flush message store so trailing blocks are persisted.

        Fixes H7: previously this was a no-op, so if the driver terminated
        without flushing message_store, the last unflushed block(s) would be
        lost. BlockBasedStoreManager writes append-only blocks and flushes when
        a block fills; on shutdown we force one final flush.
        """
        store = getattr(self, "message_store", None)
        if store is None:
            return
        for method_name in ("flush", "close", "finalize"):
            fn = getattr(store, method_name, None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    # Store shutdown failures should not mask upstream shutdown
                    # signals; log and continue. The rest of the finally block
                    # in Simulator.shutdown still needs to run.
                    import logging
                    logging.getLogger(__name__).exception(
                        "GeneralCommunicationChannel.shutdown: %s() raised",
                        method_name,
                    )
                break
