#!/usr/bin/env python
"""LTCMCollapse RuleLLM analysis using the scenario output contract."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from examples.LTCMCollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_metrics,
)
from masim.utils import load_config

DEFAULT_CONFIG = "configs/LTCMCollapse/RuleLLM/simulation.yml"


def main() -> None:
    """Run RuleLLM analysis with a RuleLLM-specific default config."""
    parser = argparse.ArgumentParser(description="Analyze LTCMCollapse RuleLLM results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)
    validation = validate_metrics(metrics)
    analysis_path = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    create_visualizations(data, str(analysis_path))
    from examples.LTCMCollapse.Rule.analysis import _write_summary

    _write_summary(analysis_path, metrics, validation)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
