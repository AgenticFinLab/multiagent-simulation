"""Analysis entry point and metric exports for the LLM variant.

Wraps the Rule pipeline and injects the LLM ``action-distribution``
audit required by ``implement-simulation-skill §7.2``.
"""

import argparse
import json
import os
from typing import Any, Dict, List

import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution
from masim.evaluation.llm_harness import finalize_llm_analysis

from examples.EndowmentEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    endowment_premium_capture_rate,
    load_simulation_data,
    mean_absolute_deviation,
    price_deviation,
    validate_endowment_effect,
    volume_suppression_ratio,
)


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


def main() -> Dict[str, Any]:
    """Run EndowmentEffect LLM analysis (Rule pipeline + action-distribution)."""
    parser = argparse.ArgumentParser(description="Analyze EndowmentEffect LLM simulation")
    parser.add_argument("-c", "--config", required=True, help="Path to simulation YAML")
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    output_dir = os.path.join(os.path.dirname(record_dir), "analysis")
    os.makedirs(output_dir, exist_ok=True)

    data = load_simulation_data(config)
    metrics = calculate_metrics(data, config)
    validation = validate_endowment_effect(metrics)
    create_visualizations(data, metrics, output_dir)

    try:
        results = load_results(config)
        action_dist = analyze_action_distribution(results)
    except Exception as exc:  # noqa: BLE001 — never fail the whole analysis
        print(f"[warn] action-distribution audit failed: {exc}")
        action_dist = analyze_action_distribution({})

    summary = {
        "scenario": "EndowmentEffect",
        "variant": "LLM",
        "total_rounds": metrics["total_rounds"],
        "metrics": metrics,
        "validation": validation,
        "llm_action_distribution": action_dist,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nVALIDATION: {validation['interpretation']}")
    print(f"Fit Score: {validation['score']:.1%}")
    print(f"Saved EndowmentEffect LLM analysis summary to {summary_path}")
    finalize_llm_analysis(
        data, config, output_dir, "EndowmentEffect", summary,
        config_path=args.config,
    )
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "price_deviation",
    "mean_absolute_deviation",
    "deviation_half_life",
    "volume_suppression_ratio",
    "endowment_premium_capture_rate",
    "portfolio_wealth_ratio",
    "turnover_rate",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "validate_endowment_effect",
    "analyze_action_distribution",
    "main",
]
