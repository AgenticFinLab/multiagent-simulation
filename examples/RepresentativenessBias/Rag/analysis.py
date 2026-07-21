"""Analysis utilities for the RepresentativenessBias RAG variant."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from examples.RepresentativenessBias.Rule.analysis import (
    _load_data,
    analyze_representativenessbias_standard,
    calculate_metrics,
    compute_agent_attribution,
    compute_base_rate_neglect,
    compute_bayesian_correction,
    compute_bias_onset,
    compute_contrarian_profitability,
    compute_mispricing,
    compute_pattern_volume,
    create_visualizations,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
DEFAULT_CONFIG = "configs/RepresentativenessBias/Rag/simulation.yml"


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load standard simulation data plus recorded RAG contexts."""
    results = load_results(config)
    data = _load_data(results)
    rag_contexts: Dict[str, Dict[int, Any]] = {}
    for player_id, player in results.players_by_role("player").items():
        contexts = player.turns.field("rag_context")
        if contexts:
            rag_contexts[player_id] = contexts
    data["rag_contexts"] = rag_contexts
    return data


def analyze_rag_knowledge_effect(
    rag_contexts: Dict[str, Dict[int, Any]],
) -> Dict[str, Any]:
    """Measure retrieval coverage and fallback frequency for RepresentativenessBias."""
    per_agent: Dict[str, Any] = {}
    total_rounds = 0
    fallback_rounds = 0
    for agent_id, round_contexts in rag_contexts.items():
        agent_total = 0
        agent_fallback = 0
        for context in round_contexts.values():
            agent_total += 1
            if str(context).strip() == _RAG_FALLBACK:
                agent_fallback += 1
        if agent_total:
            total_rounds += agent_total
            fallback_rounds += agent_fallback
            per_agent[agent_id] = {
                "total_rag_rounds": agent_total,
                "retrieval_success_rounds": agent_total - agent_fallback,
                "retrieval_fallback_rounds": agent_fallback,
                "retrieval_success_rate": (agent_total - agent_fallback) / agent_total,
                "retrieval_fallback_rate": agent_fallback / agent_total,
            }
    if total_rounds == 0:
        raise ValueError("No recorded RAG contexts found")
    aggregate = {
        "total_rag_rounds": total_rounds,
        "retrieval_success_rounds": total_rounds - fallback_rounds,
        "retrieval_fallback_rounds": fallback_rounds,
        "retrieval_success_rate": (total_rounds - fallback_rounds) / total_rounds,
        "retrieval_fallback_rate": fallback_rounds / total_rounds,
        "target_met": (total_rounds - fallback_rounds) / total_rounds >= 0.70,
    }
    return {"aggregate": aggregate, "per_agent": per_agent}


def main() -> Dict[str, Any]:
    """Run RAG analysis and write standard outputs plus `rag_stats.json`."""
    parser = argparse.ArgumentParser(description="Analyze RepresentativenessBias RAG")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = analyze_representativenessbias_standard(data, config, str(output_dir))
    rag_stats = analyze_rag_knowledge_effect(data["rag_contexts"])
    summary["rag_knowledge_effect"] = rag_stats
    with (output_dir / "rag_stats.json").open("w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
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
        scenario='RepresentativenessBias',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "compute_base_rate_neglect",
    "compute_pattern_volume",
    "compute_mispricing",
    "compute_bayesian_correction",
    "compute_contrarian_profitability",
    "compute_bias_onset",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "_RAG_FALLBACK",
    "main",
]


if __name__ == "__main__":
    main()
