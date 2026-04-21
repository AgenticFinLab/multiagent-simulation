#!/usr/bin/env python
"""LTCMCollapse LLM Simulation Analysis

Usage:
    python examples/LTCMCollapse/LLM/analysis.py \
        -c configs/LTCMCollapse/LLM/simulation.yml
"""

from examples.LTCMCollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
