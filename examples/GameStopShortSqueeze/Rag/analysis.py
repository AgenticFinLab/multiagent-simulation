#!/usr/bin/env python
"""GameStopShortSqueeze Rag Simulation Analysis

Usage:
    python examples/GameStopShortSqueeze/Rag/analysis.py \
        -c configs/GameStopShortSqueeze/Rag/simulation.yml
"""

from examples.GameStopShortSqueeze.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
