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

from masim.utils import load_config, load_results

from examples.AnchoringEffect.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_anchoring_effect,
    _build_interpretation,
    _compute_mad,
    _compute_half_life,
    _compute_autocorrelation,
    _compute_max_drawdown,
    _compute_rolling_volatility,
    _compute_bias_magnitude,
    analyze_anchoring,
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
                r["quantity"] for r in agent_records[agent_id] if r["action"] == "buy"
            )
            total_sell = sum(
                r["quantity"] for r in agent_records[agent_id] if r["action"] == "sell"
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

    Reuses all metrics from Rule/analysis.py via analyze_anchoring().
    LLM variant: expect higher metric variance vs. Rule (analysis-bases.md §4).
    """
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_anchoring(data, config, output_dir)
    return summary


if __name__ == "__main__":
    main()
