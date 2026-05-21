#!/usr/bin/env python
"""GFC2008 Rag analysis with standard outputs and RAG stats."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import numpy as np

from examples.GFC2008.Rule.analysis import (
    SCENARIO,
    analyze_standard_scenario,
    calculate_metrics,
    create_visualizations,
    load_simulation_data as load_rule_simulation_data,
)
from masim.utils import load_config, load_results

DEFAULT_CONFIG = "configs/GFC2008/Rag/simulation.yml"
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load market data and recorded RAG contexts."""
    data = load_rule_simulation_data(config)
    results = load_results(config)
    rag_contexts = {}
    for pid, player in results.players_by_role("player").items():
        contexts = player.turns.field("rag_context")
        if contexts:
            rag_contexts[pid] = contexts
    data["rag_contexts"] = rag_contexts
    return data


def analyze_rag_knowledge_effect(
    rag_contexts: Dict[str, Dict[int, Any]],
) -> Dict[str, Any]:
    """Summarize RAG retrieval coverage for GFC2008 runs."""
    rag_stats: Dict[str, Any] = {}
    for agent_id, round_contexts in rag_contexts.items():
        total = 0
        failures = 0
        for context in round_contexts.values():
            total += 1
            if str(context).strip() == _RAG_FALLBACK:
                failures += 1
        if total:
            rag_stats[agent_id] = {
                "total_rag_rounds": total,
                "retrieval_success_rounds": total - failures,
                "retrieval_failure_rounds": failures,
                "retrieval_failure_rate": float(failures / total),
            }
    rates = [
        stats["retrieval_failure_rate"]
        for stats in rag_stats.values()
        if "retrieval_failure_rate" in stats
    ]
    if rates:
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(rates)),
            "max_retrieval_failure_rate": float(np.max(rates)),
        }
    return rag_stats


def main() -> None:
    """Run GFC2008 Rag analysis and write `rag_stats.json`."""
    parser = argparse.ArgumentParser(description="Analyze GFC2008 Rag results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    analysis_path = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    analyze_standard_scenario(SCENARIO, data, config, str(analysis_path))
    rag_stats = analyze_rag_knowledge_effect(data["rag_contexts"])
    with (analysis_path / "rag_stats.json").open("w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
