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
from collections import defaultdict

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LiquidityDryup.analysis import (
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

    # Load data via lazy result loader
    print("\n[1] Loading simulation data...")
    results = load_results(config)
    # Coordinator batch store 'price' holds the market price time-series
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("price").all()) if coordinators else []
    # payload fields: bid_price, quantity, strategy, investor
    trades = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            # Inject round number into each payload for downstream analysis
            trades[pid] = [
                {**p, "round": rn} for rn, p in sorted(payloads_by_round.items())
            ]
    data = {"prices": prices, "trades": trades}
    print(f"    Loaded {len(prices)} price points")
    print(f"    Loaded trades from {len(trades)} players")

    # Calculate liquidity states
    print("\n[2] Calculating liquidity states...")
    liquidity_states = calculate_liquidity_states(data["prices"], data["trades"])

    state_summary = defaultdict(int)
    for s in liquidity_states:
        state_summary[s["state"]] += 1
    for state, count in state_summary.items():
        pct = count / len(liquidity_states) * 100 if liquidity_states else 0
        print(f"    {state:10s}: {count:4d} rounds ({pct:.1f}%)")

    # Identify dry-up episodes
    print("\n[3] Identifying dry-up episodes...")
    episodes = identify_dryup_episodes(liquidity_states)
    print(f"    Found {len(episodes)} dry-up episodes")
    for i, ep in enumerate(episodes):
        print(
            f"    Episode {i + 1}: Rounds {ep['start']}-{ep['end']} "
            f"(duration: {ep['duration']}, min liquidity: {ep['min_liquidity']:.0f})"
        )

    # Generate plots
    print("\n[4] Generating plots...")
    plot_liquidity_analysis(data, liquidity_states, episodes, output_dir)
    print(f"    Saved to {output_dir}/liquidity_analysis.png")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, liquidity_states, episodes)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Dry-up Detected: {summary['dryup_detected']}")
    print(f"Severity: {summary['dryup_severity']}")
    print(f"Episodes: {summary['dryup_episodes']['count']}")
    print(
        f"Total Duration in Dry-up: {summary['dryup_episodes']['total_duration']} rounds"
    )
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()
