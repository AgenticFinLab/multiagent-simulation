#!/usr/bin/env python
"""FlashCrash2010 LLM Simulation Analysis

Analyze the 2010 Flash Crash LLM simulation results.

Usage:
    python examples.FlashCrash2010.RuleLLM.analysis.py \
        -c configs/FlashCrash2010/LLM/simulation.yml
"""

from examples.FlashCrash2010.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    generate_summary_report,
    load_simulation_data,
    main,
)

__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "generate_summary_report",
    "main",
]

if __name__ == "__main__":
    main()
