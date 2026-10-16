"""Run-level scaling metrics for the simulator.

Why this module exists
----------------------
The platform could not measure its own behaviour: ``ExecutionClock`` only kept
a total per-round duration, the actor-side ``monitoring/`` buffers were never
flushed, and no counter existed for Ray RPCs, message fan-out or memory. Any
claim of the form "this is the bottleneck at scale" was therefore unfalsifiable.

``RunMetrics`` records, once per round and with negligible overhead (wall-clock
timers, integer counters and one local RSS read):

* ``wall_ms`` / ``execute_ms`` / ``collect_ms`` / ``dispatch_ms`` — where the
  round's wall time actually goes, which is the first question when rule agents
  (microseconds) share a simulation with LLM agents (seconds);
* ``operate_calls`` / ``messages`` / ``deliveries`` / ``max_fanout`` — the
  RPC and message volume, i.e. the cost of the communication model itself;
* ``agents_active`` / ``levels`` — the shape of the round;
* ``driver_rss_mb`` — the simulator process footprint, a proxy for how much
  bookkeeping lives outside the actors.

Nothing here changes simulation behaviour; it is pure observation. Results are
written to ``<run_root>/monitoring/run_metrics.json`` next to the run's other
artifacts, with a percentile summary, so a scaling study can compare runs of
different sizes directly.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("masim.simulator.metrics")

try:  # psutil is a declared runtime dependency; stay importable without it.
    import psutil
except Exception:  # pragma: no cover - environment dependent
    psutil = None  # type: ignore[assignment]


@dataclass
class RoundMetrics:
    """Per-round observation record."""

    round: int
    wall_ms: float
    execute_ms: float
    collect_ms: float
    dispatch_ms: float
    levels: int
    agents_active: int
    operate_calls: int
    messages: int
    deliveries: int
    max_fanout: int
    driver_rss_mb: Optional[float] = None
    object_store_used_mb: Optional[float] = None
    # Shared world state: how much of the world this run is tracking.
    world_keys: int = 0
    world_scopes: int = 0
    world_version: str = ""


def _percentile(values: List[float], fraction: float) -> float:
    """Return the nearest-rank percentile of ``values`` (0.0 when empty)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    index = min(len(ordered) - 1, max(0, int(round(fraction * (len(ordered) - 1)))))
    return float(ordered[index])


@dataclass
class RunMetrics:
    """Collector for one simulation run."""

    simulation_id: str
    seed: Optional[int] = None
    total_rounds: int = 0
    n_actors: int = 0
    n_agent_classes: int = 0
    ray_gets: int = 0
    ray_objects_fetched: int = 0
    started_at: str = ""
    finished_at: str = ""
    total_wall_ms: float = 0.0
    rounds: List[RoundMetrics] = field(default_factory=list)
    _run_start: float = 0.0

    # -- lifecycle ---------------------------------------------------------

    def start_run(self) -> None:
        self._run_start = time.perf_counter()
        self.started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    def finish_run(self) -> None:
        if self._run_start:
            self.total_wall_ms = (time.perf_counter() - self._run_start) * 1000.0
        self.finished_at = time.strftime("%Y-%m-%dT%H:%M:%S")

    def note_topology_shape(self, n_actors: int, n_agent_classes: int) -> None:
        self.n_actors = n_actors
        self.n_agent_classes = n_agent_classes

    def note_ray_get(self, n_objects: int = 0) -> None:
        """Record one ``ray.get`` round-trip and how many objects it collected."""
        self.ray_gets += 1
        self.ray_objects_fetched += max(0, int(n_objects))

    def record_round(self, record: RoundMetrics) -> None:
        self.rounds.append(record)

    # -- reporting ---------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return totals plus per-round percentiles, ready for JSON."""
        wall = [r.wall_ms for r in self.rounds]
        execute = [r.execute_ms for r in self.rounds]
        collect = [r.collect_ms for r in self.rounds]
        dispatch = [r.dispatch_ms for r in self.rounds]
        return {
            "simulation_id": self.simulation_id,
            "seed": self.seed,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "n_actors": self.n_actors,
            "n_agent_classes": self.n_agent_classes,
            "n_rounds": len(self.rounds),
            "total_rounds_configured": self.total_rounds,
            "total_wall_ms": round(self.total_wall_ms, 3),
            "ray_gets": self.ray_gets,
            "ray_objects_fetched": self.ray_objects_fetched,
            "world": {
                "keys": self.rounds[-1].world_keys if self.rounds else 0,
                "scopes": self.rounds[-1].world_scopes if self.rounds else 0,
                "version": self.rounds[-1].world_version if self.rounds else "",
            },
            "totals": {
                "operate_calls": sum(r.operate_calls for r in self.rounds),
                "messages": sum(r.messages for r in self.rounds),
                "deliveries": sum(r.deliveries for r in self.rounds),
                "levels": sum(r.levels for r in self.rounds),
            },
            "per_round_ms": {
                "wall": {
                    "p50": round(_percentile(wall, 0.50), 3),
                    "p95": round(_percentile(wall, 0.95), 3),
                    "max": round(max(wall), 3) if wall else 0.0,
                },
                "execute": {
                    "p50": round(_percentile(execute, 0.50), 3),
                    "p95": round(_percentile(execute, 0.95), 3),
                    "max": round(max(execute), 3) if execute else 0.0,
                },
                "collect": {
                    "p50": round(_percentile(collect, 0.50), 3),
                    "p95": round(_percentile(collect, 0.95), 3),
                    "max": round(max(collect), 3) if collect else 0.0,
                },
                "dispatch": {
                    "p50": round(_percentile(dispatch, 0.50), 3),
                    "p95": round(_percentile(dispatch, 0.95), 3),
                    "max": round(max(dispatch), 3) if dispatch else 0.0,
                },
            },
            "peak": {
                "agents_active": max((r.agents_active for r in self.rounds), default=0),
                "max_fanout": max((r.max_fanout for r in self.rounds), default=0),
                # ``is not None`` rather than truthiness: a measured 0.0 is a
                # real observation and must not be reported as "not sampled".
                "driver_rss_mb": max(
                    (
                        r.driver_rss_mb
                        for r in self.rounds
                        if r.driver_rss_mb is not None
                    ),
                    default=None,
                ),
                "object_store_used_mb": max(
                    (
                        r.object_store_used_mb
                        for r in self.rounds
                        if r.object_store_used_mb is not None
                    ),
                    default=None,
                ),
            },
        }

    def log_summary(self) -> None:
        """Emit a one-line-per-round and a summary block to the run log."""
        if not self.rounds:
            return
        logger.info("    Scaling metrics (per round):")
        logger.info(
            "      %-6s %9s %9s %9s %9s %8s %8s %8s",
            "round", "wall_ms", "exec_ms", "coll_ms", "disp_ms", "ops", "msgs", "agents",
        )
        for r in self.rounds:
            logger.info(
                "      %-6d %9.1f %9.1f %9.1f %9.1f %8d %8d %8d",
                r.round, r.wall_ms, r.execute_ms, r.collect_ms, r.dispatch_ms,
                r.operate_calls, r.messages, r.agents_active,
            )
        s = self.summary()
        totals = s["totals"]
        logger.info(
            "    Totals: rounds=%d agents=%d operate=%d messages=%d deliveries=%d "
            "ray_gets=%d wall=%.1fms",
            s["n_rounds"], s["n_actors"], totals["operate_calls"], totals["messages"],
            totals["deliveries"], s["ray_gets"], s["total_wall_ms"],
        )

    def write(self, path: str) -> bool:
        """Persist ``{summary, rounds}`` as JSON. Never raises."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            payload = {
                "summary": self.summary(),
                "rounds": [asdict(r) for r in self.rounds],
            }
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
            logger.info("    Scaling metrics written to %s", path)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not write scaling metrics to %s: %s", path, exc)
            return False

    # -- sampling helpers --------------------------------------------------

    @staticmethod
    def driver_rss_mb() -> Optional[float]:
        """Resident set size of this process in MiB (None when unavailable)."""
        if psutil is None:
            return None
        try:
            return round(psutil.Process().memory_info().rss / (1024.0 * 1024.0), 2)
        except Exception:  # pragma: no cover - defensive
            return None

    @staticmethod
    def object_store_used_mb() -> Optional[float]:
        """Object-store bytes in use, derived from Ray's own accounting."""
        try:
            import ray

            if not ray.is_initialized():
                return None
            total = ray.cluster_resources().get("object_store_memory", 0)
            available = ray.available_resources().get("object_store_memory", 0)
            used = max(0.0, float(total) - float(available))
            return round(used / (1024.0 * 1024.0), 2)
        except Exception:  # pragma: no cover - defensive
            return None
