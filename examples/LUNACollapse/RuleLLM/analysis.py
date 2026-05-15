#!/usr/bin/env python
"""LUNACollapse RuleLLM Simulation Analysis

Usage:
    python examples/LUNACollapse/RuleLLM/analysis.py \
        -c configs/LUNACollapse/RuleLLM/simulation.yml
"""

from examples.LUNACollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
