#!/usr/bin/env python
"""GameStopShortSqueeze LLM Simulation Analysis

Usage:
    python examples/GameStopShortSqueeze/LLM/analysis.py \
        -c configs/GameStopShortSqueeze/LLM/simulation.yml
"""

from examples.GameStopShortSqueeze.Rule.analysis import (
    SCENARIO,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from examples.standard_rule_analysis import run_standard_analysis

DEFAULT_CONFIG = "configs/GameStopShortSqueeze/LLM/simulation.yml"


def main():
    """Run GameStopShortSqueeze LLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
