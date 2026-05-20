"""Analysis utilities for the RepresentativenessBias Rule variant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np


def compute_base_rate_neglect(agent_beliefs: list[dict]) -> float:
    """Mean biased-vs-base-rate belief gap. See analysis-bases.md §2.1."""
    if not agent_beliefs:
        raise ValueError("agent_beliefs must not be empty")
    gaps = [
        abs(float(row["biased_belief"]) - float(row["base_rate_belief"]))
        for row in agent_beliefs
    ]
    return float(np.mean(gaps))


def compute_pattern_volume(orders: list[dict]) -> float:
    """Volume from representativeness-biased traders. See analysis-bases.md §2.2."""
    if not orders:
        raise ValueError("orders must not be empty")
    biased_types = {"PatternMatcher", "CategoryOvergeneralizer"}
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] in biased_types
        )
    )


def compute_mispricing(prices: list[float], fundamental: float) -> float:
    """Peak absolute price deviation from fundamental. See analysis-bases.md §2.3."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not prices:
        raise ValueError("prices must not be empty")
    return float(max(abs(price - fundamental) / fundamental for price in prices))


def compute_bayesian_correction(orders: list[dict]) -> float:
    """Stabilizing volume from Bayesian agents. See analysis-bases.md §2.4."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "BayesianUpdater"
        )
    )


def compute_contrarian_profitability(values: list[float]) -> float:
    """Terminal-minus-initial contrarian value change. See analysis-bases.md §2.5."""
    if len(values) < 2:
        raise ValueError("values must contain at least two observations")
    return float(values[-1] - values[0])


def compute_bias_onset(beliefs: list[float], threshold: float) -> int:
    """First round where belief deviation exceeds threshold. See analysis-bases.md §2.6."""
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if not beliefs:
        raise ValueError("beliefs must not be empty")
    for index, belief in enumerate(beliefs, start=1):
        if abs(float(belief)) > threshold:
            return index
    raise ValueError("no bias onset found")


def compute_agent_attribution(orders: list[dict]) -> dict[str, float]:
    """Attribute signed order pressure by agent type. See analysis-bases.md §2.7."""
    if not orders:
        raise ValueError("orders must not be empty")
    attribution: dict[str, float] = {}
    for order in orders:
        agent_type = order["agent_type"]
        sign = 1 if order["action"] == "buy" else -1 if order["action"] == "sell" else 0
        attribution[agent_type] = attribution.get(agent_type, 0.0) + sign * int(
            order["quantity"]
        )
    return attribution


def load_simulation_data(record_path: str | Path) -> Dict[str, Any]:
    """Load a JSON simulation result file from a record directory."""
    root = Path(record_path)
    if not root.exists():
        raise FileNotFoundError(f"record_path does not exist: {root}")
    candidates = sorted(root.rglob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"no JSON records found under {root}")
    with candidates[-1].open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate core RepresentativenessBias metrics from structured data."""
    prices: List[float] = data["price_history"]
    fundamental = float(data["fundamental"])
    metrics = {"mispricing_magnitude": compute_mispricing(prices, fundamental)}
    if "orders" in data:
        metrics["pattern_driven_volume"] = compute_pattern_volume(data["orders"])
        metrics["bayesian_correction"] = compute_bayesian_correction(data["orders"])
    if "agent_beliefs" in data:
        metrics["base_rate_neglect_index"] = compute_base_rate_neglect(
            data["agent_beliefs"]
        )
    return metrics


def create_visualizations(data: Dict[str, Any], output_dir: str | Path) -> None:
    """Create the core price-deviation visualization."""
    prices = data["price_history"]
    if not prices:
        raise ValueError("data['price_history'] must not be empty")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fundamental = float(data["fundamental"])
    rounds = list(range(1, len(prices) + 1))
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, prices, label="price")
    plt.axhline(fundamental, color="black", linestyle="--", label="fundamental")
    plt.xlabel("Round")
    plt.ylabel("Price")
    plt.title("RepresentativenessBias Price Dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "representativenessbias_price_dynamics.png")
    plt.close()


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
]

from examples.standard_rule_analysis import (  # noqa: E402
    _batch_to_rounds,
    _load_data,
    analyze_standard_scenario as _analyze_standard_scenario,
    run_standard_analysis as _run_standard_analysis,
)

STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_representativenessbias_dynamics.png",
    "02_representativenessbias_analysis.png",
    "03_summary.png",
)


def analyze_representativenessbias_standard(data: Dict[str, Any], config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Run the project standard validation, summary, and fixed PNG outputs."""
    return _analyze_standard_scenario("RepresentativenessBias", data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run RepresentativenessBias analysis using the standard output contract."""
    return _run_standard_analysis("RepresentativenessBias", "configs/RepresentativenessBias/Rule/simulation.yml")


__all__.extend([
    "_batch_to_rounds",
    "_load_data",
    "STANDARD_OUTPUT_FILES",
    "analyze_representativenessbias_standard",
    "main",
])


if __name__ == "__main__":
    main()
