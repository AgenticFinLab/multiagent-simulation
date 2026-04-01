"""DispositionEffectRuleLLM Analysis - Prospect Theory Trading Evaluation (Rule+LLM Hybrid)

Analyzes disposition effect in hybrid Rule+LLM agents.
Uses same methodology as rule-based DispositionEffect, reusing the shared analysis pipeline.

Usage:
    python examples/DispositionEffect/RuleLLM/analysis.py -c configs/DispositionEffect/RuleLLM/simulation.yml

See examples/DispositionEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DispositionEffect.analysis import (
    analyze_by_strategy,
    plot_disposition_analysis,
    generate_summary,
)


def main():
    """Run disposition effect analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze DispositionEffectRuleLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("DispositionEffectRuleLLM Analysis - Prospect Theory (Rule+LLM Hybrid)")
    print("=" * 70)

    # Load data via lazy result loader
    print("\n[1] Loading simulation data...")
    results = load_results(config)
    # Coordinator batch store 'price' holds the market price time-series
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("price").all()) if coordinators else []
    # Each non-coordinator player contributes per-round decision payloads
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

    # Analyze by strategy
    print("\n[2] Calculating PGR/PLR metrics...")
    strategy_results = analyze_by_strategy(data)

    for _, res in strategy_results.items():
        print(
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    # Generate plots
    print("\n[3] Generating figures (7 plots)...")
    plot_disposition_analysis(data, strategy_results, output_dir)
    print(f"    All figures saved to: {output_dir}/")

    # Generate summary
    print("\n[4] Generating summary...")
    summary = generate_summary(data, strategy_results)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Disposition Effect Detected: {summary['disposition_effect_detected']}")
    if summary["disposition_investor"]:
        disp = summary["disposition_investor"]
        print(f"Disposition Investor: PGR={disp['pgr']:.3f}, PLR={disp['plr']:.3f}")
        print(
            f"  -> Sells winners {disp['pgr']/disp['plr']:.1f}x more readily than losers"
            if disp["plr"] > 0
            else ""
        )
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()
