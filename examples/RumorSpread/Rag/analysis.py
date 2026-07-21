#!/usr/bin/env python
"""RumorSpread Rag analysis with retrieval-quality audit."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_results
from masim.utils.config import load_config
from masim.evaluation import write_universal_summary

from examples.RumorSpread.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def _load_rag_payloads(results: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Extract recorded RAG context by player and round."""
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
    """Measure retrieval coverage for RumorSpread Rag runs."""
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
    """Run RumorSpread analysis plus RAG retrieval audit."""
    parser = argparse.ArgumentParser(description="Analyze RumorSpread Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/RumorSpread/Rag/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)
    truth_value = config["players"]["environment"]["config"]["extras"][
        "rumor_truth_value"
    ]
    metrics = calculate_metrics(data, truth_value=truth_value)

    artifact_dir = os.path.dirname(config["setting"]["record_path"])
    analysis_dir = os.path.join(artifact_dir, "analysis")
    os.makedirs(analysis_dir, exist_ok=True)
    if data["belief"]:
        create_visualizations(data, analysis_dir, truth_value=truth_value)

    results = load_results(config)
    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(results))
    metrics["rag_knowledge_effect"] = rag_stats
    score = 1.0 if metrics["total_rounds"] > 0 else 0.0
    metrics["validation"] = {
        "score": score,
        "is_valid": bool(score >= 0.5),
        "criteria": {
            "Rumor State Recorded": {
                "value": metrics["total_rounds"],
                "target": "positive number of recorded belief rounds; 200 expected for full experiments",
                "score": score,
                "passed": bool(score >= 0.5),
            },
            "RAG Context Recorded": {
                "value": len(rag_stats),
                "target": "rag_context recorded for at least one player",
                "score": 1.0 if rag_stats else 0.0,
                "passed": bool(rag_stats),
            },
        },
        "interpretation": (
            "=== RUMOR SPREAD RAG SIMULATION VALIDATION: "
            f"{'VALID' if score >= 0.5 and rag_stats else 'INVALID'} ==="
        ),
    }

    summary = {
        "scenario": "RumorSpread",
        "mechanism": "Rag",
        "metrics": metrics,
        "validation": metrics["validation"],
    }

    with open(os.path.join(analysis_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)
    with open(os.path.join(analysis_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rag'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='RumorSpread',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["analyze_rag_knowledge_effect", "main"]


if __name__ == "__main__":
    main()
