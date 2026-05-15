#!/usr/bin/env python
"""MentalAccounting LLM Simulation Analysis

Usage:
    python examples/MentalAccounting/LLM/analysis.py \
        -c configs/MentalAccounting/LLM/simulation.yml
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
