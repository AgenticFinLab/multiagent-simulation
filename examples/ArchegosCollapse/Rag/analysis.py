#!/usr/bin/env python
"""ArchegosCollapse Rag Simulation Analysis

Rag-variant analysis for the ArchegosCollapse simulation.
Reuses all metric/validation functions from Rule/analysis.py and adds
RAG Knowledge Effect Analysis (analysis-bases.md §3 — Rag-specific dimension).

Rag-variant note (analysis-bases.md §4):
    Knowledge Reinforcement Events occur when retrieved context aligns with action.
    Knowledge Correction Events occur when retrieved context reverses default bias.
    Retrieval Failure Rounds: rounds where rag_context == fallback string.
    Compare vs. RuleLLM baseline for net RAG knowledge effect.

Usage:
    python examples/ArchegosCollapse/Rag/analysis.py \\
        -c configs/ArchegosCollapse/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results

from examples.ArchegosCollapse.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_archegos_collapse,
    _build_interpretation,
    analyze_archegos_collapse,
)

# Fallback string injected when no documents are retrieved (Rag/players.py)
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


def main() -> None:
    """Run full ArchegosCollapse Rag analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_archegos_collapse().
    Adds RAG Knowledge Effect Analysis (analysis-bases.md §3 Rag-specific).
    """
    parser = argparse.ArgumentParser(
        description="Analyze ArchegosCollapse Rag simulation results"
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
    summary = analyze_archegos_collapse(data, config, output_dir)

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


__all__ = ["analyze_rag_knowledge_effect", "main"]

if __name__ == "__main__":
    main()
