#!/usr/bin/env python
"""AvailabilityBias LLM Simulation Analysis

LLM-variant analysis for the AvailabilityBias simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §4): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline.

Usage:
    python examples/AvailabilityBias/LLM/analysis.py \\
        -c configs/AvailabilityBias/LLM/simulation.yml
"""

import argparse
import json
import os

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution

from examples.AvailabilityBias.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_availability_bias,
    _build_interpretation,
    analyze_availability_bias,
)


def main() -> None:
    """Run full AvailabilityBias LLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_availability_bias().
    LLM-variant note: stochastic decisions may produce higher variance in
    bias episode depth and persistence vs. Rule baseline.
    """
    parser = argparse.ArgumentParser(
        description="Analyze AvailabilityBias LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)

    summary = analyze_availability_bias(data, config, output_dir)

    action_dist = analyze_action_distribution(results)
    summary_path = os.path.join(output_dir, "summary.json")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            persisted = json.load(f)
    except (OSError, ValueError):
        persisted = summary if isinstance(summary, dict) else {}
    persisted["llm_action_distribution"] = action_dist
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(persisted, f, indent=2, default=str)
    if isinstance(summary, dict):
        summary["llm_action_distribution"] = action_dist
    return summary


__all__ = ["analyze_action_distribution", "main"]

if __name__ == "__main__":
    main()
