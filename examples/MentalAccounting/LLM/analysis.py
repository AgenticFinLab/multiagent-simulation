#!/usr/bin/env python
"""MentalAccounting LLM Simulation Analysis

Usage:
    python examples/MentalAccounting/LLM/analysis.py \
        -c configs/MentalAccounting/LLM/simulation.yml
"""

from examples.MentalAccounting.Rule.analysis import (
    SCENARIO,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    run_standard_analysis,
)

DEFAULT_CONFIG = "configs/MentalAccounting/LLM/simulation.yml"


def main():
    """Run MentalAccounting LLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
