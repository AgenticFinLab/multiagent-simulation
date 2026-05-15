#!/usr/bin/env python
"""OverconfidenceBias LLM Simulation Analysis

Usage:
    python examples/OverconfidenceBias/LLM/analysis.py \
        -c configs/OverconfidenceBias/LLM/simulation.yml
"""

from examples.OverconfidenceBias.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
