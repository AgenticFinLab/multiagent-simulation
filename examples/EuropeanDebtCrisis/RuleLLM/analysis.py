#!/usr/bin/env python
"""EuropeanDebtCrisis RuleLLM analysis utilities."""

from examples.EuropeanDebtCrisis.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
