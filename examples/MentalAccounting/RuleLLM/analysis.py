#!/usr/bin/env python
"""MentalAccounting RuleLLM Simulation Analysis

Usage:
    python examples/MentalAccounting/RuleLLM/analysis.py \
        -c configs/MentalAccounting/RuleLLM/simulation.yml
"""

from examples.MentalAccounting.Rule.analysis import (
    SCENARIO,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    run_standard_analysis,
)

DEFAULT_CONFIG = "configs/MentalAccounting/RuleLLM/simulation.yml"


def main():
    """Run MentalAccounting RuleLLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
