"""EndowmentEffect RAG analysis wrapper with retrieval coverage summary."""

import argparse
import json
import os
from typing import Any, Dict, List

from masim.utils import load_config

from examples.EndowmentEffect.Rule.analysis import (
    calculate_metrics as _calculate_rule_metrics,
    create_visualizations,
    load_simulation_data,
    validate_endowment_effect,
)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(trades: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Return retrieval-context coverage over RAG order payloads."""
    total_payloads = 0
    context_payloads = 0
    fallback_payloads = 0
    for payloads in trades.values():
        for payload in payloads:
            total_payloads += 1
            if "rag_context" not in payload:
                continue
            context_payloads += 1
            if payload["rag_context"].strip() == _RAG_FALLBACK:
                fallback_payloads += 1
    if total_payloads == 0:
        raise ValueError("No RAG payloads found")
    fallback_rate = fallback_payloads / context_payloads if context_payloads else 0.0
    return {
        "total_payloads": total_payloads,
        "context_payloads": context_payloads,
        "fallback_payloads": fallback_payloads,
        "retrieval_rate": context_payloads / total_payloads,
        "fallback_rate": fallback_rate,
    }


def calculate_metrics(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate shared metrics plus RAG retrieval health."""
    metrics = _calculate_rule_metrics(data, config)
    metrics["rag_knowledge_effect"] = analyze_rag_knowledge_effect(data["trades"])
    return metrics


def main() -> Dict[str, Any]:
    """Run EndowmentEffect RAG analysis."""
    parser = argparse.ArgumentParser(description="Analyze EndowmentEffect RAG simulation")
    parser.add_argument("-c", "--config", required=True, help="Path to simulation YAML")
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    output_dir = os.path.join(os.path.dirname(record_dir), "analysis")
    data = load_simulation_data(config)
    metrics = calculate_metrics(data, config)
    validation = validate_endowment_effect(metrics)
    create_visualizations(data, metrics, output_dir)

    rag_stats_path = os.path.join(output_dir, "rag_stats.json")
    with open(rag_stats_path, "w", encoding="utf-8") as f:
        json.dump(metrics["rag_knowledge_effect"], f, indent=2)

    summary = {
        "scenario": "EndowmentEffect",
        "variant": "Rag",
        "total_rounds": metrics["total_rounds"],
        "metrics": metrics,
        "validation": validation,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nVALIDATION: {validation['interpretation']}")
    print(f"Fit Score: {validation['score']:.1%}")
    print(f"Saved EndowmentEffect RAG retrieval stats to {rag_stats_path}")
    print(f"Saved EndowmentEffect RAG analysis summary to {summary_path}")
    return summary


if __name__ == "__main__":
    main()


__all__ = ["_RAG_FALLBACK", "analyze_rag_knowledge_effect", "calculate_metrics", "main"]
