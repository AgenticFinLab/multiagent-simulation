#!/usr/bin/env python
"""LTCMCollapse simulation analysis.

Implements the metrics defined in ``examples/LTCMCollapse/analysis-bases.md``.

Usage:
    python examples/LTCMCollapse/Rule/analysis.py \
        -c configs/LTCMCollapse/Rule/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.data_loader import _load_data, aligned_prices_and_fundamentals
from masim.evaluation.finance.timeseries import _returns, calculate_max_drawdown
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

__all__ = [
    "ValidationResult",
    "load_simulation_data",
    "calculate_metrics",
    "validate_metrics",
    "create_visualizations",
    "main",
]


@dataclass(frozen=True)
class ValidationResult:
    """Validation result for LTCMCollapse analysis-bases.md §6."""

    is_valid: bool
    score: float
    criteria: dict[str, dict[str, Any]]
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


def load_simulation_data(config: dict) -> dict:
    """Load market price and fundamental series via `masim.utils.load_results`."""

    results = load_results(config)
    raw = _load_data(results)
    rag_contexts = {}
    for pid, player in results.players_by_role("player").items():
        contexts = player.turns.field("rag_context")
        if contexts:
            rag_contexts[pid] = contexts
    rounds, prices, fundamentals = aligned_prices_and_fundamentals(raw)
    return {
        "rounds": rounds,
        "prices": prices,
        "fundamentals": fundamentals,
        "rag_contexts": rag_contexts,
        "agent_records": raw["investor_payloads"],
    }


def _cascade_onset_round(deviation: np.ndarray, threshold: float = -0.03) -> int | None:
    for index, value in enumerate(deviation, start=1):
        if value < threshold:
            return index
    return None


def _recovery_half_life_rounds(deviation: np.ndarray) -> int | None:
    trough_index = int(np.argmin(deviation))
    trough_value = float(deviation[trough_index])
    if trough_value >= 0:
        return None
    half_recovery_value = trough_value / 2
    for index in range(trough_index + 1, len(deviation)):
        if deviation[index] >= half_recovery_value:
            return index - trough_index
    return None


def calculate_metrics(data: dict) -> dict:
    """Calculate metrics from analysis-bases.md §2."""

    prices = np.array(data["prices"], dtype=float)
    fundamentals = np.array(data["fundamentals"], dtype=float)
    if len(prices) == 0:
        raise ValueError("Empty price series")
    if len(prices) != len(fundamentals):
        raise ValueError("Price and fundamental series lengths differ")
    if np.any(fundamentals == 0):
        raise ValueError("Fundamental series contains zero")

    returns = _returns(prices)
    deviation = (prices - fundamentals) / fundamentals
    final_deviation = float(deviation[-1] * 100)
    max_abs_deviation = float(np.max(np.abs(deviation)) * 100)
    mean_abs_deviation = float(np.mean(np.abs(deviation)) * 100)
    max_drawdown = abs(calculate_max_drawdown(prices.tolist())[0])
    onset_round = _cascade_onset_round(deviation)
    half_life = _recovery_half_life_rounds(deviation)
    if onset_round is None:
        stress_return_std = None
    else:
        stress_start = max(onset_round - 2, 0)
        stress_end = (
            len(returns)
            if half_life is None
            else min(len(returns), stress_start + half_life)
        )
        if stress_end <= stress_start:
            raise ValueError("Stress window contains no returns")
        stress_return_std = float(np.std(returns[stress_start:stress_end]) * 100)
    full_run_return_std = float(np.std(returns) * 100)

    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
            "max_drawdown_pct": max_drawdown,
        },
        "deviation_metrics": {
            "max_abs_deviation_pct": max_abs_deviation,
            "mean_abs_deviation_pct": mean_abs_deviation,
            "final_deviation_pct": final_deviation,
            "cascade_onset_round": onset_round,
            "recovery_half_life_rounds": half_life,
        },
        "volatility": {
            "annualized_pct": (
                None
                if stress_return_std is None
                else stress_return_std * float(np.sqrt(252))
            ),
            "return_std_pct": stress_return_std,
            "full_run_return_std_pct": full_run_return_std,
        },
    }


def validate_metrics(metrics: dict) -> ValidationResult:
    """Validate metrics against analysis-bases.md §6 expected results."""

    max_deviation = metrics["deviation_metrics"]["max_abs_deviation_pct"]
    volatility = metrics["volatility"]["return_std_pct"]
    final_abs_deviation = abs(metrics["deviation_metrics"]["final_deviation_pct"])
    half_life = metrics["deviation_metrics"]["recovery_half_life_rounds"]

    drawdown = metrics["price_metrics"]["max_drawdown_pct"]
    min_price = metrics["price_metrics"]["min"]
    deviation_score = 1.0 if 5.0 <= max_deviation <= 60.0 else 0.0
    drawdown_score = 1.0 if 5.0 <= drawdown <= 60.0 else 0.0
    volatility_score = (
        1.0 if volatility is not None and 1.0 <= volatility <= 12.0 else 0.0
    )
    recovery_score = 1.0 if final_abs_deviation <= max_deviation and min_price > 0 else 0.0
    half_life_score = 1.0 if half_life is not None else 0.0

    criteria = {
        "price_dislocation": {
            "observed": round(max_deviation, 3),
            "expected": "5% to 60% max absolute deviation",
            "score": round(deviation_score, 3),
            "assessment": "pass" if deviation_score >= 1.0 else "weak",
        },
        "finite_drawdown": {
            "observed": round(drawdown, 3),
            "expected": "5% to 60% maximum drawdown",
            "score": round(drawdown_score, 3),
            "assessment": "pass" if drawdown_score == 1.0 else "fail",
        },
        "stress_volatility": {
            "observed": None if volatility is None else round(volatility, 3),
            "expected": "1% to 12% return std during stress",
            "score": round(volatility_score, 3),
            "assessment": "pass" if volatility_score >= 1.0 else "weak",
        },
        "recovery_direction": {
            "observed": round(final_abs_deviation, 3),
            "expected": "positive prices and final absolute deviation no worse than max",
            "score": round(recovery_score, 3),
            "assessment": "pass" if recovery_score >= 1.0 else "fail",
        },
        "recovery_half_life": {
            "observed": half_life,
            "expected": "finite if a negative trough occurs",
            "score": round(half_life_score, 3),
            "assessment": "pass" if half_life is not None else "fail",
        },
    }

    score = (
        0.25 * deviation_score
        + 0.20 * drawdown_score
        + 0.20 * volatility_score
        + 0.20 * recovery_score
        + 0.15 * half_life_score
    )
    is_valid = all(item["assessment"] == "pass" for item in criteria.values())
    return ValidationResult(
        is_valid=is_valid,
        score=score,
        criteria=criteria,
        interpretation=(
            "LTCM stress mechanism is sufficiently visible."
            if is_valid
            else "LTCM stress mechanism is weak under current metrics."
        ),
    )


def create_visualizations(data: dict, output_path: str) -> None:
    """Create standard visualizations from analysis-bases.md §7."""

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    prices = np.array(data["prices"], dtype=float)
    fundamentals = np.array(data["fundamentals"], dtype=float)
    if len(prices) == 0:
        raise ValueError("Empty price series")

    rounds = np.arange(1, len(prices) + 1)
    deviation = (prices - fundamentals) / fundamentals * 100
    returns = _returns(prices) * 100

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("LTCMCollapse Simulation Analysis", fontsize=14, fontweight="bold")

    axes[0, 0].plot(rounds, prices, label="Price", color="red")
    axes[0, 0].plot(rounds, fundamentals, label="Fundamental", color="blue", linestyle="--")
    axes[0, 0].set_title("Price vs Fundamental")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(rounds, deviation, color="purple")
    axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0, 1].set_title("Price Deviation (%)")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(rounds[1:], returns, color="red", alpha=0.7)
    axes[1, 0].set_title("Returns (%)")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].hist(returns, bins=30, color="steelblue", alpha=0.7)
    axes[1, 1].set_title("Return Distribution")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "00_ltcmcollapse_summary.png", dpi=150)
    fig.savefig(output_dir / "00_investor_bids.png", dpi=150)
    fig.savefig(output_dir / "03_summary.png", dpi=150)
    plt.close(fig)

    _save_single_plot(output_dir / "01_price_vs_fundamental.png", rounds, prices, "Price", fundamentals)
    _save_single_plot(output_dir / "01_ltcmcollapse_dynamics.png", rounds, prices, "Price", fundamentals)
    _save_single_plot(output_dir / "02_deviation.png", rounds, deviation, "Deviation (%)")
    _save_single_plot(output_dir / "02_ltcmcollapse_analysis.png", rounds, deviation, "Deviation (%)")
    _save_single_plot(output_dir / "03_returns.png", rounds[1:], returns, "Returns (%)")


STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_ltcmcollapse_dynamics.png",
    "02_ltcmcollapse_analysis.png",
    "03_summary.png",
)


def _save_single_plot(
    path: Path,
    rounds: np.ndarray,
    values: np.ndarray,
    title: str,
    secondary: np.ndarray | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rounds, values, label=title)
    if secondary is not None:
        ax.plot(rounds, secondary, label="Fundamental", linestyle="--")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _write_summary(
    analysis_path: Path,
    metrics: dict,
    validation: ValidationResult,
) -> None:
    """Write metrics, summary JSON, and validation console report."""
    summary = {
        "metrics": metrics,
        "validation": validation.to_dict(),
    }
    with (analysis_path / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    status = "VALID" if validation.is_valid else "INVALID"
    print(f"=== LTCMCOLLAPSE SIMULATION VALIDATION: {status} ===")
    print(f"Overall Fit Score: {validation.score * 100:.1f}% (all five gates required)")
    for index, (name, criterion) in enumerate(validation.criteria.items(), start=1):
        print(f"[{index}] {name}")
        print(f"Observed: {criterion['observed']}")
        print(f"Expected: {criterion['expected']}")
        print(f"Score: {criterion['score']}")
        print(f"Assessment: {criterion['assessment']}")
    print("[SUMMARY]")
    print(validation.interpretation)
    print("Analysis complete. Results in:", analysis_path)


def main() -> None:
    """Run LTCMCollapse analysis and write metrics plus validation summary."""

    parser = argparse.ArgumentParser(description="Analyze LTCMCollapse simulation results")
    parser.add_argument("-c", "--config", type=str, default="configs/LTCMCollapse/Rule/simulation.yml")
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)
    validation = validate_metrics(metrics)

    analysis_path = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    create_visualizations(data, str(analysis_path))
    _write_summary(analysis_path, metrics, validation)
    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rule'
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
        scenario='LTCMCollapse',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )



if __name__ == "__main__":
    main()
