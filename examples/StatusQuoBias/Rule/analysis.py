#!/usr/bin/env python
"""StatusQuoBias Rule analysis using the standard output contract."""

from __future__ import annotations

from typing import Any, Dict

from examples.standard_rule_analysis import (
    _batch_to_rounds,
    _load_data,
    analyze_standard_scenario,
    calculate_standard_metrics,
    create_standard_visualizations,
    run_standard_analysis,
)
from masim.utils import load_results


SCENARIO = "StatusQuoBias"
DEFAULT_CONFIG = "configs/StatusQuoBias/Rule/simulation.yml"
STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_statusquobias_dynamics.png",
    "02_statusquobias_analysis.png",
    "03_summary.png",
)


def compute_inertia_rate(orders: list[dict]) -> float:
    """Fraction of hold orders. See analysis-bases.md §2.1."""
    if not orders:
        raise ValueError("orders must not be empty")
    holds = sum(1 for order in orders if order["action"] == "hold")
    return float(holds / len(orders))


def compute_default_adherence(states: list[dict]) -> float:
    """Mean closeness to default allocation. See analysis-bases.md §2.2."""
    if not states:
        raise ValueError("states must not be empty")
    gaps = [
        abs(float(state["allocation"]) - float(state["default_allocation"]))
        for state in states
    ]
    return float(1.0 - (sum(gaps) / len(gaps)))


def compute_active_rebalance_volume(orders: list[dict]) -> float:
    """Volume from active rebalancing agents. See analysis-bases.md §2.3."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            abs(int(order["quantity"]))
            for order in orders
            if "ActiveRebalancer" in order["agent_type"]
        )
    )


def compute_underreaction_lag(prices: list[float], signals: list[float]) -> int:
    """Rounds until price response follows signal direction. See analysis-bases.md §2.4."""
    if len(prices) != len(signals):
        raise ValueError("prices and signals lengths must match")
    if len(prices) < 2:
        raise ValueError("prices must contain at least two observations")
    for index in range(1, len(prices)):
        price_change = prices[index] - prices[index - 1]
        if price_change * signals[index - 1] > 0:
            return index
    raise ValueError("no signal-following price response found")


def compute_momentum_offset(orders: list[dict]) -> float:
    """Volume from momentum agents that offsets inertia. See analysis-bases.md §2.5."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            abs(int(order["quantity"]))
            for order in orders
            if "MomentumTrader" in order["agent_type"]
        )
    )


def compute_price_deviation(prices: list[float], fundamental: float) -> list[float]:
    """Price gap from fundamental by round. See analysis-bases.md §2.6."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not prices:
        raise ValueError("prices must not be empty")
    return [float((price - fundamental) / fundamental) for price in prices]


def compute_agent_attribution(orders: list[dict]) -> dict[str, float]:
    """Attribute signed order pressure by agent type. See analysis-bases.md §2.7."""
    if not orders:
        raise ValueError("orders must not be empty")
    attribution: dict[str, float] = {}
    for order in orders:
        agent_type = order["agent_type"]
        sign = 1 if order["action"] == "buy" else -1 if order["action"] == "sell" else 0
        attribution[agent_type] = attribution.get(agent_type, 0.0) + sign * int(
            order["quantity"]
        )
    return attribution


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load simulation data through `masim.utils.load_results`."""
    return _load_data(load_results(config))


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate standard structural metrics for StatusQuoBias."""
    return calculate_standard_metrics(data)


def create_visualizations(data: Dict[str, Any], output_dir: str) -> None:
    """Create fixed standard analysis PNG outputs."""
    create_standard_visualizations(SCENARIO, data, output_dir)


def analyze_statusquobias(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run metrics, validation, plots, and `summary.json` output."""
    return analyze_standard_scenario(SCENARIO, data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run StatusQuoBias Rule analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    "compute_inertia_rate",
    "compute_default_adherence",
    "compute_active_rebalance_volume",
    "compute_underreaction_lag",
    "compute_momentum_offset",
    "compute_price_deviation",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_statusquobias",
    "main",
]


if __name__ == "__main__":
    main()
