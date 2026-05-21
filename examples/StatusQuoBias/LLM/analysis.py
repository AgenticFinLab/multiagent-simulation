#!/usr/bin/env python
"""StatusQuoBias LLM analysis using the standard output contract."""

from __future__ import annotations

from typing import Any, Dict

from examples.StatusQuoBias.Rule.analysis import (
    calculate_metrics,
    compute_active_rebalance_volume,
    compute_agent_attribution,
    compute_default_adherence,
    compute_inertia_rate,
    compute_momentum_offset,
    compute_price_deviation,
    compute_underreaction_lag,
    create_visualizations,
    load_simulation_data,
)
from examples.standard_rule_analysis import run_standard_analysis


SCENARIO = "StatusQuoBias"
DEFAULT_CONFIG = "configs/StatusQuoBias/LLM/simulation.yml"


def main() -> Dict[str, Any]:
    """Run StatusQuoBias LLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
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
    "main",
]


if __name__ == "__main__":
    main()
