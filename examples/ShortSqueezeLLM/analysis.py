"""ShortSqueezeLLM Analysis - Supply-Demand Imbalance Evaluation (LLM Version)

Analyzes short squeeze dynamics in LLM-driven agents.
Uses same methodology as rule-based ShortSqueeze.

Usage:
    python examples/ShortSqueezeLLM/analysis.py -c configs/ShortSqueezeLLM/simulation.yml

See examples/ShortSqueeze/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

from masim.utils import load_config

# Import from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ShortSqueeze.analysis import (
    load_simulation_data,
    calculate_squeeze_metrics,
    identify_squeeze_phases,
    plot_squeeze_analysis,
    generate_summary,
)


def main():
    """Run squeeze analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze ShortSqueezeLLM simulation")
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
    print("ShortSqueezeLLM Analysis - Supply-Demand Imbalance (LLM Agents)")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")

    # Calculate squeeze metrics
    print("\n[2] Calculating squeeze metrics...")
    squeeze_metrics = calculate_squeeze_metrics(data["prices"], data["trades"])

    # Identify phases
    print("\n[3] Identifying squeeze phases...")
    phases = identify_squeeze_phases(data["prices"])

    # Generate plots
    print("\n[4] Generating plots...")
    plot_squeeze_analysis(data, squeeze_metrics, phases, output_dir)
    print(f"    Saved to {output_dir}/")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, squeeze_metrics, phases)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    return summary


if __name__ == "__main__":
    main()
