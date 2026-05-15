#!/usr/bin/env python
"""LUNACollapse LLM Simulation Analysis

Usage:
    python examples/LUNACollapse/LLM/analysis.py \
        -c configs/LUNACollapse/LLM/simulation.yml
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
