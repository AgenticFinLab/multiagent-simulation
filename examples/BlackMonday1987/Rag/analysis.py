#!/usr/bin/env python
"""BlackMonday1987 Rag Simulation Analysis

Rag-variant analysis for the BlackMonday1987 simulation.
Reuses all metric/validation functions from Rule/analysis.py and adds
RAG Knowledge Effect Analysis (analysis-bases.md §3 — Rag-specific dimension).

Rag-variant note (analysis-bases.md §4):
    Knowledge Reinforcement Events occur when retrieved context aligns with action.
    Knowledge Correction Events occur when retrieved context reverses default bias.
    Retrieval Failure Rounds: rounds where rag_context == fallback string.

Usage:
    python examples/BlackMonday1987/Rag/analysis.py \\
        -c configs/BlackMonday1987/Rag/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.BlackMonday1987.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_black_monday,
    _build_interpretation,
    analyze_black_monday,
)

# Fallback string injected when no documents are retrieved. Imported from
# players.py to preserve a single source of truth per polish-simulation-pipeline.
from examples.BlackMonday1987.Rag.players import _RAG_FALLBACK  # noqa: E402


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
    else:
        raise ValueError(
            "No rag_context values found in investor payloads; Rag records are incomplete"
        )

    return rag_stats


def main() -> None:
    """Run full BlackMonday1987 Rag analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_black_monday().
    Adds RAG Knowledge Effect Analysis (analysis-bases.md §3 Rag-specific).
    """
    parser = argparse.ArgumentParser(
        description="Analyze BlackMonday1987 Rag simulation results"
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
    summary = analyze_black_monday(data, config, output_dir)

    # Rag-specific: RAG knowledge effect analysis
    rag_stats = analyze_rag_knowledge_effect(data["investor_payloads"])
    summary["rag_knowledge_effect"] = rag_stats

    rag_stats_path = os.path.join(output_dir, "rag_stats.json")
    with open(rag_stats_path, "w", encoding="utf-8") as fh:
        json.dump(rag_stats, fh, indent=2)
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    agg = rag_stats["aggregate"]
    print(
        f"Mean RAG retrieval failure rate: "
        f"{agg['mean_retrieval_failure_rate']:.1%}"
    )
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
        scenario='BlackMonday1987',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["analyze_rag_knowledge_effect", "main"]

if __name__ == "__main__":
    main()
