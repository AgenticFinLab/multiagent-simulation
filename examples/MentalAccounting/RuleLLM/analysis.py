#!/usr/bin/env python
"""MentalAccounting RuleLLM Simulation Analysis

Usage:
    python examples/MentalAccounting/RuleLLM/analysis.py \
        -c configs/MentalAccounting/RuleLLM/simulation.yml
"""

from examples.MentalAccounting.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
