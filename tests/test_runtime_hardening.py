"""Regression tests for the runtime-hardening pass.

Run with::

    PYTHONPATH=. python3 -m unittest discover -s tests -t tests -v

Covers three defects that were silently corrupting experiment data:

1. ``StorageProxy`` per-player message/turn records collided on a
   second-resolution wall-clock key, so a coordinator receiving several
   messages in the same round and second kept only one of them
   (``BlockBasedStoreManager`` treats a repeated key as an *update*).
2. The channel-level encoded-message store used the wall clock as its only
   disambiguator, which is unsafe on platforms with coarse timer granularity.
3. ``GeneralSimulator.run()`` auto-resumed a partially-written
   ``record_path``, mixing two datasets in one directory. It now refuses
   unless the caller passes ``resume=True`` / ``fresh=True``.

No Ray cluster is required.
"""

import asyncio
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from masim.communication.base import Message, MessageType, SimPacket
from masim.communication.general import GeneralCommunicationChannel
from masim.persona.general import PlayerPersona
from masim.player.base import PlayerConfig
from masim.player.general import GeneralPlayer
from masim.proxy.base import StorageConfig
from masim.proxy.general import StorageProxy
from masim.simulator.base import SimulationConfig
from masim.simulator.general import (
    GeneralSimulator,
    _clear_run_outputs,
    derive_persona_output_paths,
)
from masim.simulator.resume_scanner import write_resume_checkpoint


def _count_records(folder: str) -> int:
    """Count records stored by ``BlockBasedStoreManager`` under ``folder``."""
    total = 0
    for path in Path(folder).glob("*_block_*.json"):
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
        total += len(payload)
    return total


def _lmbase_available() -> bool:
    """True when the optional ``lmbase`` record-store backend is installed."""
    try:
        from lmbase.utils.tools import BlockBasedStoreManager  # noqa: F401
    except Exception:
        return False
    return True


LMBAVAILABLE = _lmbase_available()
# Writing records needs the lmbase block store; the framework core (import,
# simulator construction, output cleanup, resume policy) must work without it.
STORE_REQUIRED = unittest.skipUnless(
    LMBAVAILABLE, "optional lmbase record-store backend not installed"
)


@STORE_REQUIRED
class TestMessageRecordUniqueness(unittest.TestCase):
    """Every inbound message must survive to disk."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="masim-records-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_all_inbound_messages_are_persisted(self) -> None:
        """N messages recorded in one round within one second ⇒ N records.

        The pre-fix key was ``msg_r{round}_{%m%d%H%M%S}``; because the loop
        below completes well inside a second, all 12 records collapsed onto a
        single key and only 1 survived.
        """
        proxy = StorageProxy(
            StorageConfig(
                record_path=os.path.join(self.tmp, "records"),
                record_rounds=True,
                turn_block_size=50,
            )
        )
        for index in range(12):
            proxy.record_message(
                player_id="market",
                round_num=1,
                message={"order": index},
                direction="inbound",
            )
        asyncio.run(proxy.shutdown())
        stored = _count_records(os.path.join(self.tmp, "records", "market", "messages"))
        self.assertEqual(stored, 12, "inbound messages were overwritten")

    def test_record_keys_are_round_scoped_and_ordered(self) -> None:
        """Keys carry the round and a monotonic ordinal, not a wall clock."""
        proxy = StorageProxy(
            StorageConfig(
                record_path=os.path.join(self.tmp, "records"),
                record_rounds=True,
                turn_block_size=50,
            )
        )
        for index in range(3):
            proxy.record_message("investor", 2, {"n": index}, "outbound")

        block_path = Path(self.tmp, "records", "investor", "messages", "msg_block_0.json")
        keys = list(json.loads(block_path.read_text()))
        self.assertEqual(keys, ["msg_r000002_000001", "msg_r000002_000002", "msg_r000002_000003"])

    def test_turn_records_are_persisted(self) -> None:
        proxy = StorageProxy(
            StorageConfig(
                record_path=os.path.join(self.tmp, "records"),
                record_rounds=True,
                turn_block_size=50,
            )
        )
        for _ in range(2):
            proxy.record_turn_result("market", 1, {"turn": "x"})

        stored = _count_records(os.path.join(self.tmp, "records", "market", "turns"))
        self.assertEqual(stored, 2)


@STORE_REQUIRED
class TestInboundRoundLabelling(unittest.TestCase):
    """Inbound records must carry the SENDER's round, not the receiver's.

    Inbound delivery happens during the sender's level, so an agent at level
    > 0 receives a broadcast *before* its own ``operate()`` for that round.
    Recording ``persona.current_round`` therefore labelled every inbound
    message with the previous round (and round 0 before the first
    ``operate()``), corrupting the per-round analysis of order flow.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="masim-round-label-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _persona(self) -> PlayerPersona:
        return PlayerPersona(
            player_class=GeneralPlayer,
            player_config=PlayerConfig(name="p1", identity="investor_1"),
            persona_config={
                "proxy": {
                    "storage": {
                        "record_path": os.path.join(self.tmp, "records"),
                        "checkpoint_dir": os.path.join(self.tmp, "checkpoints"),
                    },
                    "monitoring": {"record_path": os.path.join(self.tmp, "monitoring")},
                    "communication": {},
                }
            },
        )

    @staticmethod
    def _message(round_num: int) -> Message:
        return Message(
            message_type=MessageType.PEER,
            sender_id="market",
            recipient_id="investor_1",
            payload={
                "content": {"price": 10.0},
                "content_type": "market",
                "extras": {},
            },
            extras={"round_num": round_num},
        )

    def test_recorded_round_comes_from_the_message(self) -> None:
        persona = self._persona()
        asyncio.run(persona.initialize())
        # Simulates the real ordering: inbound arrives before any operate().
        self.assertEqual(persona.current_round, 0)

        for round_num in (7, 8):
            persona.receive_message(self._message(round_num))

        block = Path(self.tmp, "records", "investor_1", "messages", "msg_block_0.json")
        records = json.loads(block.read_text())
        self.assertEqual(
            sorted(records), ["msg_r000007_000001", "msg_r000008_000001"]
        )
        self.assertEqual([r["round_num"] for r in records.values()], [7, 8])

    def test_key_prefix_and_stored_round_agree(self) -> None:
        """Guards the invariant a reader relies on when filtering by round."""
        persona = self._persona()
        asyncio.run(persona.initialize())
        for round_num in (3, 3, 4):
            persona.receive_message(self._message(round_num))

        block = Path(self.tmp, "records", "investor_1", "messages", "msg_block_0.json")
        records = json.loads(block.read_text())
        for key, record in records.items():
            self.assertEqual(int(key.split("_")[1][1:]), record["round_num"])

    def test_delivered_info_carries_the_round(self) -> None:
        """The documented feedback-edge hook needs info.extras['round_num'].

        ``build_message_from_info`` stamps the round on the Message; the proxy
        must merge it into the Info unit, otherwise a player cannot tell a
        current message from a round-lagged one.
        """
        persona = self._persona()
        asyncio.run(persona.initialize())
        persona.receive_message(self._message(11))

        infos = persona.message_proxy.get_received_infos()
        self.assertEqual(len(infos), 1)
        self.assertEqual(infos[0].extras.get("round_num"), 11)
        # The sender's content extras must survive the merge.
        self.assertEqual(infos[0].payload, {"price": 10.0})


@STORE_REQUIRED
class TestChannelRecordUniqueness(unittest.TestCase):
    """The wire-level store must not depend on wall-clock resolution."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="masim-channel-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_every_encoded_message_is_persisted(self) -> None:
        channel = GeneralCommunicationChannel(
            {
                "storage_path": os.path.join(self.tmp, "communication"),
                "record_messages": True,
                "message_block_size": 500,
            }
        )
        for index in range(25):
            channel.record_encoded_message(
                SimPacket(
                    encoded=json.dumps({"i": index}),
                    sender_id="a",
                    recipient_id="b",
                ),
                round_num=1,
            )
        stored = _count_records(os.path.join(self.tmp, "communication"))
        self.assertEqual(stored, 25, "encoded wire messages were overwritten")

    def test_resumed_run_does_not_overwrite_previous_records(self) -> None:
        """A resumed run is a new process: its key counter restarts.

        Without the round prefix in the key, the resumed run's first messages
        reused ``msg_00000001``… and overwrote the previous run's records in
        the same ``communication/`` directory. Keys are now round-scoped, so
        run 2 appends instead of replacing.
        """
        cfg = {
            "storage_path": os.path.join(self.tmp, "communication"),
            "record_messages": True,
            "message_block_size": 500,
        }

        def one_process_rounds(rounds, per_round=4) -> None:
            # A fresh channel == a fresh process == counter resets to 0.
            channel = GeneralCommunicationChannel(cfg)
            for round_num in rounds:
                for index in range(per_round):
                    channel.record_encoded_message(
                        SimPacket(
                            encoded=json.dumps({"round": round_num, "i": index}),
                            sender_id="a",
                            recipient_id="b",
                        ),
                        round_num=round_num,
                    )

        one_process_rounds((1, 2, 3))
        self.assertEqual(_count_records(cfg["storage_path"]), 12)

        one_process_rounds((4, 5))
        self.assertEqual(
            _count_records(cfg["storage_path"]),
            20,
            "the resumed run overwrote records written by the earlier run",
        )


class TestRunOutputCleanup(unittest.TestCase):
    """``_clear_run_outputs`` must be complete *and* unable to escape."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="masim-cleanup-")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_removes_every_derived_output_dir(self) -> None:
        record_root = os.path.join(self.tmp, "EXPERIMENT", "Demo", "Rule", "records")
        for name in ("records", "communication", "monitoring", "checkpoints"):
            os.makedirs(os.path.join(os.path.dirname(record_root), name), exist_ok=True)
        # A directory outside the run root must never be touched.
        outsider = os.path.join(self.tmp, "EXPERIMENT", "OtherScenario", "records")
        os.makedirs(outsider, exist_ok=True)

        removed = _clear_run_outputs(record_root)

        self.assertEqual(
            sorted(removed), ["checkpoints", "communication", "monitoring", "records"]
        )
        self.assertFalse(os.path.isdir(os.path.dirname(record_root) + "/records"))
        self.assertTrue(os.path.isdir(outsider), "cleanup escaped the run root")

    def test_relative_record_path_does_not_escape(self) -> None:
        """A bare relative path resolves inside the CWD, not to '/'."""
        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            os.makedirs("records", exist_ok=True)
            removed = _clear_run_outputs("records")
            self.assertEqual(removed, ["records"])
            self.assertFalse(os.path.isdir("records"))
        finally:
            os.chdir(cwd)

    def test_missing_dirs_are_skipped(self) -> None:
        record_root = os.path.join(self.tmp, "EXPERIMENT", "Demo", "records")
        os.makedirs(record_root, exist_ok=True)
        self.assertEqual(_clear_run_outputs(record_root), ["records"])


class TestResumePolicy(unittest.TestCase):
    """A partially-written run must never be continued by accident."""

    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="masim-resume-")
        self.record_path = os.path.join(self.tmp, "records")
        self.config = SimulationConfig(
            setting={
                "name": "resume_policy_test",
                "total_rounds": 3,
                "record_path": self.record_path,
                "round_history_limit": 3,
                "save_diagram_interval": 0,
            },
            ray={"namespace": "resume_policy_test"},
            players={},
            topology={"type": "star", "connections": {}},
            communication={
                "storage_path": os.path.join(self.tmp, "communication"),
                "record_messages": False,
                "message_block_size": 500,
            },
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_existing_rounds_raise_without_explicit_choice(self) -> None:
        write_resume_checkpoint(self.record_path, 2)
        simulator = GeneralSimulator(self.config)
        with self.assertRaises(RuntimeError) as ctx:
            asyncio.run(simulator.run())
        message = str(ctx.exception)
        self.assertIn("--resume", message)
        self.assertIn("--fresh", message)

    def test_fresh_run_clears_previous_output(self) -> None:
        write_resume_checkpoint(self.record_path, 2)
        os.makedirs(os.path.join(self.tmp, "communication"), exist_ok=True)
        Path(self.tmp, "communication", "msg_block_0.json").write_text("{}")

        simulator = GeneralSimulator(self.config)
        # Nothing left to run after the clear, so run() returns before it
        # would touch Ray — enough to assert the cleanup contract.
        simulator.config.setting["total_rounds"] = 0
        result = asyncio.run(simulator.run(fresh=True))
        self.assertEqual(result, [])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "communication")))
        self.assertFalse(
            os.path.exists(os.path.join(self.record_path, ".masim-progress.json"))
        )

    def test_derived_paths_are_siblings_of_record_root(self) -> None:
        derived = derive_persona_output_paths("/runs/demo/records")
        self.assertEqual(derived["storage"]["record_path"], "/runs/demo/records")
        self.assertEqual(derived["storage"]["checkpoint_dir"], "/runs/demo/checkpoints")
        self.assertEqual(derived["monitoring"]["record_path"], "/runs/demo/monitoring")


if __name__ == "__main__":
    unittest.main()
