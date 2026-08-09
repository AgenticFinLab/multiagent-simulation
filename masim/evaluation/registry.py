"""Evaluation Registry — Metric type system and registry infrastructure.

Provides the core types used by scenario-specific metric catalogues:
- Metric: A named, categorized metric definition with computation function
- MetricsRegistry: A registry that collects Metric instances and batch-computes them
- MetricUnavailable: Exception raised when a metric cannot be computed due to missing data

Usage:
    from masim.evaluation.registry import Metric, MetricsRegistry, MetricUnavailable

    REGISTRY = MetricsRegistry()

    def m_max_drawdown(data, config):
        prices = data.get("market_prices")
        if not prices:
            raise MetricUnavailable("market_prices not available")
        # ... compute ...
        return {"max_drawdown_pct": max_dd}

    REGISTRY.register(Metric(
        name="max_drawdown",
        category="price_dynamics",
        fn=m_max_drawdown,
        output_keys=("max_drawdown_pct",),
        references=("Shiller 2000",),
        description="Maximum peak-to-trough decline as percentage",
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


class MetricUnavailable(Exception):
    """Raised when a metric cannot be computed due to missing input data.

    Analysis drivers should catch this and skip the metric gracefully,
    recording it as unavailable in the output summary.
    """

    pass


@dataclass(frozen=True)
class Metric:
    """A single named metric definition.

    Parameters
    ----------
    name : str
        Unique identifier for the metric (e.g., "mad_pct", "max_drawdown").
    category : str
        Grouping category (e.g., "price_dynamics", "behavioral", "microstructure").
    fn : Callable[[Dict, Dict], Dict]
        The computation function. Signature: fn(data, config) -> dict.
        Must raise MetricUnavailable if required inputs are not present.
    output_keys : tuple of str
        Keys that fn's return dict is expected to contain.
    references : tuple of str, optional
        Academic references (e.g., ("Odean 1998", "Shiller 2000")).
    description : str, optional
        Human-readable description of what the metric measures.
    """

    name: str
    category: str
    fn: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    output_keys: Tuple[str, ...] = ()
    references: Tuple[str, ...] = ()
    description: str = ""


class MetricsRegistry:
    """Registry that collects Metric instances and batch-computes them.

    Provides:
    - register(metric): Add a metric to the registry.
    - compute_all(data, config): Execute all registered metrics and return results.
    - categories(): List unique categories.
    - metrics_in_category(category): List metrics in a given category.
    """

    def __init__(self) -> None:
        self._metrics: List[Metric] = []
        self._by_name: Dict[str, Metric] = {}
        self._by_category: Dict[str, List[Metric]] = {}

    def register(self, metric: Metric) -> None:
        """Register a metric. Raises ValueError on duplicate names."""
        if metric.name in self._by_name:
            raise ValueError(
                f"Metric '{metric.name}' is already registered. "
                f"Use a unique name for each metric."
            )
        self._metrics.append(metric)
        self._by_name[metric.name] = metric
        self._by_category.setdefault(metric.category, []).append(metric)

    def compute_all(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute all registered metrics and return combined results.

        Returns
        -------
        dict with keys:
            "metrics": {metric_name: {output_key: value, ...}}
            "unavailable": [metric_name, ...]
            "errors": {metric_name: str}
        """
        metrics_output: Dict[str, Dict[str, Any]] = {}
        unavailable: List[str] = []
        errors: Dict[str, str] = {}

        for metric in self._metrics:
            try:
                result = metric.fn(data, config)
                metrics_output[metric.name] = result
            except MetricUnavailable as e:
                unavailable.append(metric.name)
                metrics_output[metric.name] = {"_unavailable": str(e)}
            except Exception as e:
                errors[metric.name] = f"{type(e).__name__}: {e}"
                metrics_output[metric.name] = {"_error": str(e)}

        return {
            "metrics": metrics_output,
            "unavailable": unavailable,
            "errors": errors,
        }

    def categories(self) -> List[str]:
        """Return list of unique category names."""
        return list(self._by_category.keys())

    def metrics_in_category(self, category: str) -> List[Metric]:
        """Return metrics registered under the given category."""
        return list(self._by_category.get(category, []))

    def get(self, name: str) -> Optional[Metric]:
        """Look up a metric by name. Returns None if not found."""
        return self._by_name.get(name)

    @property
    def metric_names(self) -> List[str]:
        """Return ordered list of all registered metric names."""
        return [m.name for m in self._metrics]

    def __len__(self) -> int:
        return len(self._metrics)

    def __repr__(self) -> str:
        cats = ", ".join(f"{cat}({len(ms)})" for cat, ms in self._by_category.items())
        return f"MetricsRegistry({len(self._metrics)} metrics: {cats})"
