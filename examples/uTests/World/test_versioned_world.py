"""Acceptance tests for ``VersionedSharedState`` (the World implementation).

Contract
--------
``set()`` stages, ``commit()`` publishes atomically as one version, and reads
only ever see committed values. Variables are namespaced by scope, so several
markets/assets coexist; ``read_all(key)`` reads one variable across every scope,
which is the primitive cross-market aggregation needs. ``snapshot()`` /
``restore()`` make the world the first part of the framework that can be moved
back in time.

No Ray, no filesystem.
"""

from __future__ import annotations

import json
import unittest

from masim.platform.world.base import SharedState, WorldVersion
from masim.world.shared_state import VersionedSharedState


class TestVersionedSharedState(unittest.TestCase):
    """Read/write/version/snapshot semantics."""

    def setUp(self) -> None:
        self.world = VersionedSharedState()

    def test_is_a_shared_state(self) -> None:
        self.assertIsInstance(self.world, SharedState)

    def test_missing_key_raises_but_a_default_is_honoured(self) -> None:
        with self.assertRaises(KeyError):
            self.world.get("price")
        self.assertIsNone(self.world.get("price", None))
        self.assertEqual(self.world.get("price", 0.0), 0.0)

    def test_set_stages_and_commit_publishes(self) -> None:
        self.world.set("price", 100.0, WorldVersion(round_num=1, level=0))
        # Staged, not yet visible: a reader must never see a half-applied level.
        with self.assertRaises(KeyError):
            self.world.get("price")
        self.assertTrue(self.world.has_pending())

        self.world.commit()
        self.assertEqual(self.world.get("price"), 100.0)
        self.assertFalse(self.world.has_pending())

    def test_commit_records_one_history_entry_per_changed_version(self) -> None:
        self.world.set("price", 1.0, WorldVersion(round_num=1, level=0))
        self.world.commit()
        self.world.set("price", 2.0, WorldVersion(round_num=2, level=0))
        self.world.commit()
        # A commit with nothing staged adds no history entry.
        self.world.commit()
        history = self.world.history()
        self.assertEqual([h["round_num"] for h in history], [1, 2])
        self.assertEqual(history[-1]["changed"], ["world.price"])

    def test_version_tracks_the_newest_staged_write(self) -> None:
        self.assertEqual(self.world.version(), WorldVersion(round_num=0, level=0))
        self.world.set("price", 1.0, WorldVersion(round_num=3, level=1))
        self.world.commit()
        self.assertEqual(self.world.version(), WorldVersion(round_num=3, level=1))

    def test_committed_values_survive_a_later_commit(self) -> None:
        self.world.set("price", 1.0, WorldVersion(round_num=1, level=0))
        self.world.commit()
        self.world.set("volume", 5.0, WorldVersion(round_num=2, level=0))
        self.world.commit()
        self.assertEqual(self.world.get("price"), 1.0)
        self.assertEqual(self.world.get("volume"), 5.0)
        self.assertEqual(len(self.world), 2)


class TestScopesAndMultipleMarkets(unittest.TestCase):
    """Scopes are the multi-market / multi-asset primitive."""

    def setUp(self) -> None:
        self.world = VersionedSharedState()

    def _seed_two_markets(self) -> None:
        version = WorldVersion(round_num=1, level=1)
        self.world.set("price", 100.0, version, scope="market_a")
        self.world.set("price", 250.0, version, scope="market_b")
        self.world.set("volume", 7.0, version, scope="market_a")
        self.world.commit(version)

    def test_same_key_lives_independently_per_scope(self) -> None:
        self._seed_two_markets()
        self.assertEqual(self.world.get("price", scope="market_a"), 100.0)
        self.assertEqual(self.world.get("price", scope="market_b"), 250.0)
        self.assertEqual(self.world.scopes(), ["market_a", "market_b"])

    def test_read_all_returns_one_variable_across_every_scope(self) -> None:
        self._seed_two_markets()
        self.assertEqual(self.world.read_all("price"), {"market_a": 100.0, "market_b": 250.0})
        # A key present in only one scope is simply absent from the others.
        self.assertEqual(self.world.read_all("volume"), {"market_a": 7.0})

    def test_snapshot_can_be_scoped(self) -> None:
        self._seed_two_markets()
        self.assertEqual(self.world.snapshot("market_a"), {"price": 100.0, "volume": 7.0})
        self.assertIn("market_b.price", self.world.snapshot())

    def test_keys_are_reported_short_within_a_scope(self) -> None:
        self._seed_two_markets()
        self.assertEqual(self.world.keys("market_a"), ["price", "volume"])
        self.assertEqual(
            self.world.keys(), ["market_a.price", "market_a.volume", "market_b.price"]
        )

    def test_an_unscoped_write_lands_in_the_default_scope(self) -> None:
        self.world.set("sentiment", 0.5, WorldVersion(round_num=1, level=0))
        self.world.commit()
        self.assertEqual(self.world.get("sentiment", scope="world"), 0.5)
        self.assertEqual(self.world.scopes(), ["world"])


class TestSnapshotRestoreAndPersistence(unittest.TestCase):
    """The world can be taken back in time and written down."""

    def test_to_dict_is_json_serialisable_and_round_trips(self) -> None:
        world = VersionedSharedState()
        version = WorldVersion(round_num=4, level=2)
        world.set("price", 12.5, version, scope="market")
        world.commit(version)

        payload = json.loads(json.dumps(world.to_dict(), default=str))
        self.assertEqual(payload["version"], {"round_num": 4, "level": 2, "seq": 0})
        self.assertEqual(payload["scopes"], ["market"])
        self.assertEqual(len(payload["history"]), 1)

        restored = VersionedSharedState()
        restored.restore(payload)
        self.assertEqual(restored.get("price", scope="market"), 12.5)
        self.assertEqual(restored.version(), version)

    def test_restore_replaces_rather_than_merges(self) -> None:
        world = VersionedSharedState()
        world.set("price", 1.0, WorldVersion(round_num=1, level=0))
        world.commit()
        world.restore({"version": {"round_num": 0, "level": 0}, "values": {}})
        self.assertEqual(len(world), 0)
        with self.assertRaises(KeyError):
            world.get("price")

    def test_snapshot_is_a_copy_not_a_live_view(self) -> None:
        world = VersionedSharedState()
        world.set("price", 1.0, WorldVersion(round_num=1, level=0))
        world.commit()
        snap = world.snapshot()
        snap["world.price"] = 999.0
        self.assertEqual(world.get("price"), 1.0)


if __name__ == "__main__":
    unittest.main()
