"""EquityPremiumLLM Analysis - Myopic Loss Aversion Evaluation (LLM Version)

Analyzes equity premium puzzle in LLM-driven agents.
Uses same methodology as rule-based EquityPremium.

Usage:
    python examples/EquityPremium/LLM/analysis.py -c configs/EquityPremium/LLM/simulation.yml

See examples/EquityPremium/Rule/analysis.py for detailed documentation.
"""

import argparse
import json
import os

from masim.utils import load_config, load_results

from examples.EquityPremium.Rule.analysis import (
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

    # Calculate equity premium
    print("\n[2] Calculating equity premium metrics...")
    premium_metrics = calculate_equity_premium(prices, len(prices))
    print(f"    Annual Stock Return: {premium_metrics['annual_return']:.2f}%")
    print(f"    Risk-Free Rate:      {premium_metrics['risk_free_rate']:.2f}%")
    print(f"    Equity Premium:      {premium_metrics['equity_premium']:.2f}%")
    print(f"    Sharpe Ratio:        {premium_metrics['sharpe_ratio']:.2f}")

    # Calculate loss probability by horizon
    print("\n[3] Calculating loss probability by horizon...")
    horizons = [1, 5, 10, 20, 50, 100]
    horizons = [h for h in horizons if h < len(prices)]
    loss_probs = calculate_loss_probability(prices, horizons)
    for h, prob in sorted(loss_probs.items()):
        print(f"    Horizon {h:3d} rounds: P(Loss) = {prob:.1f}%")

    # Analyze investor allocations
    print("\n[4] Analyzing investor allocations...")
    allocations = analyze_investor_allocations(trades)
    for pid, alloc in allocations.items():
        print(
            f"    {alloc['strategy']:24s}: Stock allocation ~{alloc['implied_stock_allocation']*100:.0f}%"
        )

    # Generate plots (pass prices/trades directly to avoid re-extracting)
    print("\n[5] Generating plots...")
    plot_equity_premium_analysis(
        {"prices": prices, "trades": trades},
        premium_metrics,
        loss_probs,
        allocations,
        output_dir,
    )
    print(f"    Saved to {output_dir}/equity_premium_analysis.png")

    # Generate summary
    print("\n[6] Generating summary...")
    summary = generate_summary(
        {"prices": prices, "trades": trades}, premium_metrics, loss_probs, allocations
    )

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Equity Premium: {premium_metrics['equity_premium']:.2f}% annual")
    print(
        f"Puzzle Explanation: {'Supported' if summary['puzzle_explained'] else 'Not clear'}"
    )
    if loss_probs:
        short_h = min(loss_probs.keys())
        long_h = max(loss_probs.keys())
        print(f"Short-horizon P(Loss): {loss_probs[short_h]:.1f}%")
        print(f"Long-horizon P(Loss):  {loss_probs[long_h]:.1f}%")
        print("→ Myopic investors see more losses, demand higher premium")
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()
