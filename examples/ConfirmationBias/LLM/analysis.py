#!/usr/bin/env python
"""ConfirmationBias LLM Simulation Analysis

LLM-variant analysis for the ConfirmationBias simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/ConfirmationBias/LLM/analysis.py \\
        -c configs/ConfirmationBias/LLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.ConfirmationBias.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_confirmation_bias,
    _build_interpretation,
    analyze_confirmation_bias,
)


def main() -> None:
    """Run full ConfirmationBias LLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze ConfirmationBias LLM simulation results"
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

    summary = analyze_confirmation_bias(data, config, output_dir)
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
