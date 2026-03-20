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

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ShortSqueeze.analysis import (
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

    # Calculate squeeze metrics
    print("\n[2] Calculating squeeze metrics...")
    squeeze_metrics = calculate_squeeze_metrics(data["prices"], data["trades"])
    print(f"    Entry Price: ${squeeze_metrics['entry_price']:.2f}")
    print(
        f"    Peak Price:  ${squeeze_metrics['peak_price']:.2f} (Round {squeeze_metrics['peak_round']})"
    )
    print(f"    Squeeze:     +{squeeze_metrics['squeeze_percentage']:.1f}%")

    # Identify phases
    print("\n[3] Identifying squeeze phases...")
    phases = identify_squeeze_phases(data["prices"])
    for phase_name, phase_data in phases.items():
        print(
            f"    {phase_name.title():12s}: Rounds {phase_data['start']}-{phase_data['end']}"
        )

    # Generate plots
    print("\n[4] Generating plots...")
    plot_squeeze_analysis(data, squeeze_metrics, phases, output_dir)
    print(f"    Saved to {output_dir}/squeeze_analysis.png")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, squeeze_metrics, phases)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Squeeze Detected: {summary['squeeze_detected']}")
    print(f"Squeeze Intensity: {summary['squeeze_intensity']}")
    print(f"Max Squeeze: +{squeeze_metrics['squeeze_percentage']:.1f}%")
    print(f"Short Covering: {'Yes' if summary['short_covering_detected'] else 'No'}")
    print(f"Feedback Loop: {'Yes' if summary['feedback_loop_detected'] else 'No'}")
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()
