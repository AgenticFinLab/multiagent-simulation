#!/usr/bin/env python
"""AnchoringEffect LLM Simulation Analysis

Implements analysis-bases.md for the LLM variant.
Reuses all 8 metric functions from Rule/analysis.py and overrides
the variant label and visualization title.

LLM-variant note (analysis-bases.md §4):
    Metric values may show higher variance than Rule due to stochastic LLM decisions.
    Persona Consistency Drift and Narrative Framing Effects are LLM-specific observables.

Usage:
    python examples/AnchoringEffect/LLM/analysis.py \\
        -c configs/AnchoringEffect/LLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.AnchoringEffect.Rule.analysis import (
    _load_agent_records,
    _load_price_records,
    calculate_anchoring_bias_magnitude,
    calculate_anchoring_persistence,
    calculate_autocorrelation,
    calculate_max_drawdown,
    calculate_mean_abs_deviation,
    calculate_price_deviation,
    calculate_rolling_volatility,
    calculate_agent_volumes,
)


def create_visualizations_llm(
    prices: List[float],
    fundamentals: List[float],
    agent_records: Dict[str, List[Dict[str, Any]]],
    output_path: str,
) -> None:
    """Generate LLM-variant analysis visualizations — analysis-bases.md §7.

    Same 6-plot layout as Rule variant, retitled for LLM context.

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.
        agent_records: Per-agent decision records.
        output_path: Directory to write PNG files.
    """
    if not prices:
        return

    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)
    rounds = np.arange(len(prices))
    deviation = (price_arr - fund_arr) / fund_arr * 100

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "AnchoringEffect LLM Variant — Analysis", fontsize=14, fontweight="bold"
    )

    # Plot 1: Price vs. Fundamental
    axes[0, 0].plot(rounds, price_arr, label="Market Price", color="steelblue")
    axes[0, 0].plot(
        rounds, fund_arr, label="Fundamental Value", color="darkgreen", linestyle="--"
    )
    axes[0, 0].set_title("Price vs. Fundamental")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Price Deviation — primary anchoring signal
    axes[0, 1].plot(rounds, deviation, color="crimson")
    axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0, 1].axhline(
        y=3, color="orange", linestyle=":", alpha=0.7, label="3% threshold"
    )
    axes[0, 1].axhline(y=-3, color="orange", linestyle=":", alpha=0.7)
    axes[0, 1].set_title("Price Deviation from Fundamental (%)")
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Deviation (%)")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Rolling Volatility
    if len(prices) > 11:
        returns = np.diff(price_arr) / price_arr[:-1] * 100
        rolling_vols = [
            np.std(returns[max(0, i - 9) : i + 1]) for i in range(len(returns))
        ]
        axes[0, 2].plot(rounds[1:], rolling_vols, color="purple")
        axes[0, 2].set_title("Rolling Volatility (10-round window, %)")
        axes[0, 2].set_xlabel("Round")
        axes[0, 2].set_ylabel("Std Dev of Returns (%)")
        axes[0, 2].grid(True, alpha=0.3)

    # Plot 4: Return Distribution
    if len(prices) > 1:
        returns = np.diff(price_arr) / price_arr[:-1] * 100
        axes[1, 0].hist(
            returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1, 0].set_title("Return Distribution (%) — LLM Stochasticity")
        axes[1, 0].set_xlabel("Return (%)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].grid(True, alpha=0.3)

    # Plot 5: Agent-Type Trading Volume
    if agent_records:
        agent_ids = list(agent_records.keys())
        buy_vols = []
        sell_vols = []
        for agent_id in agent_ids:
            total_buy = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "buy"
            )
            total_sell = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "sell"
            )
            buy_vols.append(total_buy)
            sell_vols.append(total_sell)

        x_pos = np.arange(len(agent_ids))
        axes[1, 1].bar(
            x_pos - 0.2, buy_vols, 0.4, label="Buy", color="green", alpha=0.7
        )
        axes[1, 1].bar(
            x_pos + 0.2, sell_vols, 0.4, label="Sell", color="red", alpha=0.7
        )
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1, 1].set_title("Agent-Type Trading Volume")
        axes[1, 1].set_ylabel("Total Quantity")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

    # Plot 6: Absolute Deviation — anchoring persistence
    abs_deviation = np.abs(deviation)
    axes[1, 2].plot(rounds, abs_deviation, color="darkorange", label="|Deviation|")
    if len(abs_deviation) > 0:
        half_target = abs_deviation[0] / 2.0
        axes[1, 2].axhline(
            y=half_target,
            color="grey",
            linestyle=":",
            alpha=0.7,
            label="Half-life target",
        )
    axes[1, 2].set_title("Anchoring Persistence (|Deviation| Decay)")
    axes[1, 2].set_xlabel("Round")
    axes[1, 2].set_ylabel("|Deviation| (%)")
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_path, "anchoringeffect_llm_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    """Run full AnchoringEffect LLM analysis pipeline.

    Reuses all 8 metrics from Rule/analysis.py. Outputs summary.json
    and a 6-plot visualization labelled for LLM variant.
    LLM variant: expect higher metric variance vs. Rule (analysis-bases.md §4).
    """
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AnchoringEffect/LLM/simulation.yml",
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_path = config["setting"]["record_path"]

    prices, fundamentals = _load_price_records(record_path)

    if not prices:
        print("No simulation data found. Run simulation first.")
        return

    agent_records = _load_agent_records(record_path)

    adjustment_factor = config.get("extras", {}).get("adjustment_factor", 0.3)

    # Compute all 8 metrics from analysis-bases.md §2
    price_deviation = calculate_price_deviation(prices, fundamentals)
    mad = calculate_mean_abs_deviation(prices, fundamentals)
    persistence = calculate_anchoring_persistence(prices, fundamentals)
    rolling_vol = calculate_rolling_volatility(prices)
    autocorr = calculate_autocorrelation(prices)
    max_drawdown = calculate_max_drawdown(prices)
    agent_volumes = calculate_agent_volumes(agent_records)
    bias_magnitude = calculate_anchoring_bias_magnitude(
        prices, fundamentals, adjustment_factor
    )

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations_llm(prices, fundamentals, agent_records, analysis_path)

    summary = {
        "variant": "LLM",
        "simulation": "AnchoringEffect",
        "rounds": len(prices),
        "metrics": {
            "price_deviation": price_deviation,
            "mean_absolute_deviation_pct": float(mad * 100),
            "anchoring_persistence": persistence,
            "rolling_volatility": rolling_vol,
            "return_autocorrelation_lag1": autocorr,
            "max_drawdown": max_drawdown,
            "agent_volumes": agent_volumes,
            "anchoring_bias_magnitude": float(bias_magnitude),
        },
    }

    summary_path = os.path.join(analysis_path, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    agent_volumes_path = os.path.join(analysis_path, "agent_volumes.json")
    with open(agent_volumes_path, "w", encoding="utf-8") as fh:
        json.dump(agent_volumes, fh, indent=2)

    print(f"Analysis complete. Results written to: {analysis_path}")
    print(f"MAD: {mad * 100:.2f}%")
    print(f"Half-life: {persistence['half_life_rounds']:.0f} rounds")
    print(f"Max drawdown: {max_drawdown['max_drawdown_pct']:.2f}%")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}")


if __name__ == "__main__":
    main()
