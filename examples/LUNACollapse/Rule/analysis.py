#!/usr/bin/env python
"""LUNACollapse Simulation Analysis

Analyze the LUNACollapse simulation results.

Usage:
    python examples/LUNACollapse/Rule/analysis.py \
        -c configs/LUNACollapse/Rule/simulation.yml
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
                    custom = record["custom_state"]
                    data["prices"].append(custom["price"])
                    data["fundamentals"].append(custom["fundamental"])
    
    return data


def calculate_metrics(data: dict) -> dict:
    """Calculate simulation metrics."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    
    if len(prices) == 0:
        return {}
    
    returns = np.diff(prices) / prices[:-1]
    deviation = (prices - fundamentals) / fundamentals
    
    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
            "max_drawdown_pct": float(np.min(returns) * 100) if len(returns) > 0 else 0,
        },
        "deviation_metrics": {
            "max_deviation_pct": float(np.max(np.abs(deviation)) * 100) if len(deviation) > 0 else 0,
            "mean_deviation_pct": float(np.mean(np.abs(deviation)) * 100) if len(deviation) > 0 else 0,
        },
        "volatility": {
            "annualized_pct": float(np.std(returns) * np.sqrt(252) * 100) if len(returns) > 0 else 0,
        },
    }


def create_visualizations(data: dict, output_path: str) -> None:
    """Create analysis plots."""
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    
    if len(prices) == 0:
        return
    
    rounds = np.arange(len(prices))
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("LUNACollapse Simulation Analysis", fontsize=14, fontweight="bold")
    
    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(rounds, fundamentals, label="Fundamental", color="blue", linestyle="--")
    axes[0, 0].set_title("Price vs Fundamental")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    if len(fundamentals) > 0 and fundamentals[0] > 0:
        deviation = (prices - fundamentals) / fundamentals * 100
        axes[0, 1].plot(rounds, deviation, color="purple")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].set_title("Price Deviation (%)")
        axes[0, 1].grid(True, alpha=0.3)
    
    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        axes[1, 0].plot(rounds[1:], returns, color="red", alpha=0.7)
        axes[1, 0].set_title("Returns (%)")
        axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].hist(returns if len(prices) > 1 else [0], bins=30, color="steelblue", alpha=0.7)
    axes[1, 1].set_title("Return Distribution")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "lunacollapse_analysis.png"), dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyze LUNACollapse simulation results")
    parser.add_argument("-c", "--config", type=str, default="configs/LUNACollapse/Rule/simulation.yml")
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
    
    with open(os.path.join(analysis_path, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
    
    print("Analysis complete. Results in:", analysis_path)


if __name__ == "__main__":
    main()
