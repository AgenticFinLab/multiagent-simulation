#!/usr/bin/env python
"""Analysis entry point and metric contracts for the EchoChamber LLM variant."""

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from typing import Any

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np

from examples.EchoChamber.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils.config import load_config


def compute_polarization_amplification(polarization: Sequence[float]) -> float:
    """Return peak polarization divided by its positive initial level."""
    values = np.asarray(polarization, dtype=float)
    if values.size == 0 or values[0] <= 0:
        return 0.0
    return float(np.max(values) / max(float(values[0]), 0.01))


def compute_polarization_persistence(polarization: Sequence[float]) -> float:
    """Return mean polarization over the second half of the series."""
    values = np.asarray(polarization, dtype=float)
    if values.size == 0:
        return 0.0
    return float(np.mean(values[values.size // 2 :]))


def compute_cluster_separation(cluster_series: Sequence[float]) -> dict[str, float]:
    """Summarize maximum, final, and mean opinion-cluster separation."""
    values = np.asarray(cluster_series, dtype=float)
    if values.size == 0:
        return {"maximum": 0.0, "final": 0.0, "average": 0.0}
    return {
        "maximum": float(np.max(values)),
        "final": float(values[-1]),
        "average": float(np.mean(values)),
    }


def compute_polarize_activity(polarize_counts: Sequence[int]) -> float:
    """Return total polarizing actions across all recorded rounds."""
    return float(np.sum(np.asarray(polarize_counts, dtype=float)))


def compute_depolarize_activity(depolarize_counts: Sequence[int]) -> float:
    """Return total depolarizing actions across all recorded rounds."""
    return float(np.sum(np.asarray(depolarize_counts, dtype=float)))


def compute_opinion_dispersion(
    agent_opinions: Mapping[str, Sequence[float]],
) -> float:
    """Return the population standard deviation of final agent opinions."""
    finals = [float(series[-1]) for series in agent_opinions.values() if series]
    return float(np.std(finals)) if finals else 0.0


def compute_api_quality(
    actions: Sequence[Mapping[str, Any]], rag_contexts: Sequence[str] | None = None
) -> dict[str, float]:
    """Measure schema validity and optional retrieval coverage.

    ``rag_contexts`` is accepted to preserve the shared analysis contract; the
    LLM variant normally passes an empty sequence because it performs no retrieval.
    """
    valid_actions = 0
    fallback_events = 0
    for action in actions:
        action_type = action.get("action_type")
        intensity = action.get("intensity")
        reasoning = action.get("reasoning")
        valid_intensity = (
            isinstance(intensity, (int, float))
            and not isinstance(intensity, bool)
            and np.isfinite(intensity)
            and 0.0 <= float(intensity) <= 1.0
        )
        if (
            action_type in {"polarize", "neutral", "depolarize"}
            and valid_intensity
            and isinstance(reasoning, str)
            and bool(reasoning.strip())
        ):
            valid_actions += 1
        if bool(action.get("fallback_used", False)):
            fallback_events += 1

    total = len(actions)
    contexts = list(rag_contexts or ())
    retrieved = sum(bool(context.strip()) for context in contexts)
    return {
        "valid_action_rate": valid_actions / total if total else 0.0,
        "parse_failure_rate": (total - valid_actions) / total if total else 0.0,
        "fallback_rate": fallback_events / total if total else 0.0,
        "retrieval_coverage": retrieved / len(contexts) if contexts else 0.0,
    }


def main() -> None:
    """Analyze EchoChamber LLM records using the shared Rule visualizations."""
    parser = argparse.ArgumentParser(description="Analyze EchoChamber LLM results")
    parser.add_argument(
        "-c",
        "--config",
        default="configs/EchoChamber/LLM/simulation.yml",
        help="Path to the LLM simulation configuration file.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)
    if not data["polarization"]:
        print("No simulation data found. Run the LLM simulation first.")
        return

    metrics = calculate_metrics(data)
    analysis_dir = os.path.join(
        os.path.dirname(config["setting"]["record_path"]), "analysis"
    )
    os.makedirs(analysis_dir, exist_ok=True)
    create_visualizations(data, analysis_dir)

    metrics["llm_contract_metrics"] = {
        "opinion_dispersion": compute_opinion_dispersion(data["agent_opinions"]),
        "api_quality": "requires recorded action payloads; use compute_api_quality()",
    }
    summary = {
        "scenario": "EchoChamber",
        "variant": "LLM",
        "total_rounds": metrics.get("total_rounds", 0),
        "metrics": metrics,
    }
    summary_path = os.path.join(analysis_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
    print(f"EchoChamber LLM analysis saved to {analysis_dir}")


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "compute_polarization_amplification",
    "compute_polarization_persistence",
    "compute_cluster_separation",
    "compute_polarize_activity",
    "compute_depolarize_activity",
    "compute_opinion_dispersion",
    "compute_api_quality",
    "main",
]


if __name__ == "__main__":
    main()
