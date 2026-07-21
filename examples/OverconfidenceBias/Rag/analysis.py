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
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

DEFAULT_CONFIG = "configs/OverconfidenceBias/Rag/simulation.yml"
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
    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(load_results(config)))
    summary["rag_knowledge_effect"] = rag_stats
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as handle:
        json.dump(rag_stats, handle, indent=2)
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as handle:
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
        scenario='OverconfidenceBias',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "_load_rag_payloads",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
