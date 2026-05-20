"""Analysis utilities for the SunkCostFallacy Rule variant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np


def compute_losing_holding_rate(positions: list[dict]) -> float:
    """Hold frequency for losing positions. See analysis-bases.md §2.1."""
    if not positions:
        raise ValueError("positions must not be empty")
    losing = [row for row in positions if float(row["unrealized_return"]) < 0]
    if not losing:
        raise ValueError("positions contain no losing observations")
    holds = sum(1 for row in losing if row["action"] == "hold")
    return float(holds / len(losing))


def compute_escalation_volume(orders: list[dict]) -> float:
    """Additional buy volume by escalation agents. See analysis-bases.md §2.2."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "CommitmentEscalator"
            and order["action"] == "buy"
        )
    )


def compute_rational_cut_volume(orders: list[dict]) -> float:
    """Sell volume by rational cutters. See analysis-bases.md §2.3."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "RationalCutter" and order["action"] == "sell"
        )
    )


def compute_opportunity_reallocation(orders: list[dict]) -> float:
    """Opportunity-cost reallocation volume. See analysis-bases.md §2.4."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "OpportunityCostTrader"
        )
    )


def compute_performance_drag(agent_values: dict[str, list[float]]) -> float:
    """Performance gap between biased and rational agents. See analysis-bases.md §2.5."""
    if "biased" not in agent_values or "rational" not in agent_values:
        raise ValueError("agent_values must contain biased and rational series")
    biased = agent_values["biased"]
    rational = agent_values["rational"]
    if not biased or not rational:
        raise ValueError("agent value series must not be empty")
    rational_final = float(rational[-1])
    if rational_final == 0:
        raise ValueError("rational final value must not be zero")
    return float((rational_final - float(biased[-1])) / rational_final)


def compute_loss_onset(prices: list[float], cost_basis: float) -> int:
    """First round where price falls below cost basis. See analysis-bases.md §2.6."""
    if cost_basis <= 0:
        raise ValueError("cost_basis must be positive")
    if not prices:
        raise ValueError("prices must not be empty")
    for index, price in enumerate(prices, start=1):
        if price < cost_basis:
            return index
    raise ValueError("no loss onset found")


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


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate core SunkCostFallacy metrics from structured data."""
    prices: List[float] = data["price_history"]
    cost_basis = float(data["cost_basis"])
    metrics: Dict[str, Any] = {"loss_onset_round": compute_loss_onset(prices, cost_basis)}
    if "orders" in data:
        metrics["escalation_volume"] = compute_escalation_volume(data["orders"])
        metrics["rational_cut_volume"] = compute_rational_cut_volume(data["orders"])
        metrics["opportunity_reallocation"] = compute_opportunity_reallocation(
            data["orders"]
        )
    if "positions" in data:
        metrics["losing_holding_rate"] = compute_losing_holding_rate(
            data["positions"]
        )
    if "agent_values" in data:
        metrics["performance_drag"] = compute_performance_drag(data["agent_values"])
    return metrics


def create_visualizations(data: Dict[str, Any], output_dir: str | Path) -> None:
    """Create the core price/cost-basis visualization."""
    prices = data["price_history"]
    if not prices:
        raise ValueError("data['price_history'] must not be empty")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    cost_basis = float(data["cost_basis"])
    rounds = list(range(1, len(prices) + 1))
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, prices, label="price")
    plt.axhline(cost_basis, color="black", linestyle="--", label="cost basis")
    plt.xlabel("Round")
    plt.ylabel("Price")
    plt.title("SunkCostFallacy Price Dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "sunkcostfallacy_price_dynamics.png")
    plt.close()


__all__ = [
    "compute_losing_holding_rate",
    "compute_escalation_volume",
    "compute_rational_cut_volume",
    "compute_opportunity_reallocation",
    "compute_performance_drag",
    "compute_loss_onset",
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
    "01_sunkcostfallacy_dynamics.png",
    "02_sunkcostfallacy_analysis.png",
    "03_summary.png",
)


def analyze_sunkcostfallacy_standard(data: Dict[str, Any], config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Run the project standard validation, summary, and fixed PNG outputs."""
    return _analyze_standard_scenario("SunkCostFallacy", data, config, output_dir)


def main() -> Dict[str, Any]:
    """Run SunkCostFallacy analysis using the standard output contract."""
    return _run_standard_analysis("SunkCostFallacy", "configs/SunkCostFallacy/Rule/simulation.yml")


__all__.extend([
    "_batch_to_rounds",
    "_load_data",
    "STANDARD_OUTPUT_FILES",
    "analyze_sunkcostfallacy_standard",
    "main",
])


if __name__ == "__main__":
    main()
