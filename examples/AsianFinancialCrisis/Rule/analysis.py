#!/usr/bin/env python
"""AsianFinancialCrisis Simulation Analysis

Analyze the AsianFinancialCrisis simulation results.
See analysis-bases.md for metric definitions (§2.1–§2.6).

Usage:
    python examples/AsianFinancialCrisis/Rule/analysis.py \\
        -c configs/AsianFinancialCrisis/Rule/simulation.yml
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config


def load_simulation_data(config: dict) -> dict:
    """Load simulation data from experiment records."""
    record_path = config["setting"]["record_path"]
    data = {"prices": [], "fundamentals": [], "volumes": []}

    market_path = os.path.join(record_path, "market")
    if os.path.exists(market_path):
        for filename in sorted(os.listdir(market_path)):
            if filename.endswith(".json"):
                with open(os.path.join(market_path, filename), "r") as f:
                    record = json.load(f)
                    custom = record.get("custom_state", {})
                    data["prices"].append(custom.get("price", 0))
                    data["fundamentals"].append(custom.get("fundamental", 0))

    return data


def calculate_metrics(data: dict) -> dict:
    """Calculate simulation metrics per analysis-bases.md §2."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])

    if len(prices) == 0:
        return {}

    returns = np.diff(prices) / prices[:-1]
    deviation = (
        (prices - fundamentals) / fundamentals if len(fundamentals) > 0 else prices
    )

    # §2.2 Maximum Drawdown
    peak = np.maximum.accumulate(prices)
    drawdown = (peak - prices) / peak
    max_drawdown = float(np.max(drawdown)) if len(drawdown) > 0 else 0.0

    # §2.3 Crisis Velocity
    crash_velocity = float(np.max(np.abs(np.diff(prices)))) if len(prices) > 1 else 0.0

    # §2.4 Return Autocorrelation
    if len(returns) > 2:
        ac1 = float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
    else:
        ac1 = 0.0

    # §2.6 Crisis Onset Round
    crisis_onset = None
    for i, d in enumerate(deviation):
        if d < -0.10:
            crisis_onset = i
            break

    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
        },
        "deviation_metrics": {
            "max_deviation_pct": float(np.max(np.abs(deviation)) * 100),
            "mean_deviation_pct": float(np.mean(np.abs(deviation)) * 100),
            "min_deviation_pct": float(np.min(deviation) * 100),
        },
        "crisis_metrics": {
            "max_drawdown_pct": max_drawdown * 100,
            "crash_velocity": crash_velocity,
            "return_autocorrelation_ac1": ac1,
            "crisis_onset_round": crisis_onset,
        },
        "volatility": {
            "annualized_pct": (
                float(np.std(returns) * np.sqrt(252) * 100) if len(returns) > 0 else 0
            ),
        },
    }


def create_visualizations(data: dict, output_path: str) -> None:
    """Create analysis plots per analysis-bases.md §7 (Plots 1–4)."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])

    if len(prices) == 0:
        return

    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "AsianFinancialCrisis Rule Simulation Analysis", fontsize=14, fontweight="bold"
    )

    # Plot 1: Price vs Fundamental
    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental", color="blue", linestyle="--"
    )
    axes[0, 0].set_title("Price vs Fundamental (Currency/Asset)")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Price Deviation
    if len(fundamentals) > 0 and fundamentals[0] > 0:
        deviation = (prices - fundamentals) / fundamentals * 100
        axes[0, 1].plot(rounds, deviation, color="purple")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].axhline(
            y=-10, color="orange", linestyle=":", alpha=0.7, label="Crisis onset (-10%)"
        )
        axes[0, 1].set_title("Price Deviation from Fundamental (%)")
        axes[0, 1].set_xlabel("Round")
        axes[0, 1].set_ylabel("Deviation (%)")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Returns
    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        axes[1, 0].plot(rounds[1:], returns, color="red", alpha=0.7)
        axes[1, 0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1, 0].set_title("Round Returns (%) — Contagion Cascade Signal")
        axes[1, 0].set_xlabel("Round")
        axes[1, 0].set_ylabel("Return (%)")
        axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Return Distribution
    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        axes[1, 1].hist(
            returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1, 1].set_title("Return Distribution (Left Tail = Contagion)")
        axes[1, 1].set_xlabel("Return (%)")
        axes[1, 1].set_ylabel("Frequency")
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "asianfinancialcrisis_analysis.png"), dpi=150)
    plt.close()


def main() -> None:
    """Run AsianFinancialCrisis Rule analysis.

    Implements analysis-bases.md §2 core metrics for the Rule baseline variant.
    Output written to EXPERIMENT/AsianFinancialCrisis/Rule/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze AsianFinancialCrisis Rule simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AsianFinancialCrisis/Rule/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)

    if not data["prices"]:
        print("No simulation data found. Run simulation first.")
        return

    metrics = calculate_metrics(data)

    analysis_path = os.path.join(config["setting"]["record_path"], "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations(data, analysis_path)

    with open(os.path.join(analysis_path, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Analysis complete. Results in:", analysis_path)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations"]

if __name__ == "__main__":
    main()
