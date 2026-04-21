#!/usr/bin/env python
"""LossAversion LLM Simulation Analysis

Usage:
    python examples/LossAversion/LLM/analysis.py \
        -c configs/LossAversion/LLM/simulation.yml
"""

from examples.LossAversion.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
