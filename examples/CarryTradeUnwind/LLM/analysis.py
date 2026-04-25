#!/usr/bin/env python
"""CarryTradeUnwind LLM Simulation Analysis

LLM-variant analysis for the CarryTradeUnwind simulation.
Reuses core metric functions from Rule/analysis.py and adds
LLM-specific behavior visualization.
See analysis-bases.md for metric definitions.

Usage:
    python examples/CarryTradeUnwind/LLM/analysis.py \\
        -c configs/CarryTradeUnwind/LLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.CarryTradeUnwind.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)

__all__ = ["main"]


def _load_agent_actions(record_path: str) -> Dict[str, List[str]]:
    """Load per-round action sequences for all non-market agents."""
    agent_actions: Dict[str, List[str]] = {}
    if not os.path.exists(record_path):
        return agent_actions
    for agent_folder in os.listdir(record_path):
        agent_path = os.path.join(record_path, agent_folder)
        if not os.path.isdir(agent_path) or agent_folder in ("market", "analysis"):
            continue
        actions: List[str] = []
        for fname in sorted(os.listdir(agent_path)):
            if fname.endswith(".json"):
                with open(os.path.join(agent_path, fname), "r", encoding="utf-8") as f:
                    rec = json.load(f)
                actions.append(rec.get("action", "hold"))
        if actions:
            agent_actions[agent_folder] = actions
    return agent_actions


def main() -> None:
    """Run CarryTradeUnwind LLM analysis: metrics + LLM action distribution.

    Implements analysis-bases.md §2 core metrics plus LLM-specific
    action-frequency visualization. Output written to
    EXPERIMENT/CarryTradeUnwind/LLM/records/analysis/.
    """
    parser = argparse.ArgumentParser(
        description="Analyze CarryTradeUnwind LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/CarryTradeUnwind/LLM/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_path = config["setting"]["record_path"]
    data = load_simulation_data(config)

    if not data["prices"]:
        print("No simulation data found. Run simulation first.")
        return

    metrics = calculate_metrics(data)
    agent_actions = _load_agent_actions(record_path)

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    # Core 2×2 plot (reuse Rule visualizations)
    create_visualizations(data, analysis_path, variant="LLM")

    # LLM action distribution plot
    if agent_actions:
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.suptitle("CarryTradeUnwind LLM — Action Distribution by Agent", fontsize=12)
        x = np.arange(len(agent_actions))
        width = 0.25
        agents = list(agent_actions.keys())
        buy_counts = [agent_actions[a].count("buy") for a in agents]
        sell_counts = [agent_actions[a].count("sell") for a in agents]
        hold_counts = [agent_actions[a].count("hold") for a in agents]
        ax.bar(x - width, buy_counts, width, label="buy", color="green", alpha=0.8)
        ax.bar(x, sell_counts, width, label="sell", color="red", alpha=0.8)
        ax.bar(x + width, hold_counts, width, label="hold", color="gray", alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(agents, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("Number of Rounds")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(
            os.path.join(analysis_path, "carrytradeunwind_llm_actions.png"), dpi=150
        )
        plt.close()

    summary = {"variant": "LLM", **metrics}
    with open(os.path.join(analysis_path, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("LLM analysis complete. Results in:", analysis_path)


if __name__ == "__main__":
    main()
