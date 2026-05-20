#!/usr/bin/env python
"""MentalAccounting Rule analysis using the standard output contract."""

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


SCENARIO = "MentalAccounting"
DEFAULT_CONFIG = "configs/MentalAccounting/Rule/simulation.yml"
STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_mentalaccounting_dynamics.png",
    "02_mentalaccounting_analysis.png",
    "03_summary.png",
)


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load simulation data through `masim.utils.load_results`."""
    return _load_data(load_results(config))


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate standard structural metrics."""
    return calculate_standard_metrics(data)


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Create fixed standard analysis PNG outputs."""
    create_standard_visualizations(SCENARIO, data, output_path)


def analyze_mentalaccounting(data: Dict[str, Any], config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Run metrics, validation, plots, and `summary.json` output."""
    return analyze_standard_scenario(SCENARIO, data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run MentalAccounting analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_mentalaccounting",
    "STANDARD_OUTPUT_FILES",
    "main",
]


if __name__ == "__main__":
    main()
