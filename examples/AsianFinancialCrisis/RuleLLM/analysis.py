#!/usr/bin/env python
"""AsianFinancialCrisis RuleLLM Simulation Analysis

RuleLLM-variant analysis for the AsianFinancialCrisis simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/AsianFinancialCrisis/RuleLLM/analysis.py \\
        -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.AsianFinancialCrisis.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_asian_financial_crisis,
    _build_interpretation,
    analyze_asian_financial_crisis,
)


def main() -> None:
    """Run full AsianFinancialCrisis RuleLLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_asian_financial_crisis().
    """
    parser = argparse.ArgumentParser(
        description="Analyze AsianFinancialCrisis RuleLLM simulation results"
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
