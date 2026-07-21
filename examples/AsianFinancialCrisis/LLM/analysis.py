#!/usr/bin/env python
"""AsianFinancialCrisis LLM Simulation Analysis

LLM-variant analysis for the AsianFinancialCrisis simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §4): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline.

Usage:
    python examples/AsianFinancialCrisis/LLM/analysis.py \\
        -c configs/AsianFinancialCrisis/LLM/simulation.yml
"""

import argparse
import json
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution

from examples.AsianFinancialCrisis.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_asian_financial_crisis,
    _build_interpretation,
    analyze_asian_financial_crisis,
)


def main() -> None:
    """Run full AsianFinancialCrisis LLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_asian_financial_crisis().
    LLM-variant note: stochastic decisions may produce higher variance in
    crisis depth and onset timing vs. Rule baseline.
    """
    parser = argparse.ArgumentParser(
        description="Analyze AsianFinancialCrisis LLM simulation results"
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

    summary = analyze_asian_financial_crisis(data, config, output_dir)

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
