#!/usr/bin/env python
"""BlackMonday1987 RuleLLM Simulation Analysis

RuleLLM-variant analysis for the BlackMonday1987 simulation.
Reuses core metric functions from Rule/analysis.py and adds
rule-adherence analysis specific to the RuleLLM hybrid variant.
See analysis-bases.md for metric definitions.

Usage:
    python examples/BlackMonday1987/RuleLLM/analysis.py \\
        -c configs/BlackMonday1987/RuleLLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.BlackMonday1987.Rule.analysis import (
    calculate_metrics,
    load_simulation_data,
)


def analyze_rule_adherence(
    agent_records: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute rule-adherence rate for RuleLLM agents.

    Compares LLM-produced action against the expected rule action stored
    in record["rule_action"]. Target adherence rate >= 0.80.

    Args:
        agent_records: Mapping of agent_id → list of per-round record dicts.
            Each record should contain "action" and optionally "rule_action".

    Returns:
        Dict mapping agent_id → adherence statistics.
    """
    adherence: Dict[str, Any] = {}
    for agent_id, records in agent_records.items():
        total = 0
        matching = 0
        for record in records:
            rule_action = record.get("rule_action")
            llm_action = record.get("action")
            if rule_action is not None and llm_action is not None:
                total += 1
                if rule_action == llm_action:
                    matching += 1
        if total > 0:
            adherence[agent_id] = {
                "adherence_rate": float(matching / total),
                "matching_rounds": matching,
                "total_rounds": total,
                "meets_target": (matching / total >= 0.80),
            }
    return adherence


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
    """Run BlackMonday1987 RuleLLM analysis: metrics + rule-adherence report.

    Implements analysis-bases.md §2 core metrics plus RuleLLM-specific
    rule-adherence analysis (target ≥80%). Output written to
    EXPERIMENT/BlackMonday1987/RuleLLM/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze BlackMonday1987 RuleLLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/BlackMonday1987/RuleLLM/simulation.yml",
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
    rule_adherence = analyze_rule_adherence(agent_records)

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    prices = np.array(data["prices"])
    fundamentals = np.array(data["fundamentals"])
    rounds = np.arange(len(prices))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "BlackMonday1987 RuleLLM Simulation Analysis", fontsize=14, fontweight="bold"
    )

    axes[0, 0].plot(rounds, prices, label="Price", color="darkred")
    axes[0, 0].plot(
        rounds, fundamentals, label="Fundamental", color="navy", linestyle="--"
    )
    axes[0, 0].set_title("Price vs Fundamental (RuleLLM)")
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
        axes[1, 0].plot(rounds[1:], returns, color="firebrick", alpha=0.8)
        axes[1, 0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1, 0].set_title("Round Returns (%) — RuleLLM")
        axes[1, 0].grid(True, alpha=0.3)

    if rule_adherence:
        agent_ids = list(rule_adherence.keys())
        rates = [rule_adherence[a]["adherence_rate"] for a in agent_ids]
        colors = ["green" if r >= 0.80 else "red" for r in rates]
        bars = axes[1, 1].bar(range(len(agent_ids)), rates, color=colors, alpha=0.8)
        axes[1, 1].axhline(
            y=0.80, color="black", linestyle="--", linewidth=1.5, label="Target (80%)"
        )
        axes[1, 1].set_xticks(range(len(agent_ids)))
        axes[1, 1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=7)
        axes[1, 1].set_ylim(0, 1.05)
        axes[1, 1].set_title("Rule Adherence Rate by Agent (target ≥80%)")
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
            "No rule-adherence data",
            ha="center",
            va="center",
            transform=axes[1, 1].transAxes,
        )

    plt.tight_layout()
    plt.savefig(
        os.path.join(analysis_path, "blackmonday1987_rulellm_analysis.png"), dpi=150
    )
    plt.close()

    summary = {"variant": "RuleLLM", **metrics, "rule_adherence": rule_adherence}
    with open(os.path.join(analysis_path, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(
        os.path.join(analysis_path, "rule_adherence.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(rule_adherence, f, indent=2)

    print("RuleLLM analysis complete. Results in:", analysis_path)


__all__ = ["analyze_rule_adherence", "main"]

if __name__ == "__main__":
    main()
