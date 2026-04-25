#!/usr/bin/env python
"""ArchegosCollapse LLM Simulation Analysis

LLM-variant analysis for the ArchegosCollapse simulation.
Reuses core metric functions from Rule/analysis.py and adds LLM-specific
visualization title. See analysis-bases.md for metric definitions.

Usage:
    python examples/ArchegosCollapse/LLM/analysis.py \\
        -c configs/ArchegosCollapse/LLM/simulation.yml
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)


def main() -> None:
    """Run ArchegosCollapse LLM analysis: load data, compute metrics, plot.

    Analysis implements analysis-bases.md §2 (all 6 metrics) for the LLM variant.
    Output written to EXPERIMENT/ArchegosCollapse/LLM/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze ArchegosCollapse LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ArchegosCollapse/LLM/simulation.yml",
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

    # Reuse Rule visualization but with LLM variant title
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "ArchegosCollapse LLM Simulation Analysis", fontsize=14, fontweight="bold"
    )

    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    rounds = np.arange(len(prices))

    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental", color="blue", linestyle="--"
    )
    axes[0, 0].set_title("Price vs Fundamental (LLM)")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    if len(fundamentals) > 0 and fundamentals[0] > 0:
        deviation = (prices - fundamentals) / fundamentals * 100
        axes[0, 1].plot(rounds, deviation, color="purple")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].set_title("Price Deviation from Fundamental (%)")
        axes[0, 1].grid(True, alpha=0.3)

    if len(prices) > 1:
        returns = np.diff(prices) / prices[:-1] * 100
        axes[1, 0].plot(rounds[1:], returns, color="darkorange", alpha=0.7)
        axes[1, 0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1, 0].set_title("Round Returns (%) — LLM Stochastic Variability")
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].hist(
            returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1, 1].set_title("Return Distribution (LLM)")
        axes[1, 1].set_xlabel("Return (%)")
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(analysis_path, "archegsoscollapse_llm_analysis.png"), dpi=150
    )
    plt.close()

    with open(os.path.join(analysis_path, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"variant": "LLM", **metrics}, f, indent=2)

    print("LLM analysis complete. Results in:", analysis_path)


__all__ = ["main"]

if __name__ == "__main__":
    main()
