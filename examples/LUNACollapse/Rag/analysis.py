#!/usr/bin/env python
"""LUNACollapse Rag analysis with standard outputs and RAG stats."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import numpy as np

from examples.LUNACollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from examples.standard_rule_analysis import analyze_standard_scenario
from masim.utils import load_config

DEFAULT_CONFIG = "configs/LUNACollapse/Rag/simulation.yml"
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(
    rag_contexts: Dict[str, Dict[int, Any]],
) -> Dict[str, Any]:
    """Calculate retrieval coverage from recorded RAG contexts."""
    rag_stats: Dict[str, Any] = {}
    for agent_id, round_contexts in rag_contexts.items():
        total = 0
        failures = 0
        for context in round_contexts.values():
            text = str(context)
            total += 1
            if text.strip() == _RAG_FALLBACK:
                failures += 1
        if total:
            rag_stats[agent_id] = {
                "total_rag_rounds": total,
                "retrieval_success_rounds": total - failures,
                "retrieval_failure_rounds": failures,
                "retrieval_failure_rate": float(failures / total),
            }

    rates = [
        value["retrieval_failure_rate"]
        for value in rag_stats.values()
        if "retrieval_failure_rate" in value
    ]
    if rates:
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(rates)),
            "max_retrieval_failure_rate": float(np.max(rates)),
        }
    return rag_stats


def main() -> Dict[str, Any]:
    """Run Rag analysis and write `rag_stats.json`."""
    parser = argparse.ArgumentParser(description="Analyze LUNACollapse Rag results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    analysis_path = Path(base_dir) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    data = load_simulation_data(config)
    summary = analyze_standard_scenario(
        "LUNACollapse",
        data,
        config,
        str(analysis_path),
    )
    rag_stats = analyze_rag_knowledge_effect(data["rag_contexts"])
    with (analysis_path / "rag_stats.json").open("w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)
    return summary


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
