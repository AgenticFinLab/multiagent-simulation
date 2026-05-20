"""Analysis utilities for the FramingEffect Rule variant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np


def framing_deviation_index(price_history: list[float], fundamental: float) -> float:
    """Mean absolute deviation from fundamental. See analysis-bases.md §2.1."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not price_history:
        raise ValueError("price_history must not be empty")
    return float(np.mean([abs(price - fundamental) / fundamental for price in price_history]))


def framing_asymmetry_ratio(price_history: list[float], fundamental: float) -> float:
    """Positive-vs-negative deviation magnitude ratio. See analysis-bases.md §2.2."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not price_history:
        raise ValueError("price_history must not be empty")
    deviations = [(price - fundamental) / fundamental for price in price_history]
    positives = [abs(dev) for dev in deviations if dev > 0]
    negatives = [abs(dev) for dev in deviations if dev < 0]
    if not positives or not negatives:
        raise ValueError("price_history must contain both positive and negative deviations")
    return float(np.mean(positives) / np.mean(negatives))


def framing_volume_impact(
    net_demand_history: list[float],
    dev_history: list[float],
    threshold: float = 0.02,
) -> float:
    """Average absolute net demand in framing-active rounds. See analysis-bases.md §2.3."""
    if len(net_demand_history) != len(dev_history):
        raise ValueError("net_demand_history and dev_history lengths must match")
    active = [
        abs(demand)
        for demand, deviation in zip(net_demand_history, dev_history)
        if abs(deviation) > threshold
    ]
    if not active:
        raise ValueError("no framing-active rounds found")
    return float(np.mean(active))


def rational_correction_efficiency(
    dev_history: list[float],
    lookahead: int = 5,
    threshold: float = 0.05,
) -> float:
    """Fraction of large deviations that halve within a lookahead window. See analysis-bases.md §2.4."""
    if lookahead <= 0:
        raise ValueError("lookahead must be positive")
    if len(dev_history) <= lookahead:
        raise ValueError("dev_history is shorter than lookahead window")
    candidates = [
        idx
        for idx in range(len(dev_history) - lookahead)
        if abs(dev_history[idx]) > threshold
    ]
    if not candidates:
        raise ValueError("no large deviations found for correction-efficiency calculation")
    corrected = [
        idx
        for idx in candidates
        if abs(dev_history[idx + lookahead]) < abs(dev_history[idx]) * 0.5
    ]
    return float(len(corrected) / len(candidates))


def volatility_amplification_factor(
    price_history: list[float],
    dev_history: list[float],
    threshold: float = 0.02,
) -> float:
    """Volatility ratio of framing-active rounds to quiet rounds. See analysis-bases.md §2.5."""
    if len(price_history) != len(dev_history):
        raise ValueError("price_history and dev_history lengths must match")
    if len(price_history) < 3:
        raise ValueError("price_history must contain at least three points")
    returns = np.diff(np.array(price_history, dtype=float)) / np.array(price_history[:-1], dtype=float)
    active = [ret for ret, dev in zip(returns, dev_history[1:]) if abs(dev) > threshold]
    quiet = [ret for ret, dev in zip(returns, dev_history[1:]) if abs(dev) <= threshold]
    if len(active) < 2 or len(quiet) < 2:
        raise ValueError("both active and quiet return groups need at least two observations")
    quiet_vol = float(np.std(quiet))
    if quiet_vol == 0:
        raise ValueError("quiet-round volatility is zero")
    return float(np.std(active) / quiet_vol)


def wealth_distribution_index(agent_wealth: list[float]) -> float:
    """Gini-style wealth dispersion index. See analysis-bases.md §2.6."""
    if not agent_wealth:
        raise ValueError("agent_wealth must not be empty")
    wealth = np.array(agent_wealth, dtype=float)
    if np.any(wealth < 0):
        raise ValueError("agent_wealth must be non-negative")
    if np.sum(wealth) == 0:
        raise ValueError("agent_wealth sum must be positive")
    sorted_wealth = np.sort(wealth)
    n = len(sorted_wealth)
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * sorted_wealth)) / (n * np.sum(sorted_wealth)) - (n + 1) / n)


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
    """Calculate core FramingEffect metrics from structured simulation data."""
    prices: List[float] = data["price_history"]
    fundamental = float(data["fundamental"])
    dev_history = [(price - fundamental) / fundamental for price in prices]
    metrics = {
        "framing_deviation_index": framing_deviation_index(prices, fundamental),
        "framing_asymmetry_ratio": framing_asymmetry_ratio(prices, fundamental),
    }
    if "net_demand_history" in data:
        metrics["framing_volume_impact"] = framing_volume_impact(
            data["net_demand_history"], dev_history
        )
    if "agent_wealth" in data:
        metrics["wealth_distribution_index"] = wealth_distribution_index(data["agent_wealth"])
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
    plt.title("FramingEffect Price Dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "framingeffect_price_dynamics.png")
    plt.close()


__all__ = [
    "framing_deviation_index",
    "framing_asymmetry_ratio",
    "framing_volume_impact",
    "rational_correction_efficiency",
    "volatility_amplification_factor",
    "wealth_distribution_index",
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
    "01_framingeffect_dynamics.png",
    "02_framingeffect_analysis.png",
    "03_summary.png",
)


def analyze_framingeffect_standard(data: Dict[str, Any], config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Run the project standard validation, summary, and fixed PNG outputs."""
    return _analyze_standard_scenario("FramingEffect", data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run FramingEffect analysis using the standard output contract."""
    return _run_standard_analysis("FramingEffect", "configs/FramingEffect/Rule/simulation.yml")


__all__.extend([
    "_batch_to_rounds",
    "_load_data",
    "STANDARD_OUTPUT_FILES",
    "analyze_framingeffect_standard",
    "main",
])


if __name__ == "__main__":
    main()
