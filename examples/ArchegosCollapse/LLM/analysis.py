#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Analysis

Usage:
    python examples/ArchegosCollapse/LLM/analysis.py \
        -c configs/ArchegosCollapse/LLM/simulation.yml
"""

from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
