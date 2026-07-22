#!/usr/bin/env python
"""Echo Chamber Rag Simulation Analysis."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from typing import Any, Dict

import numpy as np

from masim.utils import load_results
from masim.utils.config import load_config
from masim.evaluation import write_universal_summary

from examples.EchoChamber.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from examples.EchoChamber.Rag.players import _RAG_FALLBACK


def compute_polarization_amplification(polarization: Sequence[float]) -> float:
    """Return peak polarization divided by its positive initial level."""
    values = np.asarray(polarization, dtype=float)
    if values.size == 0 or values[0] <= 0:
        return 0.0
    return float(np.max(values) / max(float(values[0]), 0.01))


def compute_polarization_persistence(polarization: Sequence[float]) -> float:
    """Return mean polarization over the second half of the series."""
    values = np.asarray(polarization, dtype=float)
    return float(np.mean(values[values.size // 2 :])) if values.size else 0.0


def compute_cluster_separation(cluster_series: Sequence[float]) -> Dict[str, float]:
    """Summarize maximum, final, and average cluster separation."""
    values = np.asarray(cluster_series, dtype=float)
    if values.size == 0:
        return {"maximum": 0.0, "final": 0.0, "average": 0.0}
    return {
        "maximum": float(np.max(values)),
        "final": float(values[-1]),
        "average": float(np.mean(values)),
    }


def compute_polarize_activity(polarize_counts: Sequence[int]) -> float:
    """Return total polarizing actions across recorded rounds."""
    return float(np.sum(np.asarray(polarize_counts, dtype=float)))


def compute_depolarize_activity(depolarize_counts: Sequence[int]) -> float:
    """Return total depolarizing actions across recorded rounds."""
    return float(np.sum(np.asarray(depolarize_counts, dtype=float)))


def compute_opinion_dispersion(
    agent_opinions: Mapping[str, Sequence[float]],
) -> float:
    """Return the population standard deviation of final agent opinions."""
    finals = [float(series[-1]) for series in agent_opinions.values() if series]
    return float(np.std(finals)) if finals else 0.0


def compute_api_quality(
    actions: Sequence[Mapping[str, Any]], rag_contexts: Sequence[str]
) -> Dict[str, float]:
    """Measure action-schema validity and successful retrieval coverage."""
    valid_actions = 0
    for action in actions:
        intensity = action.get("intensity")
        valid_intensity = (
            isinstance(intensity, (int, float))
            and not isinstance(intensity, bool)
            and np.isfinite(intensity)
            and 0.0 <= float(intensity) <= 1.0
        )
        if (
            action.get("action_type") in {"polarize", "neutral", "depolarize"}
            and valid_intensity
            and isinstance(action.get("reasoning"), str)
            and bool(action["reasoning"].strip())
        ):
            valid_actions += 1

    contexts = list(rag_contexts)
    retrieved = sum(
        bool(context.strip()) and context.strip() != _RAG_FALLBACK
        for context in contexts
    )
    fallback_events = sum(context.strip() == _RAG_FALLBACK for context in contexts)
    total = len(actions)
    return {
        "valid_action_rate": valid_actions / total if total else 0.0,
        "parse_failure_rate": (total - valid_actions) / total if total else 0.0,
        "fallback_rate": fallback_events / len(contexts) if contexts else 0.0,
        "retrieval_coverage": retrieved / len(contexts) if contexts else 0.0,
    }


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
    agent_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Measure retrieval coverage for EchoChamber Rag runs."""
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in agent_payloads.items():
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
    """Run EchoChamber analysis plus RAG retrieval audit."""
    parser = argparse.ArgumentParser(description="Analyze EchoChamber Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EchoChamber/Rag/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)

    analysis_dir = os.path.join(
        os.path.dirname(config["setting"]["record_path"]), "analysis"
    )
    os.makedirs(analysis_dir, exist_ok=True)
    if data["polarization"]:
        create_visualizations(data, analysis_dir)

    results = load_results(config)
    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(results))
    metrics["rag_knowledge_effect"] = rag_stats
    total_rounds = metrics["total_rounds"]
    validation = {
        "score": 1.0 if total_rounds > 0 else 0.0,
        "is_valid": bool(total_rounds > 0),
        "criteria": {
            "Echo Chamber State Recorded": {
                "value": total_rounds,
                "target": "positive number of recorded opinion rounds; 200 expected for full experiments",
                "score": 1.0 if total_rounds > 0 else 0.0,
                "passed": bool(total_rounds > 0),
            }
        },
        "interpretation": "=== ECHO CHAMBER RAG SIMULATION VALIDATION ===",
    }
    metrics["validation"] = validation
    summary = {
        "scenario": "EchoChamber",
        "variant": "Rag",
        "total_rounds": total_rounds,
        "metrics": metrics,
        "validation": validation,
    }

    with open(os.path.join(analysis_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)
    with open(os.path.join(analysis_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
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
        scenario='EchoChamber',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "compute_polarization_amplification",
    "compute_polarization_persistence",
    "compute_cluster_separation",
    "compute_polarize_activity",
    "compute_depolarize_activity",
    "compute_opinion_dispersion",
    "compute_api_quality",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
