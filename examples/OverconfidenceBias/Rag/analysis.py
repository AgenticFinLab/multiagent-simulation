#!/usr/bin/env python
"""OverconfidenceBias Rag Simulation Analysis

Usage:
    python examples/OverconfidenceBias/Rag/analysis.py \
        -c configs/OverconfidenceBias/Rag/simulation.yml
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
