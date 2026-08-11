#!/usr/bin/env python
"""OverconfidenceBias LLM analysis using the standard output contract."""

from __future__ import annotations

import argparse
from typing import Any, Dict

from examples.OverconfidenceBias.Rule.analysis import (
    SCENARIO,
    analyze_overconfidencebias,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils import load_config
from masim.evaluation.llm_harness import finalize_llm_analysis

DEFAULT_CONFIG = "configs/OverconfidenceBias/LLM/simulation.yml"


def main(config_path: str | None = None) -> Dict[str, Any]:
    """Run OverconfidenceBias LLM analysis."""
    if config_path is None:
        parser = argparse.ArgumentParser(description="OverconfidenceBias LLM analysis")
        parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
        args = parser.parse_args()
        config_path = args.config
    config = load_config(config_path)
    data = load_simulation_data(config)
    output_dir = config["setting"]["record_path"].rsplit("/", 1)[0] + "/analysis"
    summary = analyze_overconfidencebias(data, config, output_dir)
    finalize_llm_analysis(
        data, config, output_dir, "OverconfidenceBias", summary,
        config_path=config_path,
    )
    return summary


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
