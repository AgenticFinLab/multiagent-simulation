#!/usr/bin/env python
"""EuropeanDebtCrisis Rule analysis utilities."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config


def load_simulation_data(config: dict) -> Dict[str, Any]:
    """Load market price and fundamental records from an experiment run."""
    record_path = config["setting"]["record_path"]
    market_path = os.path.join(record_path, "market")
    if not os.path.exists(market_path):
        raise FileNotFoundError(f"Market record directory not found: {market_path}")

    prices = []
    fundamentals = []
    for filename in sorted(os.listdir(market_path)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(market_path, filename), "r", encoding="utf-8") as f:
            record = json.load(f)
        custom_state = record["custom_state"]
        prices.append(float(custom_state["price"]))
        fundamentals.append(float(custom_state["fundamental"]))

    if not prices:
        raise ValueError(f"No market price records found in {market_path}")
    return {"prices": prices, "fundamentals": fundamentals}


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate EuropeanDebtCrisis metrics from analysis-bases.md §2."""
    prices = np.asarray(data["prices"], dtype=float)
    fundamentals = np.asarray(data["fundamentals"], dtype=float)
    if len(prices) < 2:
        raise ValueError("At least two price records are required for metrics")
    if np.any(fundamentals == 0):
        raise ValueError("Fundamental values must be non-zero")

    deviations = (prices - fundamentals) / fundamentals
    crisis_mask = deviations < -0.10
    trough_idx = int(np.argmin(deviations))
    recovery_candidates = np.where(deviations[trough_idx:] > -0.05)[0]
    spread_recovery_time = (
        int(recovery_candidates[0]) if len(recovery_candidates) > 0 else -1
    )

    return {
        "crisis_depth_index": float(abs(np.min(deviations))),
        "crisis_duration": int(np.sum(crisis_mask)),
        "spread_recovery_time": spread_recovery_time,
        "final_deviation": float(deviations[-1]),
        "min_price": float(np.min(prices)),
        "max_price": float(np.max(prices)),
    }


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Create standard EuropeanDebtCrisis diagnostic plots."""
    prices = np.asarray(data["prices"], dtype=float)
    fundamentals = np.asarray(data["fundamentals"], dtype=float)
    if len(prices) < 2:
        raise ValueError("At least two price records are required for visualization")
    if np.any(fundamentals == 0):
        raise ValueError("Fundamental values must be non-zero")

    rounds = np.arange(len(prices))
    deviations = (prices - fundamentals) / fundamentals * 100
    returns = np.diff(prices) / prices[:-1] * 100

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("EuropeanDebtCrisis Analysis", fontsize=14, fontweight="bold")

    axes[0, 0].plot(rounds, prices, label="Bond Price", color="firebrick")
    axes[0, 0].plot(rounds, fundamentals, label="Fundamental", linestyle="--")
    axes[0, 0].set_title("Price vs Fundamental")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(rounds, deviations, color="purple")
    axes[0, 1].axhline(y=-10, color="red", linestyle="--", alpha=0.6)
    axes[0, 1].axhline(y=-5, color="orange", linestyle="--", alpha=0.6)
    axes[0, 1].set_title("Deviation from Fundamental (%)")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(rounds[1:], returns, color="steelblue", alpha=0.8)
    axes[1, 0].set_title("Returns (%)")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].hist(returns, bins=30, color="gray", alpha=0.75)
    axes[1, 1].set_title("Return Distribution")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "europeandebtcrisis_analysis.png"), dpi=150)
    plt.close()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Analyze EuropeanDebtCrisis results")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EuropeanDebtCrisis/Rule/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)

    analysis_path = os.path.join(config["setting"]["record_path"], "analysis")
    os.makedirs(analysis_path, exist_ok=True)
    create_visualizations(data, analysis_path)

    with open(os.path.join(analysis_path, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print("Analysis complete. Results in:", analysis_path)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
