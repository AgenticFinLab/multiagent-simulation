#!/usr/bin/env python
"""SVBBankRun LLM Simulation Analysis

Usage:
    python examples/SVBBankRun/LLM/analysis.py \
        -c configs/SVBBankRun/LLM/simulation.yml
"""

from examples.SVBBankRun.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
