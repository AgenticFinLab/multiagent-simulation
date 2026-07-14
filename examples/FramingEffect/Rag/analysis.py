"""Analysis utilities for the FramingEffect RAG variant."""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List

from masim.utils import load_config, load_results

from examples.FramingEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    framing_asymmetry_ratio,
    framing_deviation_index,
    framing_volume_impact,
    load_simulation_data,
    rational_correction_efficiency,
    volatility_amplification_factor,
    wealth_distribution_index,
)
from examples.standard_rule_analysis import (
    _load_data,
    analyze_standard_scenario as _analyze_standard_scenario,
)
from examples.FramingEffect.Rag.players import _RAG_FALLBACK


def analyze_rag_knowledge_effect(records: List[Dict[str, Any]]) -> Dict[str, float]:
    """Measure retrieval coverage and fallback frequency for FramingEffect RAG runs."""
    if not records:
        raise ValueError("records must not be empty")
    total = 0
    retrieved = 0
    fallback = 0
    for record in records:
        if "rag_context" not in record:
            continue
        total += 1
        context = record["rag_context"]
        if context == _RAG_FALLBACK:
            fallback += 1
        elif context:
            retrieved += 1
    if total == 0:
        raise ValueError("records contain no rag_context entries")
    return {
        "retrieval_success_rate": retrieved / total,
        "fallback_rate": fallback / total,
        "rag_context_observations": float(total),
    }


def _collect_rag_records(results: Any) -> List[Dict[str, Any]]:
    """Collect player turn payloads that may include `rag_context`."""
    records: List[Dict[str, Any]] = []
    for player in results.players_by_role("player").values():
        for payload in player.turns.payloads().values():
            if isinstance(payload, dict):
                records.append(payload)
    return records


def main() -> Dict[str, Any]:
    """Run FramingEffect RAG analysis with standard outputs plus RAG stats."""
    parser = argparse.ArgumentParser(description="Analyze FramingEffect RAG results")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FramingEffect/Rag/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = _analyze_standard_scenario("FramingEffect", data, config, output_dir)
    rag_stats = analyze_rag_knowledge_effect(_collect_rag_records(results))
    summary["metrics"]["rag_knowledge_effect"] = rag_stats

    rag_stats_path = os.path.join(output_dir, "rag_stats.json")
    with open(rag_stats_path, "w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"Saved FramingEffect RAG retrieval stats to {rag_stats_path}")
    return summary


__all__ = [
    "framing_deviation_index",
    "framing_asymmetry_ratio",
    "framing_volume_impact",
    "rational_correction_efficiency",
    "volatility_amplification_factor",
    "wealth_distribution_index",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "_collect_rag_records",
    "_RAG_FALLBACK",
    "main",
]


if __name__ == "__main__":
    main()
