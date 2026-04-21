#!/usr/bin/env python
"""ArchegosCollapse RuleLLM Simulation Analysis

Usage:
    python examples/ArchegosCollapse/RuleLLM/analysis.py \
        -c configs/ArchegosCollapse/RuleLLM/simulation.yml
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
