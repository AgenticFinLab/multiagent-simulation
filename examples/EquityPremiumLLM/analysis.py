"""EquityPremiumLLM Analysis - Myopic Loss Aversion Evaluation (LLM Version)

Analyzes equity premium puzzle in LLM-driven agents.
Uses same methodology as rule-based EquityPremium.

Usage:
    python examples/EquityPremiumLLM/analysis.py -c configs/EquityPremiumLLM/simulation.yml

See examples/EquityPremium/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

import numpy as np

from masim.utils import load_config

# Import from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from EquityPremium.analysis import (
    load_simulation_data,
    calculate_equity_premium,
    calculate_loss_probability,
    analyze_investor_allocations,
    plot_equity_premium_analysis,
    generate_summary,
)


def main():
    """Run equity premium analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze EquityPremiumLLM simulation")
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
    print("EquityPremiumLLM Analysis - Myopic Loss Aversion (LLM Agents)")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")

    # Calculate equity premium
    print("\n[2] Calculating equity premium...")
    premium_metrics = calculate_equity_premium(data["prices"], len(data["prices"]))

    # Calculate loss probability by horizon
    print("\n[3] Calculating loss probability by horizon...")
    horizons = [1, 5, 10, 20, 50, 100]
    horizons = [h for h in horizons if h < len(data["prices"])]
    loss_probs = calculate_loss_probability(data["prices"], horizons)

    # Analyze investor allocations
    print("\n[4] Analyzing investor allocations...")
    allocations = analyze_investor_allocations(data["trades"])

    # Generate plots
    print("\n[5] Generating plots...")
    plot_equity_premium_analysis(
        data, premium_metrics, loss_probs, allocations, output_dir
    )
    print(f"    Saved to {output_dir}/")

    # Generate summary
    print("\n[6] Generating summary...")
    summary = generate_summary(data, premium_metrics, loss_probs, allocations)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            summary,
            f,
            indent=2,
            default=lambda x: (
                int(x)
                if isinstance(x, (np.bool_, np.integer))
                else float(x) if isinstance(x, np.floating) else str(x)
            ),
        )
    print(f"    Saved to {summary_path}")

    return summary


if __name__ == "__main__":
    main()
