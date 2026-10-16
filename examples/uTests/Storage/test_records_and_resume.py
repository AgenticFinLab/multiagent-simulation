"""Acceptance tests for the Storage part (records, history, resume).

``HistoryBuffer`` keeps the newest entries hot and spills the rest to disk in
blocks, with ``flush()`` persisting the final batch; ``write_resume_checkpoint``
is atomic and ``detect_resume_round`` reads it back; ``_clear_run_outputs``
deletes exactly the derived dirs and can never escape the run root.
"""

from __future__ import annotations

import json
import os
import unittest

from examples.uTests._helpers import (
    STORE_REQUIRED,
    TempDirTestCase,
    read_batch_values,
    write_json,
)

from masim.simulator.general import _clear_run_outputs
from masim.simulator.resume_scanner import (
    detect_resume_round,
    max_persisted_message_round,
    write_resume_checkpoint,
)
from masim.utils.history import HistoryBuffer
from masim.utils.result_loader import load_results, load_simulation_data


class TestHistoryBufferHotStorage(TempDirTestCase):
    """Hot-path behaviour must work without the optional disk backend."""

    def test_construction_is_lazy_and_creates_no_directory(self) -> None:
        folder = self.tmp_path("history")
        buffer = HistoryBuffer(folder=folder, entry_limit=3, block_size=3)
        self.assertIsNone(buffer.cold_store)
        self.assertFalse(os.path.exists(folder))

    def test_recent_entries_stay_in_the_hot_deque(self) -> None:
        buffer = HistoryBuffer(
            folder=self.tmp_path("history"), entry_limit=3, block_size=3
        )
        for value in (1, 2, 3):
            buffer.append(value)
        self.assertEqual(list(buffer), [1, 2, 3])
        self.assertEqual(buffer.recent, [1, 2, 3])
        self.assertEqual(buffer.get_recent(2), [2, 3])
        self.assertEqual(buffer[-1], 3)
        self.assertEqual(buffer[0], 1)
        self.assertEqual(len(buffer), 3)
        self.assertEqual(buffer.cold_count, 0)

    def test_index_out_of_range_raises(self) -> None:
        buffer = HistoryBuffer(
            folder=self.tmp_path("history"), entry_limit=2, block_size=2
        )
        buffer.append("only")
        with self.assertRaises(IndexError):
            buffer.get(4)


@STORE_REQUIRED
class TestHistoryBufferColdSpill(TempDirTestCase):
    """Overflow moves the oldest entry to cold storage in block batches."""

    def test_entries_spill_once_the_block_size_is_reached(self) -> None:
        buffer = HistoryBuffer(
            folder=self.tmp_path("history"), entry_limit=3, block_size=3
        )
        for value in range(6):
            buffer.append(value)
        # 1,2,3 were evicted and written as one full block; 4,5,6 stay hot.
        self.assertEqual(buffer.cold_count, 3)
        self.assertEqual(buffer.recent, [3, 4, 5])
        self.assertTrue(os.path.exists(self.tmp_path("history")))

    def test_flush_persists_the_final_partial_block(self) -> None:
        buffer = HistoryBuffer(
            folder=self.tmp_path("history"), entry_limit=3, block_size=3
        )
        for value in range(6):
            buffer.append(value)
        buffer.flush()
        self.assertEqual(buffer.recent, [])
        self.assertEqual(buffer.cold_count, 6)
        self.assertEqual(read_batch_values(self.tmp_path("history")), [0, 1, 2, 3, 4, 5])

    def test_get_all_returns_the_complete_series_in_order(self) -> None:
        buffer = HistoryBuffer(
            folder=self.tmp_path("history"), entry_limit=2, block_size=2
        )
        for value in range(9):
            buffer.append(value)
        self.assertEqual(buffer.get_all(), list(range(9)))
        self.assertEqual(len(buffer), 9)

    def test_cold_blocks_are_durable_after_flush(self) -> None:
        folder = self.tmp_path("history")
        buffer = HistoryBuffer(folder=folder, entry_limit=2, block_size=2)
        for value in range(5):
            buffer.append(value)
        buffer.flush()
        # Flushing empties the hot deque; the full series lives in the blocks.
        self.assertEqual(buffer.recent, [])
        self.assertEqual(read_batch_values(folder), list(range(5)))


class TestResumeCheckpoint(TempDirTestCase):
    """The progress marker is atomic and authoritative for resume."""

    def test_write_is_atomic_and_leaves_no_partial_file(self) -> None:
        root = self.tmp_path("run")
        write_resume_checkpoint(root, 7)
        names = sorted(os.listdir(root))
        self.assertEqual(names, [".masim-progress.json"])
        self.assertFalse([name for name in names if name.endswith(".tmp")])
        with open(os.path.join(root, ".masim-progress.json"), encoding="utf-8") as h:
            self.assertEqual(json.load(h), {"completed_round": 7})

    def test_detect_resume_round_reads_the_checkpoint_back(self) -> None:
        root = self.tmp_path("run")
        write_resume_checkpoint(root, 3)
        self.assertEqual(detect_resume_round(root), 3)
        # A later completed round overwrites the marker in place.
        write_resume_checkpoint(root, 4)
        self.assertEqual(detect_resume_round(root), 4)

    def test_detect_resume_round_of_an_empty_or_missing_directory_is_zero(
        self,
    ) -> None:
        self.assertEqual(detect_resume_round(self.tmp_path("missing")), 0)
        os.makedirs(self.tmp_path("empty"))
        self.assertEqual(detect_resume_round(self.tmp_path("empty")), 0)

    def test_detect_resume_round_ignores_a_corrupt_marker(self) -> None:
        root = self.tmp_path("run")
        os.makedirs(root)
        with open(os.path.join(root, ".masim-progress.json"), "w", encoding="utf-8") as h:
            h.write("{not json")
        self.assertEqual(detect_resume_round(root), 0)

    def test_detect_resume_round_falls_back_to_environment_messages(self) -> None:
        root = self.tmp_path("run")
        write_json(
            os.path.join(root, "environment", "messages", "msg_block_0.json"),
            {
                "msg_r000005_000001": {"round_num": 5},
                "msg_r000009_000001": {"round_num": 9},
            },
        )
        self.assertEqual(detect_resume_round(root), 9)
        self.assertEqual(
            max_persisted_message_round(
                os.path.join(root, "environment", "messages")
            ),
            9,
        )

    def test_detect_resume_round_falls_back_to_coordinator_turns(self) -> None:
        root = self.tmp_path("run")
        write_json(
            os.path.join(root, "market", "turns", "turn_block_0.json"),
            {"turn_r000004_000001": {"round_num": 4}},
        )
        self.assertEqual(detect_resume_round(root), 4)

    def test_max_persisted_message_round_of_a_missing_dir_is_zero(self) -> None:
        self.assertEqual(max_persisted_message_round(self.tmp_path("nope")), 0)


class TestClearRunOutputs(TempDirTestCase):
    """``--fresh`` cleanup is complete for derived dirs and safely scoped."""

    def _run_root(self) -> str:
        root = self.tmp_path("experiment")
        for name in (
            "records",
            "communication",
            "monitoring",
            "checkpoints",
            "keepme",
        ):
            os.makedirs(os.path.join(root, name), exist_ok=True)
        with open(os.path.join(root, "keepme", "f.txt"), "w", encoding="utf-8") as h:
            h.write("keep")
        return root

    def test_clear_run_outputs_removes_exactly_the_derived_directories(self) -> None:
        root = self._run_root()
        removed = _clear_run_outputs(os.path.join(root, "records"))
        self.assertEqual(
            sorted(removed),
            ["checkpoints", "communication", "monitoring", "records"],
        )
        for name in removed:
            self.assertFalse(os.path.isdir(os.path.join(root, name)))

    def test_clear_run_outputs_preserves_unrelated_neighbours(self) -> None:
        root = self._run_root()
        _clear_run_outputs(os.path.join(root, "records"))
        self.assertTrue(os.path.isdir(os.path.join(root, "keepme")))
        self.assertTrue(os.path.isfile(os.path.join(root, "keepme", "f.txt")))
        self.assertEqual(sorted(os.listdir(root)), ["keepme"])

    def test_clear_run_outputs_skips_missing_directories(self) -> None:
        root = self.tmp_path("experiment")
        os.makedirs(os.path.join(root, "records"))
        removed = _clear_run_outputs(os.path.join(root, "records"))
        self.assertEqual(removed, ["records"])

    def test_clear_run_outputs_cannot_escape_the_run_root(self) -> None:
        """A ``..``-shaped record_path must never delete the parent directory."""
        nested = self.tmp_path("nested")
        sentinel = self.tmp_path("sentinel_keep")
        os.makedirs(nested)
        os.makedirs(sentinel)
        removed = _clear_run_outputs(os.path.join(nested, ".."))
        self.assertEqual(removed, [])
        self.assertTrue(os.path.isdir(sentinel))
        self.assertTrue(os.path.isdir(nested))


class TestResultLoader(TempDirTestCase):
    """``load_results`` reflects the on-disk layout lazily."""

    def _build_record_tree(self) -> str:
        records = self.tmp_path("records")
        write_json(
            os.path.join(records, "market", "turns", "turn_block_0.json"),
            {
                "turn_r000001_000001": {
                    "round_num": 1,
                    "timestamp": "t1",
                    "turn_result": {
                        "step_results": [
                            {
                                "decision_payload": {"action": "hold", "price": 9.5},
                                "action": {},
                            }
                        ],
                        "final_action": {},
                    },
                }
            },
        )
        write_json(
            os.path.join(records, "market", "messages", "msg_block_0.json"),
            {
                "msg_r000001_000001": {
                    "round_num": 1,
                    "direction": "received",
                    "timestamp": "t1",
                    "message": {"sender_id": "investor_1"},
                }
            },
        )
        write_json(
            os.path.join(records, "market", "price", "batch_block_0.json"),
            {"batch_00000000_00000000": [9.5]},
        )
        return records

    def test_results_reflect_the_directory_layout(self) -> None:
        records = self._build_record_tree()
        results = load_results(records)

        self.assertIn("market", results.players)
        self.assertEqual(results.player("market").role, "coordinator")
        player = results.player("market")
        self.assertEqual(player.turns.rounds(), [1])
        self.assertEqual(player.turns.payload(1), {"action": "hold", "price": 9.5})
        self.assertEqual(player.turns.field("action"), {1: "hold"})
        self.assertEqual(player.turns.turn_result(1)["final_action"], {})
        self.assertEqual(player.messages.rounds(), [1])
        self.assertEqual(len(player.messages.by_direction("received")), 1)
        self.assertEqual(len(player.messages.by_sender("investor_1")), 1)
        self.assertEqual(player.batch_store_names, ["price"])
        self.assertEqual(player.batch("price").all(), [9.5])
        self.assertEqual(player.batch("price").at_index(0), 9.5)

    def test_cross_player_queries_filter_by_role_and_direction(self) -> None:
        records = self._build_record_tree()
        results = load_results(records)

        self.assertEqual(results.all_payloads(role="coordinator")["market"][1]["action"], "hold")
        self.assertEqual(results.all_field("action"), {"market": {1: "hold"}})
        self.assertEqual(
            set(results.all_messages(direction="received")), {"market"}
        )
        self.assertEqual(results.players_by_role("player"), {})

    def test_missing_player_raises_key_error(self) -> None:
        records = self._build_record_tree()
        results = load_results(records)
        with self.assertRaises(KeyError):
            results.player("ghost")

    def test_a_player_without_stores_reports_empty_results(self) -> None:
        records = self.tmp_path("records")
        os.makedirs(os.path.join(records, "market", "turns"))
        results = load_results(records)
        player = results.player("market")
        self.assertTrue(player.turns.exists)
        self.assertEqual(player.turns.rounds(), [])
        self.assertFalse(player.messages.exists)
        self.assertEqual(player.messages.all(), [])
        self.assertEqual(player.batch_store_names, [])

    def test_config_form_resolves_roles_and_record_path(self) -> None:
        records = self._build_record_tree()
        config = {
            "setting": {"record_path": records},
            "players": {
                "market": {"config": {"identity": "market", "role": "coordinator"}}
            },
            "topology": {"type": "star", "sources": ["market"], "connections": {}},
        }
        results = load_results(config)
        self.assertEqual(results.player("market").role, "coordinator")
        self.assertEqual(results.topology.type, "star")
        self.assertEqual(results.topology.sources, ["market"])

    def test_load_simulation_data_is_a_backward_compatible_alias(self) -> None:
        records = self._build_record_tree()
        self.assertIn("market", load_simulation_data(records).players)
