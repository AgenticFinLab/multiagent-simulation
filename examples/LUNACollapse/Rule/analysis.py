#!/usr/bin/env python
"""LUNACollapse Rule analysis using the standard output contract."""

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


SCENARIO = "LUNACollapse"
DEFAULT_CONFIG = "configs/LUNACollapse/Rule/simulation.yml"
STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_lunacollapse_dynamics.png",
    "02_lunacollapse_analysis.png",
    "03_summary.png",
)


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load simulation data through `masim.utils.load_results`."""
    results = load_results(config)
    data = _load_data(results)
    rag_contexts: Dict[str, Dict[int, Any]] = {}
    for pid, player in results.players_by_role("player").items():
        contexts = player.turns.field("rag_context")
        if contexts:
            rag_contexts[pid] = contexts
    data["rag_contexts"] = rag_contexts
    return data


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate standard structural metrics."""
    return calculate_standard_metrics(data)


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Create fixed standard analysis PNG outputs."""
    create_standard_visualizations(SCENARIO, data, output_path)


def analyze_lunacollapse(data: Dict[str, Any], config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Run metrics, validation, plots, and `summary.json` output."""
    return analyze_standard_scenario(SCENARIO, data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run LUNACollapse analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_lunacollapse",
    "STANDARD_OUTPUT_FILES",
    "main",
]


if __name__ == "__main__":
    main()
