#!/usr/bin/env python
"""HerdingInformation LLM Simulation Analysis

Usage:
    python examples/HerdingInformation/LLM/analysis.py \
        -c configs/HerdingInformation/LLM/simulation.yml
"""

from examples.HerdingInformation.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
