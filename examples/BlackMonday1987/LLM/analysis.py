#!/usr/bin/env python
"""BlackMonday1987 LLM Simulation Analysis

LLM-variant analysis for the BlackMonday1987 simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §4): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline.

Usage:
    python examples/BlackMonday1987/LLM/analysis.py \\
        -c configs/BlackMonday1987/LLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.BlackMonday1987.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_black_monday,
    _build_interpretation,
    analyze_black_monday,
)


def main() -> None:
    """Run full BlackMonday1987 LLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_black_monday().
    LLM-variant note: stochastic decisions may produce higher variance in
    drawdown depth and crash timing vs. Rule baseline.
    """
    parser = argparse.ArgumentParser(
        description="Analyze BlackMonday1987 LLM simulation results"
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

    summary = analyze_black_monday(data, config, output_dir)
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
