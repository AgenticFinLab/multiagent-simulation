#!/usr/bin/env python
"""South Sea Bubble Rag Simulation Analysis.

Produces the standardized output set required by create-example-skill:
summary.json, 00_investor_bids.png, 01_southseabubble_dynamics.png,
02_southseabubble_analysis.png, 03_summary.png, and rag_stats.json.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results

from examples.standard_rule_analysis import _load_data, analyze_standard_scenario

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def _load_rag_payloads(results: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Extract recorded RAG contexts by player and round."""
    payloads: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        round_payloads: Dict[int, Dict[str, Any]] = {}
        for round_num, rag_context in player.turns.field("rag_context").items():
            round_payloads[round_num] = {"rag_context": rag_context}
        if round_payloads:
            payloads[pid] = round_payloads
    return payloads


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Measure retrieval coverage for SouthSeaBubble Rag runs."""
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        failure_rounds = 0
        success_rounds = 0
        total_rag_rounds = 0

        for payload in round_payloads.values():
            rag_context = payload["rag_context"]
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


def main() -> Dict[str, Any]:
    """Run the standard analysis output contract plus RAG retrieval audit."""
    parser = argparse.ArgumentParser(description="Analyze SouthSeaBubble Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/SouthSeaBubble/Rag/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_standard_scenario("SouthSeaBubble", data, config, output_dir)

    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(results))
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)

    summary["rag_knowledge_effect"] = rag_stats
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


__all__ = ["analyze_rag_knowledge_effect", "main"]


if __name__ == "__main__":
    main()
