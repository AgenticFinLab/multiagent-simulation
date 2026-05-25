#!/usr/bin/env python
"""SunkCostFallacy LLM analysis using the standard output contract."""

from __future__ import annotations

from typing import Any, Dict

from examples.SunkCostFallacy.Rule.analysis import (
    calculate_metrics,
    compute_agent_attribution,
    compute_escalation_volume,
    compute_losing_holding_rate,
    compute_loss_onset,
    compute_opportunity_reallocation,
    compute_performance_drag,
    compute_rational_cut_volume,
    create_visualizations,
    load_simulation_data,
)
from examples.standard_rule_analysis import run_standard_analysis


SCENARIO = "SunkCostFallacy"
DEFAULT_CONFIG = "configs/SunkCostFallacy/LLM/simulation.yml"


def main() -> Dict[str, Any]:
    """Run SunkCostFallacy LLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
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
    "main",
]


if __name__ == "__main__":
    main()
