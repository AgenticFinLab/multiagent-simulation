#!/usr/bin/env python
"""GFC2008 RuleLLM Simulation Analysis

Usage:
    python examples/GFC2008/RuleLLM/analysis.py \
        -c configs/GFC2008/RuleLLM/simulation.yml
"""

from examples.GFC2008.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
