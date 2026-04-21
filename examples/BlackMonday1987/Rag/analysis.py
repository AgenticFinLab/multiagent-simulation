#!/usr/bin/env python
"""BlackMonday1987 Rag Simulation Analysis

Usage:
    python examples/BlackMonday1987/Rag/analysis.py \
        -c configs/BlackMonday1987/Rag/simulation.yml
"""

from examples.BlackMonday1987.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
