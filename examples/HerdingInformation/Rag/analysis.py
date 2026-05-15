#!/usr/bin/env python
"""HerdingInformation Rag Simulation Analysis

Usage:
    python examples/HerdingInformation/Rag/analysis.py \
        -c configs/HerdingInformation/Rag/simulation.yml
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
