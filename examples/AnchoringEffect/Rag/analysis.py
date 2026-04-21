#!/usr/bin/env python
"""AnchoringEffect Rag Simulation Analysis

Usage:
    python examples/AnchoringEffect/Rag/analysis.py \
        -c configs/AnchoringEffect/Rag/simulation.yml
"""

from examples.AnchoringEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
