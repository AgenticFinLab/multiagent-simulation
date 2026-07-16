#!/usr/bin/env python
"""LossAversion RuleLLM analysis using the shared behavioral contract."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

from examples.LossAversion.Rule.analysis import (
    analyze_lossaversion,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils import load_config

DEFAULT_CONFIG = "configs/LossAversion/RuleLLM/simulation.yml"


def main() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Analyze LossAversion RuleLLM results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(config["setting"]["record_path"]).parent / "analysis"
    return analyze_lossaversion(data, config, str(output_dir))


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
