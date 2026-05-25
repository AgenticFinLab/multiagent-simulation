#!/usr/bin/env python
"""LUNACollapse LLM analysis using the scenario output contract."""

from examples.standard_rule_analysis import run_standard_analysis

from examples.LUNACollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)

SCENARIO = "LUNACollapse"
DEFAULT_CONFIG = "configs/LUNACollapse/LLM/simulation.yml"


def main():
    """Run LLM analysis with an LLM-specific default config."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
