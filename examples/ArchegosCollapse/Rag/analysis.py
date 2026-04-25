#!/usr/bin/env python
"""ArchegosCollapse Rag Simulation Analysis

Rag-variant analysis for the ArchegosCollapse simulation.
Reuses core metric functions from Rule/analysis.py and adds
RAG knowledge-effect analysis specific to the Rag variant.
See analysis-bases.md for metric definitions.

Usage:
    python examples/ArchegosCollapse/Rag/analysis.py \\
        -c configs/ArchegosCollapse/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    load_simulation_data,
)

# Fallback string injected when no documents are retrieved — analysis-bases.md §3 Rag
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(
    agent_records: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Analyze RAG knowledge retrieval effects per agent.

    Counts rounds where retrieval succeeded vs. fell back to the standard
    fallback string. A high failure rate indicates the knowledge store needs
    more relevant documents.

    Args:
        agent_records: Mapping of agent_id → list of per-round record dicts.
            Each record may contain "rag_context" field.

    Returns:
        Dict mapping agent_id → retrieval statistics.
    """
    rag_stats: Dict[str, Any] = {}
    for agent_id, records in agent_records.items():
        total_rag_rounds = 0
        failure_rounds = 0
        success_rounds = 0
        for record in records:
            rag_context = record.get("rag_context")
            if rag_context is None:
                continue
            total_rag_rounds += 1
            if rag_context.strip() == _RAG_FALLBACK.strip():
                failure_rounds += 1
            else:
                success_rounds += 1
        if total_rag_rounds > 0:
            rag_stats[agent_id] = {
                "total_rag_rounds": total_rag_rounds,
                "retrieval_success_rounds": success_rounds,
                "retrieval_failure_rounds": failure_rounds,
                "retrieval_failure_rate": float(failure_rounds / total_rag_rounds),
            }
    return rag_stats


def _load_agent_records(record_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load per-round records for all non-market agents.

    Args:
        record_path: Base experiment record path.

    Returns:
        Dict mapping agent_id → list of round records.
    """
    agent_records: Dict[str, List[Dict[str, Any]]] = {}
    if not os.path.exists(record_path):
        return agent_records
    for agent_folder in os.listdir(record_path):
        agent_path = os.path.join(record_path, agent_folder)
        if not os.path.isdir(agent_path) or agent_folder == "market":
            continue
        records: List[Dict[str, Any]] = []
        for fname in sorted(os.listdir(agent_path)):
            if fname.endswith(".json"):
                with open(os.path.join(agent_path, fname), "r", encoding="utf-8") as f:
                    records.append(json.load(f))
        if records:
            agent_records[agent_folder] = records
    return agent_records


def main() -> None:
    """Run ArchegosCollapse Rag analysis: metrics + RAG knowledge-effect report.

    Implements analysis-bases.md §2 core metrics plus Rag-specific
    knowledge-retrieval analysis. Output written to
    EXPERIMENT/ArchegosCollapse/Rag/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze ArchegosCollapse Rag simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ArchegosCollapse/Rag/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_path = config["setting"]["record_path"]
    data = load_simulation_data(config)

    if not data["prices"]:
        print("No simulation data found. Run simulation first.")
        return

    metrics = calculate_metrics(data)
    agent_records = _load_agent_records(record_path)
    rag_stats = analyze_rag_knowledge_effect(agent_records)

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    # --- Visualization ---
    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "ArchegosCollapse Rag Simulation Analysis", fontsize=14, fontweight="bold"
    )

    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental", color="blue", linestyle="--"
    )
    axes[0, 0].set_title("Price vs Fundamental (Rag)")
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
        axes[1, 0].set_title("Round Returns (%) — Rag")
        axes[1, 0].grid(True, alpha=0.3)

    # RAG retrieval success rate bar chart
    if rag_stats:
        agent_ids = list(rag_stats.keys())
        success_rates = [
            1.0 - rag_stats[a]["retrieval_failure_rate"] for a in agent_ids
        ]
        colors = ["teal" if r >= 0.5 else "coral" for r in success_rates]
        bars = axes[1, 1].bar(
            range(len(agent_ids)), success_rates, color=colors, alpha=0.8
        )
        axes[1, 1].axhline(
            y=0.5, color="black", linestyle="--", linewidth=1.5, label="50% threshold"
        )
        axes[1, 1].set_xticks(range(len(agent_ids)))
        axes[1, 1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=7)
        axes[1, 1].set_ylim(0, 1.05)
        axes[1, 1].set_title("RAG Retrieval Success Rate by Agent")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis="y")
        for bar, rate in zip(bars, success_rates):
            axes[1, 1].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{rate:.0%}",
                ha="center",
                va="bottom",
                fontsize=7,
            )
    else:
        axes[1, 1].text(
            0.5,
            0.5,
            "No RAG data available",
            ha="center",
            va="center",
            transform=axes[1, 1].transAxes,
        )

    plt.tight_layout()
    plt.savefig(
        os.path.join(analysis_path, "archegsoscollapse_rag_analysis.png"), dpi=150
    )
    plt.close()

    # --- Save output JSONs ---
    summary = {"variant": "Rag", **metrics, "rag_knowledge_effect": rag_stats}
    with open(os.path.join(analysis_path, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(
        os.path.join(analysis_path, "rag_stats.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(rag_stats, f, indent=2)

    print("Rag analysis complete. Results in:", analysis_path)


__all__ = ["analyze_rag_knowledge_effect", "main"]

if __name__ == "__main__":
    main()
