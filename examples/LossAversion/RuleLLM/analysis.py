#!/usr/bin/env python
"""LossAversion RuleLLM Simulation Analysis

Usage:
    python examples/LossAversion/RuleLLM/analysis.py \
        -c configs/LossAversion/RuleLLM/simulation.yml
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
