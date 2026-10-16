"""Acceptance tests for the Time part (execution clock + readiness gate).

``ExecutionClock`` accumulates executions; topology BFS puts the configured
sources at level 0; a player is ready iff every expected sender arrived, and
level-0 initiators are exempt only in the bootstrap round (``bootstrap=True``).
"""

from __future__ import annotations

import unittest

# The acceptance suite never renders; force a headless backend before pyplot
# is imported by masim.utils.topology.
import matplotlib

matplotlib.use("Agg")

from masim.player.base import PlayerConfig
from masim.player.general import GeneralPlayer
from masim.simulator.base import ExecutionClock, RoundPhase
from masim.utils.topology import TopologyGraph


def _topology(sources, connections) -> TopologyGraph:
    """Build a TopologyGraph from an inline config."""
    return TopologyGraph({"sources": list(sources), "connections": connections})


class TestExecutionClock(unittest.TestCase):
    """``ExecutionClock`` is the shared timing primitive at every level."""

    def test_clock_accumulates_completed_executions(self) -> None:
        clock = ExecutionClock()
        self.assertEqual(clock.count_executions, 0)
        for _ in range(3):
            clock.tick_start()
            clock.tick_end()
        self.assertEqual(clock.count_executions, 3)
        self.assertGreaterEqual(clock.total_duration_ms, clock.last_duration_ms)
        self.assertGreaterEqual(clock.total_duration_ms, 0.0)
        self.assertIsNone(clock.start_time)

    def test_clock_tick_end_without_a_start_is_a_noop(self) -> None:
        clock = ExecutionClock()
        clock.tick_end()
        self.assertEqual(clock.count_executions, 0)
        self.assertEqual(clock.total_duration_ms, 0.0)

    def test_clock_to_dict_reports_the_average_over_completed_executions(self) -> None:
        clock = ExecutionClock()
        self.assertEqual(clock.to_dict()["avg_duration_ms"], 0.0)
        clock.tick_start()
        clock.tick_end()
        snapshot = clock.to_dict()
        self.assertEqual(
            set(snapshot),
            {
                "count_executions",
                "last_duration_ms",
                "total_duration_ms",
                "avg_duration_ms",
            },
        )
        self.assertEqual(snapshot["count_executions"], 1)
        self.assertEqual(snapshot["avg_duration_ms"], snapshot["total_duration_ms"])

    def test_round_phase_has_exactly_the_three_documented_phases(self) -> None:
        self.assertEqual(
            [phase.name for phase in RoundPhase],
            ["PENDING", "EXECUTING", "COMPLETE"],
        )


class TestExecutionLevels(unittest.TestCase):
    """BFS from the configured sources defines the level-ordered schedule."""

    def test_chain_topology_yields_one_level_per_node(self) -> None:
        graph = _topology(["a"], {"a": ["b"], "b": ["c"]})
        self.assertEqual(graph.get_execution_levels(), [["a"], ["b"], ["c"]])

    def test_star_topology_puts_every_spoke_on_level_one(self) -> None:
        graph = _topology(
            ["hub"],
            {"hub": ["s1", "s2", "s3"], "s1": ["hub"], "s2": ["hub"], "s3": ["hub"]},
        )
        levels = graph.get_execution_levels()
        self.assertEqual(levels[0], ["hub"])
        self.assertEqual(set(levels[1]), {"s1", "s2", "s3"})
        self.assertEqual(len(levels), 2)

    def test_diamond_topology_places_the_join_after_both_parents(self) -> None:
        graph = _topology(
            ["a"],
            {"a": ["b", "c"], "b": ["d"], "c": ["d"]},
        )
        levels = graph.get_execution_levels()
        self.assertEqual(levels[0], ["a"])
        self.assertEqual(set(levels[1]), {"b", "c"})
        self.assertEqual(levels[2], ["d"])

    def test_without_sources_every_player_lands_in_one_parallel_level(self) -> None:
        graph = TopologyGraph({"connections": {"a": ["b"], "b": ["c"]}})
        levels = graph.get_execution_levels()
        self.assertEqual(len(levels), 1)
        self.assertEqual(set(levels[0]), {"a", "b", "c"})

    def test_levels_are_cached_until_the_cache_is_invalidated(self) -> None:
        graph = _topology(["a"], {"a": ["b"]})
        self.assertEqual(graph.get_execution_levels(), [["a"], ["b"]])
        # A mutation without invalidation keeps serving the stale schedule.
        graph.graph.add_edge("b", "c")
        self.assertEqual(graph.get_execution_levels(), [["a"], ["b"]])
        graph.invalidate_levels_cache()
        self.assertEqual(graph.get_execution_levels(), [["a"], ["b"], ["c"]])

    def test_sources_that_are_not_in_the_graph_produce_no_levels(self) -> None:
        graph = _topology(["ghost"], {"a": ["b"]})
        self.assertEqual(graph.get_execution_levels(), [])

    def test_get_senders_and_targets_mirror_the_edge_direction(self) -> None:
        graph = _topology(["a"], {"a": ["b"], "b": ["c"]})
        self.assertEqual(graph.get_targets("a"), ["b"])
        self.assertEqual(graph.get_senders("b"), ["a"])
        self.assertTrue(graph.can_send("a", "b"))
        self.assertFalse(graph.can_send("b", "a"))
        self.assertEqual(graph.get_targets("nope"), [])


class TestReadinessGate(unittest.TestCase):
    """``is_received_ready`` is a hard gate owned by the Player."""

    @staticmethod
    def _player(expected_senders=()):
        player = GeneralPlayer(PlayerConfig(name="p", identity="p"))
        player.expected_senders = set(expected_senders)
        return player

    def test_level_zero_in_the_bootstrap_round_is_ready_without_inbound(self) -> None:
        player = self._player({"market"})
        self.assertTrue(player.is_received_ready(1, set(), level=0))

    def test_bootstrap_kwarg_overrides_the_round_one_fallback(self) -> None:
        player = self._player({"market"})
        # A resumed run starts at N > 1; the Simulator marks it explicitly.
        self.assertTrue(
            player.is_received_ready(5, set(), level=0, bootstrap=True)
        )

    def test_non_bootstrap_level_zero_demands_every_expected_sender(self) -> None:
        """Documents the resumed-run hazard the ``bootstrap`` kwarg fixes.

        Level-0 initiators have no level below them, so the only way this can
        be False is a resumed run (round N > 1) in which the caller forgot
        ``bootstrap=True``.  The Simulator now always passes it; this test pins
        the current fallback semantics so a future relaxation is deliberate.
        """
        player = self._player({"market"})
        self.assertFalse(player.is_received_ready(5, set(), level=0))
        self.assertTrue(player.is_received_ready(5, {"market"}, level=0))

    def test_level_one_requires_every_expected_sender(self) -> None:
        player = self._player({"market"})
        self.assertFalse(player.is_received_ready(1, set(), level=1))
        self.assertFalse(player.is_received_ready(1, {"other"}, level=1))
        self.assertTrue(player.is_received_ready(1, {"market"}, level=1))

    def test_a_subset_of_expected_senders_is_not_enough(self) -> None:
        player = self._player({"a", "b"})
        self.assertFalse(player.is_received_ready(2, {"a"}, level=1))
        self.assertTrue(player.is_received_ready(2, {"a", "b"}, level=1))

    def test_a_player_without_expected_senders_is_always_ready(self) -> None:
        player = self._player()
        self.assertTrue(player.is_received_ready(2, set(), level=1))
        self.assertTrue(player.is_received_ready(9, set(), level=0))

    def test_bootstrap_does_not_relax_non_initiator_levels(self) -> None:
        player = self._player({"market"})
        self.assertFalse(
            player.is_received_ready(5, set(), level=1, bootstrap=True)
        )

    def test_level_defaults_to_zero_when_the_kwarg_is_absent(self) -> None:
        player = self._player({"market"})
        self.assertTrue(player.is_received_ready(1, set()))
