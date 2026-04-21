#!/usr/bin/env python
"""Volmageddon LLM Simulation Analysis

Usage:
    python examples/Volmageddon/LLM/analysis.py \
        -c configs/Volmageddon/LLM/simulation.yml
"""

from examples.Volmageddon.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
