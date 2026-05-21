#!/usr/bin/env python
"""OverconfidenceBias Rag analysis with standard outputs and RAG stats."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from examples.OverconfidenceBias.Rule.analysis import (
    analyze_overconfidencebias,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils import load_config

DEFAULT_CONFIG = "configs/OverconfidenceBias/Rag/simulation.yml"
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Calculate retrieval coverage from recorded RAG order payloads."""
    rag_stats: Dict[str, Any] = {}
    for agent_id, round_payloads in investor_payloads.items():
        total = 0
        failures = 0
        for payload in round_payloads.values():
            rag_context = payload["rag_context"]
            total += 1
            if rag_context.strip() == _RAG_FALLBACK:
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


def main(config_path: str | None = None) -> Dict[str, Any]:
    """Run OverconfidenceBias Rag analysis and write `rag_stats.json`."""
    if config_path is None:
        parser = argparse.ArgumentParser(description="OverconfidenceBias Rag analysis")
        parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
        args = parser.parse_args()
        config_path = args.config
    config = load_config(config_path)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)
    data = load_simulation_data(config)
    summary = analyze_overconfidencebias(data, config, output_dir)
    rag_stats = analyze_rag_knowledge_effect(data["investor_payloads"])
    summary["rag_knowledge_effect"] = rag_stats
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as handle:
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
