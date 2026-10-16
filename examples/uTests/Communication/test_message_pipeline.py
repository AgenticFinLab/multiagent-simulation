"""Acceptance tests for the Communication part (Info/Message/SimPacket).

``Info → Message → SimPacket`` preserves payload, content_type and extras and
stamps ``round_num``; persisted keys are round-scoped and collision-free
(``msg_r{round:06d}_{seq:06d}`` / ``turn_r{round:06d}_{seq:06d}``).
"""

from __future__ import annotations

import os
import unittest

from examples.uTests._helpers import (
    STORE_REQUIRED,
    TempDirTestCase,
    WIRE_KEY_RE,
    TURN_KEY_RE,
    make_channel,
    read_block_records,
)

from masim.communication.base import Message, MessageType
from masim.communication.general import build_message_from_info
from masim.player.base import Info
from masim.proxy.base import SendReceiveConfig, StorageConfig
from masim.proxy.general import SendReceiveProxy, StorageProxy


class TestInfoMessagePacketRoundTrip(TempDirTestCase):
    """The three-layer wire model loses nothing and stamps the round."""

    def test_build_message_from_info_wraps_content_metadata(self) -> None:
        info = Info(
            payload={"price": 10.5},
            content_type="market_broadcast",
            extras={"fundamental": 9.0},
        )
        message = build_message_from_info(info, "market", "investor_1", round_num=4)

        self.assertEqual(message.message_type, MessageType.PEER)
        self.assertEqual(message.sender_id, "market")
        self.assertEqual(message.recipient_id, "investor_1")
        self.assertEqual(message.payload["content"], {"price": 10.5})
        self.assertEqual(message.payload["content_type"], "market_broadcast")
        self.assertEqual(message.payload["extras"], {"fundamental": 9.0})
        self.assertEqual(message.extras, {"round_num": 4})

    def test_encode_decode_preserves_every_message_field(self) -> None:
        channel = make_channel(self.tmp_path("comm"))
        original = build_message_from_info(
            Info(payload={"order": [1, 2]}, content_type="investor_bid"),
            "investor_1",
            "market",
            round_num=7,
        )
        restored = channel.decode_message(channel.encode_message(original))

        self.assertEqual(restored.message_type, original.message_type)
        self.assertEqual(restored.sender_id, original.sender_id)
        self.assertEqual(restored.recipient_id, original.recipient_id)
        self.assertEqual(restored.payload, original.payload)
        self.assertEqual(restored.extras, original.extras)
        self.assertEqual(restored.priority, original.priority)
        self.assertEqual(restored.timestamp, original.timestamp)

    def test_encode_and_deliver_rejects_an_empty_recipient(self) -> None:
        channel = make_channel(self.tmp_path("comm"))
        message = Message(
            message_type=MessageType.PEER,
            sender_id="a",
            payload={"content": {}, "content_type": None, "extras": {}},
            recipient_id=None,
        )
        with self.assertRaises(ValueError):
            channel.encode_and_deliver([message], {})

    def test_encode_and_deliver_rejects_an_unregistered_recipient(self) -> None:
        channel = make_channel(self.tmp_path("comm"))
        message = build_message_from_info(Info(payload={}), "a", "ghost", 1)
        with self.assertRaises(KeyError):
            channel.encode_and_deliver([message], {"other": object()})


class TestHandleIncoming(TempDirTestCase):
    """``handle_incoming`` rebuilds the player-layer Info from the wire."""

    def _queued_info(self, info: Info, round_num: int) -> Info:
        channel = make_channel(self.tmp_path("comm"))
        message = build_message_from_info(info, "market", "investor_1", round_num)
        proxy = SendReceiveProxy(SendReceiveConfig())
        proxy.handle_incoming(channel.decode_message(channel.encode_message(message)))
        received = proxy.get_received_infos()
        self.assertEqual(len(received), 1)
        return received[0]

    def test_handle_incoming_restores_payload_content_type_and_sender(self) -> None:
        received = self._queued_info(
            Info(payload={"price": 3.0}, content_type="market_broadcast"),
            round_num=2,
        )
        self.assertEqual(received.payload, {"price": 3.0})
        self.assertEqual(received.content_type, "market_broadcast")
        self.assertEqual(received.sender_id, "market")
        self.assertIsNotNone(received.time_received)

    def test_handle_incoming_merges_the_routing_round_into_info_extras(self) -> None:
        received = self._queued_info(
            Info(payload={"price": 3.0}, extras={"origin": "market"}), round_num=9
        )
        self.assertEqual(received.extras, {"origin": "market", "round_num": 9})

    def test_content_extras_win_over_the_routing_round(self) -> None:
        """A sender may stamp an explicit round_num on the content envelope."""
        received = self._queued_info(
            Info(payload={"price": 3.0}, extras={"round_num": 5}), round_num=9
        )
        self.assertEqual(received.extras["round_num"], 5)

    def test_send_receive_proxy_queues_are_single_consumption(self) -> None:
        proxy = SendReceiveProxy(SendReceiveConfig())
        info = Info(payload={"a": 1}, sender_id="market")
        proxy.handle_incoming(
            Message(
                message_type=MessageType.PEER,
                sender_id="market",
                recipient_id="p",
                payload={"content": {"a": 1}, "content_type": None, "extras": {}},
                extras={"round_num": 1},
            )
        )
        self.assertTrue(proxy.has_received_infos())
        self.assertEqual(proxy.get_received_senders(), {"market"})
        self.assertEqual(len(proxy.get_received_infos()), 1)
        self.assertEqual(proxy.get_received_infos(), [])
        self.assertFalse(proxy.has_received_infos())

        proxy.enqueue_info(info)
        self.assertEqual(proxy.dequeue_infos(), [info])
        self.assertEqual(proxy.dequeue_infos(), [])


@STORE_REQUIRED
class TestRecordKeyUniqueness(TempDirTestCase):
    """Persisted keys are round-scoped and collision-free."""

    def test_wire_record_keys_are_round_scoped_and_ordered(self) -> None:
        channel = make_channel(self.tmp_path("comm"))
        packet = channel.encode_message(
            build_message_from_info(Info(payload={"n": 0}), "a", "b", round_num=2)
        )
        for _ in range(4):
            channel.record_encoded_message(packet, round_num=2)
        channel.record_encoded_message(packet, round_num=3)

        keys = list(read_block_records(self.tmp_path("comm")))
        self.assertEqual(
            keys,
            [
                "msg_r000002_000001",
                "msg_r000002_000002",
                "msg_r000002_000003",
                "msg_r000002_000004",
                "msg_r000003_000001",
            ],
        )
        for key in keys:
            self.assertRegex(key, WIRE_KEY_RE)

    def test_wire_keys_do_not_collide_across_two_writer_instances(self) -> None:
        """A resumed run is a fresh process with a fresh per-round ordinal."""
        root = self.tmp_path("comm")
        first = make_channel(root)
        packet = first.encode_message(
            build_message_from_info(Info(payload={"n": 0}), "a", "b", round_num=1)
        )
        for _ in range(3):
            first.record_encoded_message(packet, round_num=1)
        first.record_encoded_message(packet, round_num=2)

        # Second writer = new channel instance in the same storage directory.
        second = make_channel(root)
        for _ in range(2):
            second.record_encoded_message(packet, round_num=3)

        keys = list(read_block_records(root))
        self.assertEqual(len(keys), len(set(keys)), "a record key was overwritten")
        self.assertEqual(len(keys), 6)
        self.assertTrue(any(key.startswith("msg_r000003_") for key in keys))

    def test_per_player_message_keys_are_unique_within_a_round(self) -> None:
        proxy = StorageProxy(
            StorageConfig(
                record_path=self.tmp_path("records"),
                record_rounds=True,
                turn_block_size=50,
            )
        )
        for index in range(5):
            proxy.record_message("market", 2, {"order": index}, "received")

        folder = self.tmp_path("records", "market", "messages")
        keys = list(read_block_records(folder))
        self.assertEqual(len(keys), 5)
        self.assertEqual(
            keys,
            [
                "msg_r000002_000001",
                "msg_r000002_000002",
                "msg_r000002_000003",
                "msg_r000002_000004",
                "msg_r000002_000005",
            ],
        )

    def test_per_player_turn_keys_use_the_turn_prefix_and_a_separate_store(
        self,
    ) -> None:
        proxy = StorageProxy(
            StorageConfig(
                record_path=self.tmp_path("records"),
                record_rounds=True,
                turn_block_size=50,
            )
        )
        for _ in range(2):
            proxy.record_turn_result("market", 4, {"turn_result": {}})

        turn_keys = list(read_block_records(self.tmp_path("records", "market", "turns")))
        self.assertEqual(turn_keys, ["turn_r000004_000001", "turn_r000004_000002"])
        for key in turn_keys:
            self.assertRegex(key, TURN_KEY_RE)
        # Messages and turns never share a store directory.
        self.assertFalse(
            any(key.startswith("msg_") for key in turn_keys)
        )

    def test_record_rounds_false_disables_all_recording(self) -> None:
        proxy = StorageProxy(
            StorageConfig(
                record_path=self.tmp_path("records"),
                record_rounds=False,
                turn_block_size=50,
            )
        )
        proxy.record_message("market", 1, {"n": 1}, "received")
        proxy.record_turn_result("market", 1, {"n": 1})
        self.assertFalse(os.path.exists(self.tmp_path("records", "market")))
