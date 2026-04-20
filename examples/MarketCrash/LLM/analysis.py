"""MarketCrashLLM Analysis - Panic Selling Cascade Evaluation (LLM Version)

Analyzes market crash dynamics in LLM-driven agents.
Uses same methodology as rule-based MarketCrash.

Usage:
    python examples/MarketCrash/LLM/analysis.py -c configs/MarketCrash/LLM/simulation.yml

See examples/MarketCrash/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.MarketCrash.Rule.analysis import (
    _load_data,
    analyze_crash,
)


def main():
    """Run crash analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze MarketCrashLLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    # Load config and derive paths
    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("MarketCrashLLM Analysis - Panic Selling Cascade (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
