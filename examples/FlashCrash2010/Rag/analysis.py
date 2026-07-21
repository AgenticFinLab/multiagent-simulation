#!/usr/bin/env python
"""FlashCrash2010 Rag Simulation Analysis.

Extends the Rule-variant pipeline with RAG retrieval diagnostics
(``analyze_rag_knowledge_effect``) and writes both ``summary.json`` and
``rag_stats.json`` to the analysis output directory.

The Rag investors record two extra decision-payload fields:

    * ``rag_context``               — the retrieved documents (or fallback text)
    * ``liquidity_field_missing``   — whether the LLM omitted the
                                      ``provides_liquidity`` field

Both are consumed here to score retrieval coverage.

Usage
-----
    python examples/FlashCrash2010/Rag/analysis.py \
        -c configs/FlashCrash2010/Rag/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.FlashCrash2010.Rule.analysis import (
    STANDARD_OUTPUT_FILES,
    _write_standard_named_outputs,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_flashcrash2010,
)
from examples.FlashCrash2010.Rag.players import _RAG_FALLBACK


def _load_rag_payloads(results: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Collect ``rag_context`` and ``liquidity_field_missing`` per-round."""
    payloads: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        round_payloads: Dict[int, Dict[str, Any]] = {}
        for round_num, rag_context in player.turns.field("rag_context").items():
            round_payloads[round_num] = {"rag_context": rag_context}
        for round_num, missing in player.turns.field(
            "liquidity_field_missing"
        ).items():
            round_payloads.setdefault(round_num, {})[
                "liquidity_field_missing"
            ] = bool(missing)
        if round_payloads:
            payloads[pid] = round_payloads
    return payloads


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Measure per-agent retrieval coverage vs the ``_RAG_FALLBACK`` sentinel.

    Any round whose ``rag_context`` equals ``_RAG_FALLBACK`` is scored as a
    retrieval failure — the KnowledgeStore returned nothing usable.
    """
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        failure_rounds = 0
        success_rounds = 0
        total_rag_rounds = 0
        liquidity_field_missing_rounds = 0

        for payload in round_payloads.values():
            if payload.get("liquidity_field_missing"):
                liquidity_field_missing_rounds += 1

            rag_context = payload.get("rag_context")
            if rag_context is None:
                continue
            total_rag_rounds += 1
            if str(rag_context).strip() == _RAG_FALLBACK.strip():
                failure_rounds += 1
            else:
                success_rounds += 1

        if total_rag_rounds == 0:
            rag_stats[agent_id] = {
                "note": "no rag_context field in records",
                "liquidity_field_missing_rounds": liquidity_field_missing_rounds,
            }
            continue

        rag_stats[agent_id] = {
            "total_rag_rounds": total_rag_rounds,
            "retrieval_success_rounds": success_rounds,
            "retrieval_failure_rounds": failure_rounds,
            "retrieval_failure_rate": float(failure_rounds / total_rag_rounds),
            "liquidity_field_missing_rounds": liquidity_field_missing_rounds,
        }

    agents_with_data = [v for v in rag_stats.values() if "retrieval_failure_rate" in v]
    if agents_with_data:
        failure_rates = [v["retrieval_failure_rate"] for v in agents_with_data]
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(failure_rates)),
            "max_retrieval_failure_rate": float(np.max(failure_rates)),
            "num_agents": len(agents_with_data),
        }

    return rag_stats


def analyze_rag(config_path: str) -> Dict[str, Any]:
    """Run the Rule pipeline, add Rag retrieval audit, persist both artefacts."""
    config = load_config(config_path)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = load_simulation_data(config, results)
    metrics = calculate_metrics(data, config)
    validation = validate_flashcrash2010(metrics)

    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)

    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(results))
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2, default=str)

    summary: Dict[str, Any] = {
        "scenario": "FlashCrash2010",
        "variant": "Rag",
        "config_path": config_path,
        **metrics,
        "validation": validation,
        "rag_knowledge_effect": rag_stats,
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    return summary


def main() -> Dict[str, Any]:
    """CLI entry point for the Rag variant."""
    parser = argparse.ArgumentParser(
        description="Analyze FlashCrash2010 Rag simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/Rag/simulation.yml",
    )
    args = parser.parse_args()
    print("=" * 72)
    print("FlashCrash2010 Rag Analysis")
    print("=" * 72)
    summary = analyze_rag(args.config)
    print(f"max_drawdown         = {summary['max_drawdown']:.4f}")
    print(f"recovery_time        = {summary['recovery_time']}")
    agg = summary["rag_knowledge_effect"].get("aggregate", {})
    if agg:
        print(
            f"mean_retrieval_failure_rate = {agg['mean_retrieval_failure_rate']:.3f}"
        )
    print(summary["validation"]["interpretation"])
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
        scenario='FlashCrash2010',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "analyze_rag_knowledge_effect",
    "analyze_rag",
    "main",
]


if __name__ == "__main__":
    main()
