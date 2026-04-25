#!/usr/bin/env python
"""CarryTradeUnwind Rule-Based Simulation Analysis

Authoritative analysis module for the CarryTradeUnwind simulation.
All LLM, RuleLLM, and Rag variants import core functions from this module.
See analysis-bases.md for full metric definitions and methodology.

Usage:
    python examples/CarryTradeUnwind/Rule/analysis.py \\
        -c configs/CarryTradeUnwind/Rule/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations"]


def load_simulation_data(config: dict) -> dict:
    """Load simulation data from experiment records.

    Reads per-round JSON records written by the Market agent to extract
    the price series and fundamental series.

    Args:
        config: Parsed simulation YAML config (from masim.utils.config.load_config).

    Returns:
        dict with keys:
            "prices"      — list[float] exchange rate per round
            "fundamentals"— list[float] PPP fundamental per round
            "deviations"  — list[float] (price-fundamental)/fundamental per round
    """
    record_path = config["setting"]["record_path"]
    data: dict = {"prices": [], "fundamentals": [], "deviations": []}

    market_path = os.path.join(record_path, "market")
    if os.path.exists(market_path):
        for filename in sorted(os.listdir(market_path)):
            if filename.endswith(".json"):
                fpath = os.path.join(market_path, filename)
                with open(fpath, "r", encoding="utf-8") as f:
                    record = json.load(f)
                custom = record.get("custom_state", {})
                price = custom.get("price", 0.0)
                fundamental = custom.get("fundamental", 0.0)
                deviation = custom.get("deviation", 0.0)
                data["prices"].append(float(price))
                data["fundamentals"].append(float(fundamental))
                data["deviations"].append(float(deviation))

    return data


def calculate_metrics(data: dict) -> dict:
    """Calculate CarryTradeUnwind-specific simulation metrics.

    Implements all metrics defined in analysis-bases.md §2:
      §2.1  max_drawdown_pct  — maximum peak-to-trough FX decline
      §2.2  unwind_velocity   — fastest single-round FX move (abs)
      §2.3  unwind_duration   — rounds with deviation < -0.05
      §2.4  crisis_onset      — first round where deviation < -0.05
      §2.5  recovery_ratio    — (|dev_min| - |dev_final|) / |dev_min|
      §2.6  AC(1)             — first-order return autocorrelation
      §2.7  annualized_vol    — std(returns) * sqrt(252) * 100

    Args:
        data: Output of load_simulation_data().

    Returns:
        Nested dict with keys: price_metrics, unwind_metrics, market_metrics.
    """
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    deviations = np.array(data["deviations"])

    if len(prices) == 0:
        return {}

    # §2.1 Max drawdown
    peak = np.maximum.accumulate(prices)
    drawdowns = (peak - prices) / np.where(peak > 0, peak, 1.0)
    max_drawdown = float(np.max(drawdowns) * 100)

    # §2.2 Unwind velocity (fastest single-round absolute move)
    if len(prices) > 1:
        price_changes = np.abs(np.diff(prices))
        unwind_velocity = float(np.max(price_changes))
    else:
        unwind_velocity = 0.0

    # §2.3 Unwind duration (rounds where deviation < -0.05)
    CRISIS_THRESHOLD = -0.05
    crisis_mask = deviations < CRISIS_THRESHOLD
    unwind_duration = int(np.sum(crisis_mask))

    # §2.4 Crisis onset round
    crisis_indices = np.where(crisis_mask)[0]
    crisis_onset = int(crisis_indices[0]) if len(crisis_indices) > 0 else -1

    # §2.5 Recovery ratio
    if len(deviations) > 0:
        dev_min = float(np.min(deviations))
        dev_final = float(deviations[-1])
        if abs(dev_min) > 1e-9:
            recovery_ratio = float((abs(dev_min) - abs(dev_final)) / abs(dev_min))
        else:
            recovery_ratio = 0.0
    else:
        dev_min = dev_final = recovery_ratio = 0.0

    # §2.6 AC(1) — first-order return autocorrelation
    if len(prices) > 2:
        returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0)
        if len(returns) > 2:
            ac1 = float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
        else:
            ac1 = 0.0
    else:
        returns = np.array([])
        ac1 = 0.0

    # §2.7 Annualized volatility
    if len(returns) > 1:
        ann_vol = float(np.std(returns) * np.sqrt(252) * 100)
    else:
        ann_vol = 0.0

    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
        },
        "unwind_metrics": {
            "max_drawdown_pct": max_drawdown,
            "unwind_velocity": unwind_velocity,
            "unwind_duration_rounds": unwind_duration,
            "crisis_onset_round": crisis_onset,
            "recovery_ratio": recovery_ratio,
            "min_deviation_pct": float(dev_min * 100),
            "final_deviation_pct": float(dev_final * 100),
        },
        "market_metrics": {
            "return_autocorrelation_ac1": ac1,
            "annualized_vol_pct": ann_vol,
        },
    }


def create_visualizations(data: dict, output_path: str, variant: str = "Rule") -> None:
    """Create standard CarryTradeUnwind analysis plots.

    Generates a 2×2 figure:
      [0,0] FX rate vs PPP fundamental
      [0,1] Deviation from fundamental (%)
      [1,0] Round-by-round returns (%)
      [1,1] Return distribution histogram

    Args:
        data:        Output of load_simulation_data().
        output_path: Directory where the PNG will be saved.
        variant:     Variant label for plot title and filename.
    """
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])

    if len(prices) == 0:
        return

    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        f"CarryTradeUnwind {variant} Simulation Analysis",
        fontsize=14,
        fontweight="bold",
    )

    # [0,0] FX rate vs PPP fundamental
    axes[0, 0].plot(rounds, prices, label="FX Rate", color="steelblue")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental (PPP)", color="orange", linestyle="--"
    )
    axes[0, 0].set_title("FX Rate vs PPP Fundamental")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # [0,1] Deviation (%)
    if len(fundamentals) > 0 and np.any(fundamentals > 0):
        deviation_pct = (
            (prices - fundamentals)
            / np.where(fundamentals > 0, fundamentals, 1.0)
            * 100
        )
        axes[0, 1].plot(rounds, deviation_pct, color="crimson")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].axhline(
            y=-5, color="red", linestyle=":", alpha=0.7, label="-5% crisis threshold"
        )
        axes[0, 1].set_title("Price Deviation from Fundamental (%)")
        axes[0, 1].set_xlabel("Round")
        axes[0, 1].set_ylabel("Deviation (%)")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

    # [1,0] Returns
    if len(prices) > 1:
        returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0) * 100
        axes[1, 0].plot(rounds[1:], returns, color="darkorange", alpha=0.7)
        axes[1, 0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1, 0].set_title("Round Returns (%)")
        axes[1, 0].set_xlabel("Round")
        axes[1, 0].set_ylabel("Return (%)")
        axes[1, 0].grid(True, alpha=0.3)

        # [1,1] Return distribution
        axes[1, 1].hist(
            returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1, 1].set_title("Return Distribution")
        axes[1, 1].set_xlabel("Return (%)")
        axes[1, 1].set_ylabel("Frequency")
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    fname = f"carrytradeunwind_{variant.lower()}_analysis.png"
    plt.savefig(os.path.join(output_path, fname), dpi=150)
    plt.close()


def main() -> None:
    """Run CarryTradeUnwind Rule analysis: compute metrics + generate plots.

    Implements analysis-bases.md §2 core metrics. Output written to
    EXPERIMENT/CarryTradeUnwind/Rule/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze CarryTradeUnwind Rule simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/CarryTradeUnwind/Rule/simulation.yml",
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

    create_visualizations(data, analysis_path, variant="Rule")

    with open(os.path.join(analysis_path, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Analysis complete. Results in:", analysis_path)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
