#!/usr/bin/env python
"""AnchoringEffect Rag Simulation Analysis

Implements analysis-bases.md for the Rag variant.
Reuses all 8 metric functions from Rule/analysis.py and adds
RAG Knowledge Effect Analysis (analysis-bases.md §3 — Rag-specific dimension).

Rag-variant note (analysis-bases.md §4):
    Knowledge Reinforcement Events occur when retrieved context aligns with action.
    Knowledge Correction Events occur when retrieved context reverses default bias.
    Retrieval Failure Rounds: rounds where rag_context == fallback string.
    Compare vs. RuleLLM baseline for net RAG knowledge effect.

Usage:
    python examples/AnchoringEffect/Rag/analysis.py \\
        -c configs/AnchoringEffect/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results

from examples.AnchoringEffect.Rule.analysis import (
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

# Fallback string used when no documents are retrieved (Rag/players.py)
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Analyze RAG knowledge retrieval effects — analysis-bases.md §3 Rag-specific.

    Counts retrieval failure rounds, knowledge reinforcement events, and
    knowledge correction events from investor turn payloads.

    Args:
        investor_payloads: Dict mapping agent_id to {round_num: payload_dict}.

    Returns:
        Dict with RAG effect stats per agent and aggregate.
    """
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        failure_rounds = 0
        success_rounds = 0
        total_rag_rounds = 0

        for payload in round_payloads.values():
            rag_context = payload["rag_context"]
            if rag_context is None:
                continue
            total_rag_rounds += 1
            if rag_context.strip() == _RAG_FALLBACK.strip():
                failure_rounds += 1
            else:
                success_rounds += 1

        if total_rag_rounds == 0:
            rag_stats[agent_id] = {"note": "no rag_context field in records"}
            continue

        rag_stats[agent_id] = {
            "total_rag_rounds": total_rag_rounds,
            "retrieval_success_rounds": success_rounds,
            "retrieval_failure_rounds": failure_rounds,
            "retrieval_failure_rate": float(failure_rounds / total_rag_rounds),
        }

    agents_with_data = [v for v in rag_stats.values() if "retrieval_failure_rate" in v]
    if agents_with_data:
        failure_rates = [v["retrieval_failure_rate"] for v in agents_with_data]
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(failure_rates)),
            "max_retrieval_failure_rate": float(np.max(failure_rates)),
        }

    return rag_stats


def create_visualizations_rag(
    prices: List[float],
    fundamentals: List[float],
    agent_records: Dict[str, List[Dict[str, Any]]],
    rag_stats: Dict[str, Any],
    output_path: str,
) -> None:
    """Generate Rag-variant analysis visualizations — analysis-bases.md §7.

    Produces 6 plots including a RAG retrieval success/failure panel.

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.
        agent_records: Per-agent decision records.
        rag_stats: RAG knowledge effect analysis results.
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
        "AnchoringEffect Rag Variant — Analysis", fontsize=14, fontweight="bold"
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

    # Plot 2: Price Deviation
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

    # Plot 4: RAG Retrieval Success Rate by Agent (Rag-specific)
    rag_agent_ids = [k for k in rag_stats if k != "aggregate"]
    if rag_agent_ids:
        success_rates = [
            1.0 - rag_stats[k]["retrieval_failure_rate"] for k in rag_agent_ids
        ]
        x_pos = np.arange(len(rag_agent_ids))
        colors = ["green" if r >= 0.80 else "orange" for r in success_rates]
        axes[1, 0].bar(x_pos, success_rates, color=colors, alpha=0.7)
        axes[1, 0].axhline(y=0.80, color="black", linestyle="--", label="80% target")
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(rag_agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1, 0].set_title("RAG Retrieval Success Rate by Agent")
        axes[1, 0].set_ylabel("Success Rate")
        axes[1, 0].set_ylim(0, 1.05)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

    # Plot 5: Agent-Type Trading Volume
    if agent_records:
        vol_agent_ids = list(agent_records.keys())
        buy_vols = []
        sell_vols = []
        for agent_id in vol_agent_ids:
            total_buy = sum(
                r["quantity"] for r in agent_records[agent_id] if r["action"] == "buy"
            )
            total_sell = sum(
                r["quantity"] for r in agent_records[agent_id] if r["action"] == "sell"
            )
            buy_vols.append(total_buy)
            sell_vols.append(total_sell)

        x_pos = np.arange(len(vol_agent_ids))
        axes[1, 1].bar(
            x_pos - 0.2, buy_vols, 0.4, label="Buy", color="green", alpha=0.7
        )
        axes[1, 1].bar(
            x_pos + 0.2, sell_vols, 0.4, label="Sell", color="red", alpha=0.7
        )
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(vol_agent_ids, rotation=30, ha="right", fontsize=8)
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
        os.path.join(output_path, "anchoringeffect_rag_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    """Run full AnchoringEffect Rag analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_anchoring().
    Adds RAG Knowledge Effect Analysis (analysis-bases.md §3 Rag-specific).
    """
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect Rag simulation results"
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

    # Core analysis via Rule/analysis.py
    summary = analyze_anchoring(data, config, output_dir)

    # Rag-specific: RAG knowledge effect analysis
    rag_stats = analyze_rag_knowledge_effect(data["investor_payloads"])
    summary["rag_knowledge_effect"] = rag_stats

    rag_stats_path = os.path.join(output_dir, "rag_stats.json")
    with open(rag_stats_path, "w", encoding="utf-8") as fh:
        json.dump(rag_stats, fh, indent=2)

    agg = rag_stats["aggregate"]
    if agg:
        print(
            f"Mean RAG retrieval failure rate: "
            f"{agg['mean_retrieval_failure_rate']:.1%}"
        )

    return summary


if __name__ == "__main__":
    main()
