#!/usr/bin/env python
"""EuropeanDebtCrisis RuleLLM analysis — thin re-export of Rule pipeline.

RuleLLM embeds Rule thresholds into the LLM prompt while keeping the
Rule decision logic; therefore its analysis is identical to Rule's.
See ``examples/EuropeanDebtCrisis/RuleLLM/analysis.md`` for cross-variant
comparison notes.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

from examples.EuropeanDebtCrisis.Rule.analysis import (
    SCENARIO,
    STANDARD_OUTPUT_FILES,
    analyze_europeandebtcrisis,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_european_debt_crisis,
)
from masim.utils import load_config


DEFAULT_CONFIG = "configs/EuropeanDebtCrisis/RuleLLM/simulation.yml"


def main() -> Dict[str, Any]:
    """Run the shared Rule analysis pipeline for a RuleLLM configuration."""
    parser = argparse.ArgumentParser(
        description="Analyze EuropeanDebtCrisis RuleLLM results"
    )
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)
    return analyze_europeandebtcrisis(config, output_dir)


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    "load_simulation_data",
    "calculate_metrics",
    "validate_european_debt_crisis",
    "create_visualizations",
    "analyze_europeandebtcrisis",
    "main",
]


if __name__ == "__main__":
    main()
