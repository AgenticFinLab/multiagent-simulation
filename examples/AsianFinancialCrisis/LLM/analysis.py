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
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.utils import load_config, load_results

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
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
