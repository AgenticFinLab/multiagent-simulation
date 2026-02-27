"""LiquidityDryupLLM Analysis - Market Maker Inventory Model Evaluation (LLM Version)

Analyzes liquidity dry-up dynamics in LLM-driven agents.
Uses same methodology as rule-based LiquidityDryup.

Usage:
    python examples/LiquidityDryupLLM/analysis.py -c configs/LiquidityDryupLLM/simulation.yml

See examples/LiquidityDryup/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

from masim.utils import load_config

# Import from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LiquidityDryup.analysis import (
    load_simulation_data,
    calculate_liquidity_states,
    identify_dryup_episodes,
    plot_liquidity_analysis,
    generate_summary,
)


def main():
    """Run liquidity dry-up analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze LiquidityDryupLLM simulation")
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
    print("LiquidityDryupLLM Analysis - Market Maker Inventory Model (LLM Agents)")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")

    # Calculate liquidity states
    print("\n[2] Calculating liquidity states...")
    liquidity_states = calculate_liquidity_states(data["prices"], data["trades"])

    # Identify dry-up episodes
    print("\n[3] Identifying dry-up episodes...")
    episodes = identify_dryup_episodes(liquidity_states)

    # Generate plots
    print("\n[4] Generating plots...")
    plot_liquidity_analysis(data, liquidity_states, episodes, output_dir)
    print(f"    Saved to {output_dir}/")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, liquidity_states, episodes)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    return summary


if __name__ == "__main__":
    main()
