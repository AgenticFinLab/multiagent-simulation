#!/usr/bin/env python
"""DotComBubble Rag Simulation Analysis

Usage:
    python examples/DotComBubble/Rag/analysis.py \
        -c configs/DotComBubble/Rag/simulation.yml
"""

from examples.DotComBubble.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
