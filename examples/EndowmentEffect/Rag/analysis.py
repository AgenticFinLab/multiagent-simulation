"""EndowmentEffect RAG analysis wrapper with retrieval coverage summary."""

import argparse
import json
import os
from typing import Any, Dict, List

import numpy as np

from masim.utils import load_config
from masim.evaluation import write_universal_summary

from examples.EndowmentEffect.Rule.analysis import (
    calculate_metrics as _calculate_rule_metrics,
    create_visualizations,
    endowment_premium_capture_rate,
    load_simulation_data,
    mean_absolute_deviation,
    price_deviation,
    validate_endowment_effect,
    volume_suppression_ratio,
)
from examples.EndowmentEffect.Rag.players import _RAG_FALLBACK


def deviation_half_life(price_history: List[float], fundamental: float) -> float:
    """Estimate absolute-deviation half-life with a log-linear decay fit."""
    deviations = np.abs(np.asarray(price_deviation(price_history, fundamental)))
    usable = np.flatnonzero(deviations > 0)
    if usable.size < 2:
        raise ValueError("at least two non-zero deviations are required")
    slope, _ = np.polyfit(usable, np.log(deviations[usable]), 1)
    if slope >= 0:
        return float("inf")
    return float(np.log(2.0) / -slope)


def portfolio_wealth_ratio(
    cash_history: List[float],
    position_history: List[float],
    final_price: float,
    initial_wealth: float,
) -> float:
    """Return final marked-to-market wealth divided by initial wealth."""
    if not cash_history or not position_history:
        raise ValueError("cash and position histories must not be empty")
    if initial_wealth <= 0:
        raise ValueError("initial_wealth must be positive")
    return (cash_history[-1] + position_history[-1] * final_price) / initial_wealth


def turnover_rate(
    trades_by_agent: List[float], mean_position: float, total_rounds: int
) -> float:
    """Return per-round units traded relative to the mean position."""
    if mean_position <= 0 or total_rounds <= 0:
        raise ValueError("mean_position and total_rounds must be positive")
    return sum(abs(value) for value in trades_by_agent) / (
        mean_position * total_rounds
    )


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
    if context_payloads == 0:
        raise ValueError("RAG payloads contain no rag_context field")
    retrieval_payloads = context_payloads - fallback_payloads
    fallback_rate = fallback_payloads / context_payloads
    return {
        "total_payloads": total_payloads,
        "context_payloads": context_payloads,
        "fallback_payloads": fallback_payloads,
        "retrieval_payloads": retrieval_payloads,
        "context_rate": context_payloads / total_payloads,
        "retrieval_rate": retrieval_payloads / context_payloads,
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
        scenario='EndowmentEffect',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "_RAG_FALLBACK",
    "price_deviation",
    "mean_absolute_deviation",
    "deviation_half_life",
    "volume_suppression_ratio",
    "endowment_premium_capture_rate",
    "portfolio_wealth_ratio",
    "turnover_rate",
    "analyze_rag_knowledge_effect",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "validate_endowment_effect",
    "main",
]
