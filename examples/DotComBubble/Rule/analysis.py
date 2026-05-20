#!/usr/bin/env python
"""DotComBubble Simulation Analysis

Analyze the DotComBubble simulation results.

Usage:
    python examples/DotComBubble/Rule/analysis.py \
        -c configs/DotComBubble/Rule/simulation.yml
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
    if not os.path.exists(market_path):
        raise FileNotFoundError(f"Market record directory not found: {market_path}")
    for filename in sorted(os.listdir(market_path)):
        if filename.endswith(".json"):
            with open(os.path.join(market_path, filename), "r") as f:
                record = json.load(f)
                custom = record["custom_state"]
                data["prices"].append(custom["price"])
                data["fundamentals"].append(custom["fundamental"])

    if not data["prices"]:
        raise ValueError(f"No market price records found in {market_path}")
    return data


def calculate_metrics(data: dict) -> dict:
    """Calculate simulation metrics."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])

    if len(prices) < 2:
        raise ValueError("At least two price records are required for metrics")
    if np.any(fundamentals == 0):
        raise ValueError("Fundamental values must be non-zero")

    returns = np.diff(prices) / prices[:-1]
    deviation = (prices - fundamentals) / fundamentals

    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
            "max_drawdown_pct": float(np.min(returns) * 100),
        },
        "deviation_metrics": {
            "max_deviation_pct": float(np.max(np.abs(deviation)) * 100),
            "mean_deviation_pct": float(np.mean(np.abs(deviation)) * 100),
        },
        "volatility": {
            "annualized_pct": float(np.std(returns) * np.sqrt(252) * 100),
        },
    }


def create_visualizations(data: dict, output_path: str) -> None:
    """Create analysis plots."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])

    if len(prices) < 2:
        raise ValueError("At least two price records are required for visualization")
    if np.any(fundamentals == 0):
        raise ValueError("Fundamental values must be non-zero")

    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("DotComBubble Simulation Analysis", fontsize=14, fontweight="bold")

    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(rounds, fundamentals, label="Fundamental", color="blue", linestyle="--")
    axes[0, 0].set_title("Price vs Fundamental")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    deviation = (prices - fundamentals) / fundamentals * 100
    axes[0, 1].plot(rounds, deviation, color="purple")
    axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0, 1].set_title("Price Deviation (%)")
    axes[0, 1].grid(True, alpha=0.3)

    returns = np.diff(prices) / prices[:-1] * 100
    axes[1, 0].plot(rounds[1:], returns, color="red", alpha=0.7)
    axes[1, 0].set_title("Returns (%)")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].hist(returns, bins=30, color="steelblue", alpha=0.7)
    axes[1, 1].set_title("Return Distribution")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "dotcombubble_analysis.png"), dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze DotComBubble simulation results")
    parser.add_argument("-c", "--config", type=str, default="configs/DotComBubble/Rule/simulation.yml")
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)

    metrics = calculate_metrics(data)

    analysis_path = os.path.join(config["setting"]["record_path"], "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations(data, analysis_path)

    with open(os.path.join(analysis_path, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("Analysis complete. Results in:", analysis_path)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
