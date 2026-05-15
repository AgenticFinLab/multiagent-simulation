#!/usr/bin/env python
"""DotComBubble RuleLLM Simulation Analysis

Usage:
    python examples/DotComBubble/RuleLLM/analysis.py \
        -c configs/DotComBubble/RuleLLM/simulation.yml
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
