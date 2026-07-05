"""Local analysis compatibility helpers for AnchoringEffect.

The original scenario referenced a repo-wide ``examples.standard_rule_analysis``
module that is no longer present.  This local module provides only the small
surface AnchoringEffect uses: metric registration primitives and MASim result
loader helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Tuple


class MetricUnavailable(Exception):
    """Raised when a metric cannot be computed from the available records."""


@dataclass(frozen=True)
class Metric:
    """Registry entry for one analysis metric."""

    name: str
    category: str
    fn: Callable[[Dict[str, Any], dict], Dict[str, Any]]
    output_keys: Tuple[str, ...]
    references: Tuple[str, ...]
    description: str


class MetricsRegistry:
    """Small category-aware metric registry."""

    def __init__(self) -> None:
        self._metrics: list[Metric] = []

    def register(self, metric: Metric) -> None:
        """Register one metric, rejecting duplicate names."""
        if any(existing.name == metric.name for existing in self._metrics):
            raise ValueError(f"Duplicate metric registered: {metric.name}")
        self._metrics.append(metric)

    def by_category(self) -> Dict[str, list[Metric]]:
        """Return registered metrics grouped by category in registration order."""
        grouped: Dict[str, list[Metric]] = {}
        for metric in self._metrics:
            grouped.setdefault(metric.category, []).append(metric)
        return grouped

    def compute_all(self, data: Dict[str, Any], config: dict) -> Dict[str, Any]:
        """Compute all metrics, preserving unavailable reasons separately."""
        output: Dict[str, Any] = {}
        unavailable: Dict[str, str] = {}
        for category, metrics in self.by_category().items():
            category_output: Dict[str, Any] = {}
            for metric in metrics:
                try:
                    category_output[metric.name] = metric.fn(data, config)
                except MetricUnavailable as exc:
                    unavailable[metric.name] = str(exc)
            if category_output:
                output[category] = category_output
        output["_unavailable"] = unavailable
        return output

    def __iter__(self) -> Iterable[Metric]:
        return iter(self._metrics)


def _market_players(results) -> Dict[str, Any]:
    """Return coordinator/environment result players carrying market records."""
    candidates = results.players_by_role("coordinator")
    if candidates:
        return candidates
    candidates = results.players_by_role("environment")
    if candidates:
        return candidates
    return {
        pid: player
        for pid, player in results.players.items()
        if "market" in pid.lower() or "environment" in pid.lower()
    }


def _market_data_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract market-state dict from known MASim payload shapes."""
    if not isinstance(payload, dict):
        raise ValueError("Market payload is not a dictionary.")
    for key in ("market_data", "environment_data", "state", "observation"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    if {"price", "fundamental", "fundamental_value"}.intersection(payload):
        return payload
    decision_payload = payload.get("decision_payload")
    if isinstance(decision_payload, dict):
        return _market_data_from_payload(decision_payload)
    return {}


__all__ = [
    "Metric",
    "MetricsRegistry",
    "MetricUnavailable",
    "_market_data_from_payload",
    "_market_players",
]
