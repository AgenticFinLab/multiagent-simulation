"""Analysis utilities for the RepresentativenessBias RAG variant."""

from typing import Any, Dict, List

from examples.RepresentativenessBias.Rule.analysis import (
    calculate_metrics,
    compute_agent_attribution,
    compute_base_rate_neglect,
    compute_bayesian_correction,
    compute_bias_onset,
    compute_contrarian_profitability,
    compute_mispricing,
    compute_pattern_volume,
    create_visualizations,
    load_simulation_data,
)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(records: List[Dict[str, Any]]) -> Dict[str, float]:
    """Measure retrieval coverage and fallback frequency for RepresentativenessBias."""
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
]
