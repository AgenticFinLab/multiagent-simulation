#!/usr/bin/env python
"""AnchoringEffect Rag Simulation Analysis (registry-driven thin wrapper).

The Rag variant adds a retrieval-augmented LLM persona on top of the standard
LLM pipeline. Core analysis (data load → registry metrics → validation →
9-panel dashboards) is delegated to
:mod:`examples.AnchoringEffect.Rule.analysis`. This module supplies the
variant label and the Rag-specific knowledge-effect diagnostics from
analysis-bases.md §3.

Rag-specific notes (analysis-bases.md §4):
    * Knowledge Reinforcement Events occur when retrieved context aligns with
      action.
    * Knowledge Correction Events occur when retrieved context reverses default
      bias.
    * Retrieval Failure Rounds: rounds where ``rag_context`` equals the
      fallback string.
    * Compare versus the RuleLLM baseline for the net RAG knowledge effect.

Usage::

    python examples/AnchoringEffect/Rag/analysis.py \
        -c configs/AnchoringEffect/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results
from masim.agents import RAG_FALLBACK_MESSAGE

from examples.AnchoringEffect.Rule.analysis import (
    _load_data,
    analyze_anchoring,
)

VARIANT = "Rag"


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Per-agent RAG retrieval success / failure tally.

    Returns a dict with one entry per agent plus an ``aggregate`` summary when
    at least one agent contributed RAG-context records.
    """
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        failure_rounds = 0
        success_rounds = 0
        total_rag_rounds = 0

        for payload in round_payloads.values():
            rag_context = payload.get("rag_context")
            if rag_context is None:
                continue
            total_rag_rounds += 1
            if rag_context.strip() == RAG_FALLBACK_MESSAGE.strip():
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

    agents_with_data = [
        v for v in rag_stats.values() if "retrieval_failure_rate" in v
    ]
    if agents_with_data:
        failure_rates = [v["retrieval_failure_rate"] for v in agents_with_data]
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(failure_rates)),
            "max_retrieval_failure_rate": float(np.max(failure_rates)),
        }

    return rag_stats


def main() -> None:
    """Run full AnchoringEffect Rag analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect Rag simulation results"
    )
    parser.add_argument(
        "-c", "--config", type=str, required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)

    summary = analyze_anchoring(data, config, output_dir, variant=VARIANT)

    # Rag-specific augmentation.
    rag_stats = analyze_rag_knowledge_effect(data["investor_payloads"])
    summary["rag_knowledge_effect"] = rag_stats

    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(rag_stats, fh, indent=2)
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    agg = rag_stats.get("aggregate")
    if agg:
        print(
            f"Mean RAG retrieval failure rate: "
            f"{agg['mean_retrieval_failure_rate']:.1%}"
        )
    return summary


if __name__ == "__main__":
    main()
