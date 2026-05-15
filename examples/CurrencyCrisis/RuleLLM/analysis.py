#!/usr/bin/env python
"""CurrencyCrisis RuleLLM Simulation Analysis

RuleLLM-variant analysis for the CurrencyCrisis simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/CurrencyCrisis/RuleLLM/analysis.py \
        -c configs/CurrencyCrisis/RuleLLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.CurrencyCrisis.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_currency_crisis,
    _build_interpretation,
    analyze_currency_crisis,
)


def main() -> None:
    """Run full CurrencyCrisis RuleLLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze CurrencyCrisis RuleLLM simulation results"
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

    summary = analyze_currency_crisis(data, config, output_dir)

    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
