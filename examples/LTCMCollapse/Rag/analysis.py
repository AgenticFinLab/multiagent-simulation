#!/usr/bin/env python
"""LTCMCollapse Rag analysis with standard outputs and RAG stats."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import numpy as np

from examples.LTCMCollapse.Rule.analysis import (
    _write_summary,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_metrics,
)
from masim.utils import load_config

DEFAULT_CONFIG = "configs/LTCMCollapse/Rag/simulation.yml"
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
                "retrieval_success_rate": float((total - failures) / total),
                "retrieval_failure_rate": float(failures / total),
                "meets_target": float((total - failures) / total) >= 0.70,
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


def main() -> None:
    """Run Rag analysis and write `rag_stats.json`."""
    parser = argparse.ArgumentParser(description="Analyze LTCMCollapse Rag results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)
    validation = validate_metrics(metrics)
    analysis_path = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    create_visualizations(data, str(analysis_path))
    _write_summary(analysis_path, metrics, validation)
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
