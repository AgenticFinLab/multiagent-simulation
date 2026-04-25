#!/usr/bin/env python
"""ConfirmationBias Rag Simulation Analysis

Rag-variant analysis for the ConfirmationBias simulation.
Reuses core metric functions from Rule/analysis.py and adds
RAG knowledge-effect analysis specific to the Rag variant.
See analysis-bases.md for metric definitions.

Usage:
    python examples/ConfirmationBias/Rag/analysis.py \\
        -c configs/ConfirmationBias/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.ConfirmationBias.Rule.analysis import (
    calculate_metrics,
    load_simulation_data,
)

__all__ = ["analyze_rag_knowledge_effect", "main"]

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(
    agent_records: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute RAG knowledge retrieval statistics for Rag agents.

    Checks rag_context field in each per-round record to determine
    whether the KnowledgeStore returned useful content.
    Target retrieval success rate >= 0.70.

    Args:
        agent_records: Mapping of agent_id → list of per-round record dicts.
            Each record may contain "rag_context" key.

    Returns:
        Dict mapping agent_id → retrieval statistics.
    """
    rag_effect: Dict[str, Any] = {}
    for agent_id, records in agent_records.items():
        total_rag_rounds = 0
        success_rounds = 0
        failure_rounds = 0
        for record in records:
            rag_context = record.get("rag_context")
            if rag_context is not None:
                total_rag_rounds += 1
                if rag_context != _RAG_FALLBACK and rag_context.strip():
                    success_rounds += 1
                else:
                    failure_rounds += 1
        if total_rag_rounds > 0:
            retrieval_rate = float(success_rounds / total_rag_rounds)
            rag_effect[agent_id] = {
                "retrieval_success_rate": retrieval_rate,
                "success_rounds": success_rounds,
                "failure_rounds": failure_rounds,
                "total_rag_rounds": total_rag_rounds,
                "meets_target": (retrieval_rate >= 0.70),
            }
    return rag_effect


def _load_agent_records(record_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load per-round records for all non-market agents."""
    agent_records: Dict[str, List[Dict[str, Any]]] = {}
    if not os.path.exists(record_path):
        return agent_records
    for agent_folder in os.listdir(record_path):
        agent_path = os.path.join(record_path, agent_folder)
        if not os.path.isdir(agent_path) or agent_folder in ("market", "analysis"):
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
    """Run ConfirmationBias Rag analysis: metrics + RAG knowledge effect.

    Implements analysis-bases.md §2 core metrics plus Rag-specific
    retrieval analysis. Output written to
    EXPERIMENT/ConfirmationBias/Rag/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze ConfirmationBias Rag simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/ConfirmationBias/Rag/simulation.yml",
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
    rag_effect = analyze_rag_knowledge_effect(agent_records)

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "ConfirmationBias Rag Simulation Analysis", fontsize=14, fontweight="bold"
    )

    axes[0, 0].plot(rounds, prices, label="Asset Price", color="steelblue")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental", color="orange", linestyle="--"
    )
    axes[0, 0].set_title("Asset Price vs Fundamental (Rag)")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    if len(fundamentals) > 0 and np.any(fundamentals > 0):
        deviation_pct = (
            (prices - fundamentals)
            / np.where(fundamentals > 0, fundamentals, 1.0)
            * 100
        )
        axes[0, 1].plot(rounds, deviation_pct, color="crimson")
        axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0, 1].axhline(
            y=2, color="orange", linestyle=":", alpha=0.7, label="+2% bias threshold"
        )
        axes[0, 1].axhline(y=-2, color="orange", linestyle=":", alpha=0.7)
        axes[0, 1].set_title("Price Deviation from Fundamental (%)")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

    if len(prices) > 1:
        returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0) * 100
        axes[1, 0].plot(rounds[1:], returns, color="darkorange", alpha=0.7)
        axes[1, 0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1, 0].set_title("Round Returns (%) — Rag")
        axes[1, 0].grid(True, alpha=0.3)

    # RAG retrieval success rate bar chart
    if rag_effect:
        agent_ids = list(rag_effect.keys())
        rates = [rag_effect[a]["retrieval_success_rate"] for a in agent_ids]
        colors = ["green" if r >= 0.70 else "red" for r in rates]
        bars = axes[1, 1].bar(range(len(agent_ids)), rates, color=colors, alpha=0.8)
        axes[1, 1].axhline(
            y=0.70, color="black", linestyle="--", linewidth=1.5, label="Target (70%)"
        )
        axes[1, 1].set_xticks(range(len(agent_ids)))
        axes[1, 1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=7)
        axes[1, 1].set_ylim(0, 1.05)
        axes[1, 1].set_title("RAG Retrieval Success Rate by Agent (target ≥70%)")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis="y")
        for bar, rate in zip(bars, rates):
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
            "No RAG retrieval data",
            ha="center",
            va="center",
            transform=axes[1, 1].transAxes,
        )

    plt.tight_layout()
    plt.savefig(
        os.path.join(analysis_path, "confirmationbias_rag_analysis.png"), dpi=150
    )
    plt.close()

    summary = {"variant": "Rag", **metrics, "rag_knowledge_effect": rag_effect}
    with open(os.path.join(analysis_path, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(
        os.path.join(analysis_path, "rag_knowledge_effect.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(rag_effect, f, indent=2)

    print("Rag analysis complete. Results in:", analysis_path)


if __name__ == "__main__":
    main()
