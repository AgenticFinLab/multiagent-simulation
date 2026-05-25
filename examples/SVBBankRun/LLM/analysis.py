#!/usr/bin/env python
"""SVBBankRun LLM analysis using the standard output contract."""

from __future__ import annotations

from typing import Any, Dict

from examples.standard_rule_analysis import run_standard_analysis
from examples.SVBBankRun.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)

SCENARIO = "SVBBankRun"
DEFAULT_CONFIG = "configs/SVBBankRun/LLM/simulation.yml"


def main() -> Dict[str, Any]:
    """Run SVBBankRun LLM analysis."""
    return run_standard_analysis(SCENARIO, DEFAULT_CONFIG)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]

if __name__ == "__main__":
    main()
