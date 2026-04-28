#!/usr/bin/env python
"""CreditCycle LLM Simulation Analysis

LLM-variant analysis for the CreditCycle simulation.
Reuses all metric/validation functions from Rule/analysis.py.
LLM-variant note (analysis-bases.md §5): stochastic LLM decisions introduce
additional variance vs. the deterministic Rule baseline; boom phases may extend
via narrative momentum.

Usage:
    python examples/CreditCycle/LLM/analysis.py \
        -c configs/CreditCycle/LLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.CreditCycle.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_credit_cycle,
    _build_interpretation,
    analyze_credit_cycle,
)


def main() -> None:
    """Run full CreditCycle LLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_credit_cycle().
    LLM-variant note: stochastic decisions may produce higher variance in
    boom amplitude and Minsky fragility timing vs. Rule baseline.
    """
    parser = argparse.ArgumentParser(
        description="Analyze CreditCycle LLM simulation results"
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

    summary = analyze_credit_cycle(data, config, output_dir)
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
