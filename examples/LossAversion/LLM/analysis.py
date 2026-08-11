#!/usr/bin/env python
"""LossAversion LLM analysis using the shared behavioral contract."""

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
from masim.evaluation.llm_harness import finalize_llm_analysis

DEFAULT_CONFIG = "configs/LossAversion/LLM/simulation.yml"


def main() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Analyze LossAversion LLM results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(config["setting"]["record_path"]).parent / "analysis"
    summary = analyze_lossaversion(data, config, str(output_dir))
    finalize_llm_analysis(
        data, config, str(output_dir), "LossAversion", summary,
        config_path=args.config,
    )
    return summary


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
