#!/usr/bin/env python
"""FlashCrash2010 Simulation Analysis

Analyze the 2010 Flash Crash simulation results.

This script generates visualizations and metrics for the flash crash simulation,
including order book dynamics, HFT participation, and price cascade patterns.

Usage:
    python examples/FlashCrash2010/Rule/analysis.py \
        -c configs/FlashCrash2010/Rule/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load simulation data from experiment records."""
    record_path = config["setting"]["record_path"]

    data = {
        "prices": [],
        "fundamentals": [],
        "volumes": [],
        "spreads": [],
        "depths": [],
        "hft_participation": [],
    }

    market_path = os.path.join(record_path, "market")
    if os.path.exists(market_path):
        for filename in sorted(os.listdir(market_path)):
            if filename.endswith(".json"):
                with open(os.path.join(market_path, filename), "r") as f:
                    record = json.load(f)
                    custom = record.get("custom_state", {})
                    data["prices"].append(custom.get("price", 0))
                    data["fundamentals"].append(custom.get("fundamental", 0))
                    data["spreads"].append(custom.get("spread", 0))
                    data["depths"].append(custom.get("depth", 0))
                    hft = custom.get("hft_participation", [])
                    data["hft_participation"].append(hft[-1] if hft else 0)

    return data


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate flash crash specific metrics."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    spreads = np.array(data["spreads"])
    depths = np.array(data["depths"])
    hft_part = np.array(data["hft_participation"])

    if len(prices) == 0:
        return {}

    returns = np.diff(prices) / prices[:-1]

    min_price = np.min(prices)
    max_price = np.max(prices)
    initial_price = prices[0]
    final_price = prices[-1]

    max_drawdown = (
        (min_price - initial_price) / initial_price if initial_price > 0 else 0
    )
    peak_idx = np.argmax(prices)
    trough_idx = (
        np.argmin(prices[peak_idx:]) + peak_idx if peak_idx < len(prices) else peak_idx
    )
    crash_magnitude = (
        (prices[trough_idx] - prices[peak_idx]) / prices[peak_idx]
        if prices[peak_idx] > 0
        else 0
    )

    volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0

    max_spread = np.max(spreads)
    min_depth = np.min(depths)
    avg_hft_normal = np.mean(hft_part[: len(hft_part) // 3]) if len(hft_part) > 0 else 0
    avg_hft_stress = (
        np.mean(hft_part[len(hft_part) * 2 // 3 :]) if len(hft_part) > 0 else 0
    )

    return {
        "price_metrics": {
            "initial": float(initial_price),
            "final": float(final_price),
            "min": float(min_price),
            "max": float(max_price),
            "max_drawdown_pct": float(max_drawdown * 100),
            "crash_magnitude_pct": float(crash_magnitude * 100),
        },
        "market_structure": {
            "max_spread_pct": float(max_spread * 100),
            "min_depth": float(min_depth),
            "depth_collapse_pct": (
                float((1 - min_depth / np.max(depths)) * 100)
                if np.max(depths) > 0
                else 0
            ),
        },
        "hft_metrics": {
            "avg_participation_normal": float(avg_hft_normal * 100),
            "avg_participation_stress": float(avg_hft_stress * 100),
            "participation_drop_pct": float((avg_hft_normal - avg_hft_stress) * 100),
        },
        "volatility": {
            "annualized_volatility": float(volatility * 100),
        },
    }


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Create flash crash analysis plots."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    spreads = np.array(data["spreads"])
    depths = np.array(data["depths"])
    hft_part = np.array(data["hft_participation"])

    if len(prices) == 0:
        print("No data to visualize")
        return

    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle("FlashCrash2010 Simulation Analysis", fontsize=14, fontweight="bold")

    ax1 = axes[0, 0]
    ax1.plot(rounds, prices, label="Price", color="red", linewidth=1.5)
    ax1.plot(
        rounds,
        fundamentals,
        label="Fundamental",
        color="blue",
        linestyle="--",
        linewidth=1,
    )
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Price ($)")
    ax1.set_title("Price vs Fundamental Value")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2 = axes[0, 1]
    if len(fundamentals) > 0 and fundamentals[0] > 0:
        deviation = (prices - fundamentals) / fundamentals * 100
        ax2.plot(rounds, deviation, color="purple", linewidth=1.5)
        ax2.axhline(y=0, color="black", linestyle="--", alpha=0.5)
        ax2.fill_between(rounds, deviation, 0, alpha=0.3, color="purple")
        ax2.set_xlabel("Round")
        ax2.set_ylabel("Deviation (%)")
        ax2.set_title("Price Deviation from Fundamental")
        ax2.grid(True, alpha=0.3)

    ax3 = axes[1, 0]
    spread_pct = spreads * 100
    ax3.plot(rounds, spread_pct, color="orange", linewidth=1.5)
    ax3.set_xlabel("Round")
    ax3.set_ylabel("Spread (%)")
    ax3.set_title("Bid-Ask Spread Evolution")
    ax3.grid(True, alpha=0.3)

    ax4 = axes[1, 1]
    ax4.plot(rounds, depths, color="green", linewidth=1.5)
    ax4.set_xlabel("Round")
    ax4.set_ylabel("Depth (shares)")
    ax4.set_title("Order Book Depth")
    ax4.grid(True, alpha=0.3)

    ax5 = axes[2, 0]
    hft_pct = hft_part * 100
    ax5.plot(rounds, hft_pct, color="cyan", linewidth=1.5)
    ax5.set_xlabel("Round")
    ax5.set_ylabel("HFT Participation (%)")
    ax5.set_title("HFT Market Participation")
    ax5.grid(True, alpha=0.3)

    ax6 = axes[2, 1]
    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        ax6.plot(rounds[1:], returns, color="red", alpha=0.7, linewidth=0.8)
        ax6.axhline(y=0, color="black", linestyle="--", alpha=0.5)
        ax6.set_xlabel("Round")
        ax6.set_ylabel("Return (%)")
        ax6.set_title("Price Returns")
        ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "flashcrash2010_analysis.png"), dpi=150)
    plt.close()

    print(f"Visualization saved to: {output_path}/flashcrash2010_analysis.png")


def generate_summary_report(metrics: Dict[str, Any], output_path: str) -> None:
    """Generate text summary of flash crash metrics."""
    report_path = os.path.join(output_path, "summary.txt")

    with open(report_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("FlashCrash2010 Simulation Analysis Summary\n")
        f.write("=" * 70 + "\n\n")

        if "price_metrics" in metrics:
            pm = metrics["price_metrics"]
            f.write("PRICE METRICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Initial Price:      ${pm['initial']:.2f}\n")
            f.write(f"Final Price:        ${pm['final']:.2f}\n")
            f.write(f"Minimum Price:      ${pm['min']:.2f}\n")
            f.write(f"Maximum Price:      ${pm['max']:.2f}\n")
            f.write(f"Max Drawdown:       {pm['max_drawdown_pct']:.2f}%\n")
            f.write(f"Crash Magnitude:    {pm['crash_magnitude_pct']:.2f}%\n\n")

        if "market_structure" in metrics:
            ms = metrics["market_structure"]
            f.write("MARKET STRUCTURE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Maximum Spread:     {ms['max_spread_pct']:.4f}%\n")
            f.write(f"Minimum Depth:      {ms['min_depth']:.0f} shares\n")
            f.write(f"Depth Collapse:     {ms['depth_collapse_pct']:.1f}%\n\n")

        if "hft_metrics" in metrics:
            hm = metrics["hft_metrics"]
            f.write("HFT METRICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Normal Participation:   {hm['avg_participation_normal']:.1f}%\n")
            f.write(f"Stress Participation:   {hm['avg_participation_stress']:.1f}%\n")
            f.write(f"Participation Drop:     {hm['participation_drop_pct']:.1f}%\n\n")

        if "volatility" in metrics:
            f.write("VOLATILITY\n")
            f.write("-" * 40 + "\n")
            f.write(
                f"Annualized Volatility:  {metrics['volatility']['annualized_volatility']:.2f}%\n\n"
            )

        f.write("=" * 70 + "\n")
        f.write("INTERPRETATION\n")
        f.write("=" * 70 + "\n\n")

        if "price_metrics" in metrics:
            drawdown = metrics["price_metrics"]["max_drawdown_pct"]
            if drawdown < -5:
                f.write("✓ Flash crash pattern observed: significant price decline\n")
            else:
                f.write("✗ No significant crash: price remained relatively stable\n")

        if "market_structure" in metrics:
            collapse = metrics["market_structure"]["depth_collapse_pct"]
            if collapse > 50:
                f.write("✓ Order book depth collapsed during stress\n")
            else:
                f.write("✗ Order book remained relatively deep\n")

        if "hft_metrics" in metrics:
            drop = metrics["hft_metrics"]["participation_drop_pct"]
            if drop > 20:
                f.write("✓ HFT participation dropped significantly during stress\n")
            else:
                f.write("✗ HFT participation remained stable\n")

    print(f"Summary saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze FlashCrash2010 simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/Rule/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    print("\n" + "=" * 70)
    print("FlashCrash2010 Analysis")
    print("=" * 70 + "\n")

    data = load_simulation_data(config)

    if not data["prices"]:
        print("No simulation data found. Run simulation first.")
        return

    print(f"Loaded {len(data['prices'])} rounds of data")

    metrics = calculate_metrics(data)

    analysis_path = os.path.join(config["setting"]["record_path"], "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations(data, analysis_path)
    generate_summary_report(metrics, analysis_path)

    metrics_path = os.path.join(analysis_path, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nMetrics saved to: {metrics_path}")
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
