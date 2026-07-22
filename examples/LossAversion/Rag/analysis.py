#!/usr/bin/env python
"""LossAversion Rag Simulation Analysis

Usage:
    python examples/LossAversion/Rag/analysis.py \
        -c configs/LossAversion/Rag/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from examples.LossAversion.Rule.analysis import (
    SCENARIO,
    analyze_lossaversion,
    calculate_metrics,
    create_visualizations,
    load_simulation_data as load_rule_simulation_data,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

DEFAULT_CONFIG = "configs/LossAversion/Rag/simulation.yml"
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load LossAversion data and recorded RAG context fields."""
    data = load_rule_simulation_data(config)
    results = load_results(config)
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
    """Measure retrieval coverage and fallback frequency for RAG decisions."""
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
        raise ValueError("No recorded RAG contexts found for LossAversion Rag analysis")

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
    """Run LossAversion Rag analysis and write `rag_stats.json`."""
    parser = argparse.ArgumentParser(description="Analyze LossAversion Rag results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = analyze_lossaversion(data, config, str(output_dir))
    rag_stats = analyze_rag_knowledge_effect(data["rag_contexts"])
    summary["rag_knowledge_effect"] = rag_stats

    with (output_dir / "rag_stats.json").open("w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
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
        scenario='LossAversion',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "_RAG_FALLBACK",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "main",
]

if __name__ == "__main__":
    main()
