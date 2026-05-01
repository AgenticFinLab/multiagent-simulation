#!/usr/bin/env python
"""CarryTradeUnwind RuleLLM Simulation Analysis

RuleLLM-variant analysis for the CarryTradeUnwind simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/CarryTradeUnwind/RuleLLM/analysis.py \\
        -c configs/CarryTradeUnwind/RuleLLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.CarryTradeUnwind.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_carry_trade_unwind,
    _build_interpretation,
    analyze_carry_trade_unwind,
)


def main() -> None:
    """Run full CarryTradeUnwind RuleLLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze CarryTradeUnwind RuleLLM simulation results"
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

    summary = analyze_carry_trade_unwind(data, config, output_dir)

    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
