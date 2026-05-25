#!/usr/bin/env python
"""SunkCostFallacy Rule analysis using the standard output contract."""

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


SCENARIO = "SunkCostFallacy"
DEFAULT_CONFIG = "configs/SunkCostFallacy/Rule/simulation.yml"
STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_sunkcostfallacy_dynamics.png",
    "02_sunkcostfallacy_analysis.png",
    "03_summary.png",
)


def compute_losing_holding_rate(positions: list[dict]) -> float:
    """Hold frequency for losing positions. See analysis-bases.md §2.1."""
    if not positions:
        raise ValueError("positions must not be empty")
    losing = [row for row in positions if float(row["unrealized_return"]) < 0]
    if not losing:
        raise ValueError("positions contain no losing observations")
    holds = sum(1 for row in losing if row["action"] == "hold")
    return float(holds / len(losing))


def compute_escalation_volume(orders: list[dict]) -> float:
    """Additional buy volume by escalation agents. See analysis-bases.md §2.2."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            abs(int(order["quantity"]))
            for order in orders
            if "CommitmentEscalator" in order["agent_type"]
            and order["action"] == "buy"
        )
    )


def compute_rational_cut_volume(orders: list[dict]) -> float:
    """Valuation-based trade volume by rational cutters. See analysis-bases.md §2.3."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            abs(int(order["quantity"]))
            for order in orders
            if "RationalCutter" in order["agent_type"]
        )
    )


def compute_opportunity_reallocation(orders: list[dict]) -> float:
    """Opportunity-cost reallocation volume. See analysis-bases.md §2.4."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            abs(int(order["quantity"]))
            for order in orders
            if "OpportunityCostTrader" in order["agent_type"]
        )
    )


def compute_performance_drag(agent_values: dict[str, list[float]]) -> float:
    """Performance gap between biased and rational agents. See analysis-bases.md §2.5."""
    if "biased" not in agent_values or "rational" not in agent_values:
        raise ValueError("agent_values must contain biased and rational series")
    biased = agent_values["biased"]
    rational = agent_values["rational"]
    if not biased or not rational:
        raise ValueError("agent value series must not be empty")
    rational_final = float(rational[-1])
    if rational_final == 0:
        raise ValueError("rational final value must not be zero")
    return float((rational_final - float(biased[-1])) / rational_final)


def compute_loss_onset(prices: list[float], cost_basis: float) -> int:
    """First round where price falls below cost basis. See analysis-bases.md §2.6."""
    if cost_basis <= 0:
        raise ValueError("cost_basis must be positive")
    if not prices:
        raise ValueError("prices must not be empty")
    for index, price in enumerate(prices, start=1):
        if price < cost_basis:
            return index
    raise ValueError("no loss onset found")


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
    """Calculate standard structural metrics for SunkCostFallacy."""
    return calculate_standard_metrics(data)


def create_visualizations(data: Dict[str, Any], output_dir: str) -> None:
    """Create fixed standard analysis PNG outputs."""
    create_standard_visualizations(SCENARIO, data, output_dir)


def analyze_sunkcostfallacy(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run metrics, validation, plots, and `summary.json` output."""
    return analyze_standard_scenario(SCENARIO, data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run SunkCostFallacy Rule analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    "compute_losing_holding_rate",
    "compute_escalation_volume",
    "compute_rational_cut_volume",
    "compute_opportunity_reallocation",
    "compute_performance_drag",
    "compute_loss_onset",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_sunkcostfallacy",
    "main",
]


if __name__ == "__main__":
    main()
