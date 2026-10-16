"""Acceptance tests for the Observability part (metrics and events).

``record_metric`` / ``log_event`` append to in-memory buffers and only
``shutdown()`` flushes them to disk; the flush is owned by ``PlayerPersona``,
not the run-level Simulator.  TODO(platform): this is the in-flight fix.
"""

from __future__ import annotations

import ast
import asyncio
import os
import re
import unittest
from pathlib import Path

from examples.uTests._helpers import (
    PROJECT_ROOT,
    STORE_REQUIRED,
    TempDirTestCase,
    read_batch_values,
)

from masim.proxy.base import MonitoringConfig
from masim.proxy.general import MonitoringProxy

_SIMULATOR_DIR = PROJECT_ROOT / "masim" / "simulator"
_PERSONA_MODULE = PROJECT_ROOT / "masim" / "persona" / "general.py"

# ``monitoring.shutdown`` and ``await <proxy>.shutdown()`` spellings.
_MONITORING_SHUTDOWN = re.compile(r"\bmonitoring\s*\.\s*shutdown")


def _module_source(path: Path) -> str:
    """Return the UTF-8 source text of ``path``."""
    return path.read_text(encoding="utf-8")


def _monitoring_proxy() -> MonitoringProxy:
    """Build a MonitoringProxy with the canonical 3-entry hot limit."""
    return MonitoringProxy(MonitoringConfig(record_path="", monitor_hot_limit=3))


class TestMonitoringBuffers(unittest.TestCase):
    """Recording is in-memory and never fails."""

    def test_record_metric_appends_to_the_hot_buffer(self) -> None:
        proxy = _monitoring_proxy()
        asyncio.run(proxy.record_metric("price", 10.5, {"unit": "usd"}))
        asyncio.run(proxy.record_metric("volume", 3))

        metrics = asyncio.run(proxy.get_metrics())
        self.assertEqual([entry["name"] for entry in metrics], ["price", "volume"])
        self.assertEqual(metrics[0]["value"], 10.5)
        self.assertEqual(metrics[0]["tags"], {"unit": "usd"})
        self.assertIn("timestamp", metrics[0])

    def test_log_event_appends_to_the_hot_buffer(self) -> None:
        proxy = _monitoring_proxy()
        asyncio.run(proxy.log_event("round_start", {"round": 1}))
        asyncio.run(proxy.log_event("round_end", {"round": 1}, level="DEBUG"))

        events = asyncio.run(proxy.get_events())
        self.assertEqual(
            [entry["event_type"] for entry in events], ["round_start", "round_end"]
        )
        self.assertEqual(events[1]["level"], "DEBUG")
        self.assertEqual(events[1]["data"], {"round": 1})

    def test_get_metrics_and_events_filter_by_name_and_type(self) -> None:
        proxy = _monitoring_proxy()
        asyncio.run(proxy.record_metric("price", 1))
        asyncio.run(proxy.record_metric("price_spread", 2))
        asyncio.run(proxy.log_event("fill", {}))
        asyncio.run(proxy.log_event("shutdown", {}))

        self.assertEqual(
            [entry["name"] for entry in asyncio.run(proxy.get_metrics("price"))],
            ["price", "price_spread"],
        )
        self.assertEqual(
            [entry["event_type"] for entry in asyncio.run(proxy.get_events("fill"))],
            ["fill"],
        )

    def test_stop_timer_records_a_millisecond_metric(self) -> None:
        proxy = _monitoring_proxy()
        asyncio.run(proxy.start_timer("operate"))
        duration = asyncio.run(proxy.stop_timer("operate"))
        self.assertGreaterEqual(duration, 0.0)
        metrics = asyncio.run(proxy.get_metrics())
        self.assertEqual(metrics[-1]["name"], "timer_operate")
        self.assertEqual(metrics[-1]["tags"], {"unit": "ms"})

    def test_stop_timer_without_a_start_returns_zero(self) -> None:
        proxy = _monitoring_proxy()
        self.assertEqual(asyncio.run(proxy.stop_timer("never_started")), 0.0)

    def test_entries_carry_the_owner_identity_when_the_proxy_has_one(
        self,
    ) -> None:
        from masim.player.base import PlayerConfig
        from masim.player.general import GeneralPlayer

        owner = GeneralPlayer(PlayerConfig(name="p", identity="investor_7"))
        proxy = MonitoringProxy(
            MonitoringConfig(record_path="", monitor_hot_limit=3), owner=owner
        )
        asyncio.run(proxy.record_metric("price", 1))
        asyncio.run(proxy.log_event("boot", {}))
        self.assertEqual(
            asyncio.run(proxy.get_metrics())[0]["entity_id"], "investor_7"
        )
        self.assertEqual(asyncio.run(proxy.get_events())[0]["entity_id"], "investor_7")


@STORE_REQUIRED
class TestMonitoringFlush(TempDirTestCase):
    """``shutdown()`` is what moves the buffers onto disk."""

    def _proxy(self) -> MonitoringProxy:
        return MonitoringProxy(
            MonitoringConfig(
                record_path=self.tmp_path("monitoring"), monitor_hot_limit=3
            )
        )

    def test_buffered_metrics_and_events_are_not_written_before_shutdown(self) -> None:
        proxy = self._proxy()
        asyncio.run(proxy.record_metric("price", 1))
        asyncio.run(proxy.log_event("boot", {}))
        self.assertFalse(os.path.exists(self.tmp_path("monitoring", "metrics")))
        self.assertFalse(os.path.exists(self.tmp_path("monitoring", "events")))

    def test_shutdown_flushes_a_buffer_you_filled_yourself(self) -> None:
        proxy = self._proxy()
        for index in range(5):
            asyncio.run(proxy.record_metric("price", index))
        asyncio.run(proxy.log_event("boot", {"ok": True}))
        asyncio.run(proxy.shutdown())

        metrics_dir = self.tmp_path("monitoring", "metrics")
        events_dir = self.tmp_path("monitoring", "events")
        self.assertTrue(os.path.isdir(metrics_dir))
        self.assertTrue(os.path.isdir(events_dir))
        self.assertEqual(
            [entry["value"] for entry in read_batch_values(metrics_dir)],
            [0, 1, 2, 3, 4],
        )
        self.assertEqual(
            [entry["event_type"] for entry in read_batch_values(events_dir)],
            ["boot"],
        )
        # Flushing empties the hot deques.
        self.assertEqual(asyncio.run(proxy.get_metrics()), [])

    def test_get_all_metrics_reads_back_hot_and_cold(self) -> None:
        proxy = self._proxy()
        for index in range(6):
            asyncio.run(proxy.record_metric("price", index))
        self.assertEqual(len(asyncio.run(proxy.get_metrics())), 3)
        self.assertEqual(len(asyncio.run(proxy.get_all_metrics())), 6)

    def test_the_persona_teardown_flushes_the_monitoring_proxy(self) -> None:
        """The flush is wired into ``PlayerPersona.shutdown``, not the Simulator."""
        from masim.persona.general import PlayerPersona
        from masim.player.base import PlayerConfig
        from masim.player.general import GeneralPlayer

        persona_config = {
            "proxy": {
                "storage": {
                    "record_path": self.tmp_path("records"),
                    "checkpoint_dir": self.tmp_path("checkpoints"),
                    "record_rounds": True,
                    "turn_block_size": 3,
                },
                "monitoring": {
                    "record_path": self.tmp_path("monitoring"),
                    "monitor_hot_limit": 3,
                },
                "communication": {
                    "message_timeout_ms": 5000,
                    "enable_compression": True,
                },
            }
        }
        persona = PlayerPersona(
            GeneralPlayer,
            PlayerConfig(name="p", identity="p"),
            persona_config,
        )

        async def lifecycle() -> None:
            await persona.initialize()
            await persona.monitoring.record_metric("probe", 1)
            await persona.shutdown()

        asyncio.run(lifecycle())
        self.assertEqual(
            [entry["name"] for entry in read_batch_values(
                self.tmp_path("monitoring", "metrics")
            )],
            ["probe"],
        )
        self.assertEqual(
            [
                entry["event_type"]
                for entry in read_batch_values(self.tmp_path("monitoring", "events"))
            ],
            ["player_shutdown"],
        )


class TestMonitoringFlushWiring(unittest.TestCase):
    """Which side of the fix owns the flush — pinned over the source text."""

    def test_the_simulator_never_shuts_down_a_monitoring_proxy(self) -> None:
        """TODO(platform): no file under masim/simulator owns these buffers.

        ``MonitoringProxy`` is constructed inside
        ``PlayerPersona._initialize_proxies``; the run-level Simulator only
        holds Ray actor handles, so it can never flush a per-actor buffer.
        This assertion records today's division of responsibility: if the
        Simulator ever gains that responsibility (or the fix moves), this test
        must be updated deliberately rather than silently.
        """
        sources = {
            path.name: _module_source(path)
            for path in sorted(_SIMULATOR_DIR.glob("*.py"))
        }
        self.assertTrue(sources, "expected simulator sources to scan")
        offenders = [
            name
            for name, text in sources.items()
            if "MonitoringProxy" in text or _MONITORING_SHUTDOWN.search(text)
        ]
        self.assertEqual(offenders, [])

    def test_the_persona_shutdown_loop_includes_the_monitoring_proxy(self) -> None:
        """The Persona is the owner that flushes the monitoring buffer."""
        source = _module_source(_PERSONA_MODULE)
        tree = ast.parse(source)

        node = None
        for item in ast.walk(tree):
            if isinstance(item, ast.ClassDef) and item.name == "PlayerPersona":
                for method in item.body:
                    if (
                        isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and method.name == "shutdown"
                    ):
                        node = method
        self.assertIsNotNone(node, "PlayerPersona.shutdown not found")

        flushed = False
        for candidate in ast.walk(node):
            if not isinstance(candidate, ast.For):
                continue
            iterated = {
                ast.unparse(element)
                for element in (
                    candidate.iter.elts
                    if isinstance(candidate.iter, (ast.Tuple, ast.List))
                    else [candidate.iter]
                )
            }
            if "self.monitoring" not in iterated:
                continue
            for inner in ast.walk(candidate):
                if (
                    isinstance(inner, ast.Await)
                    and isinstance(inner.value, ast.Call)
                    and isinstance(inner.value.func, ast.Attribute)
                    and inner.value.func.attr == "shutdown"
                ):
                    flushed = True
        self.assertTrue(
            flushed,
            "PlayerPersona.shutdown must await the monitoring proxy shutdown",
        )
