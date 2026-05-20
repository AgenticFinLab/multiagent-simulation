"""Analysis utilities for the StatusQuoBias Rule variant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np


def compute_inertia_rate(orders: list[dict]) -> float:
    """Fraction of hold orders. See analysis-bases.md §2.1."""
    if not orders:
        raise ValueError("orders must not be empty")
    holds = sum(1 for order in orders if order["action"] == "hold")
    return float(holds / len(orders))


def compute_default_adherence(states: list[dict]) -> float:
    """Mean closeness to default allocation. See analysis-bases.md §2.2."""
    if not states:
        raise ValueError("states must not be empty")
    gaps = [
        abs(float(state["allocation"]) - float(state["default_allocation"]))
        for state in states
    ]
    return float(1.0 - np.mean(gaps))


def compute_active_rebalance_volume(orders: list[dict]) -> float:
    """Volume from active rebalancing agents. See analysis-bases.md §2.3."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "ActiveRebalancer"
        )
    )


def compute_underreaction_lag(prices: list[float], signals: list[float]) -> int:
    """Rounds until price response follows signal direction. See analysis-bases.md §2.4."""
    if len(prices) != len(signals):
        raise ValueError("prices and signals lengths must match")
    if len(prices) < 2:
        raise ValueError("prices must contain at least two observations")
    for index in range(1, len(prices)):
        price_change = prices[index] - prices[index - 1]
        if price_change * signals[index - 1] > 0:
            return index
    raise ValueError("no signal-following price response found")


def compute_momentum_offset(orders: list[dict]) -> float:
    """Volume from momentum agents that offsets inertia. See analysis-bases.md §2.5."""
    if not orders:
        raise ValueError("orders must not be empty")
    return float(
        sum(
            int(order["quantity"])
            for order in orders
            if order["agent_type"] == "MomentumTrader"
        )
    )


def compute_price_deviation(prices: list[float], fundamental: float) -> list[float]:
    """Price gap from fundamental by round. See analysis-bases.md §2.6."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not prices:
        raise ValueError("prices must not be empty")
    return [float((price - fundamental) / fundamental) for price in prices]


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
    """Calculate core StatusQuoBias metrics from structured data."""
    prices: List[float] = data["price_history"]
    fundamental = float(data["fundamental"])
    metrics: Dict[str, Any] = {
        "price_deviation": compute_price_deviation(prices, fundamental),
    }
    if "orders" in data:
        metrics["inertia_rate"] = compute_inertia_rate(data["orders"])
        metrics["active_rebalance_volume"] = compute_active_rebalance_volume(
            data["orders"]
        )
        metrics["momentum_offset"] = compute_momentum_offset(data["orders"])
    if "states" in data:
        metrics["default_adherence"] = compute_default_adherence(data["states"])
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
    plt.title("StatusQuoBias Price Dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "statusquobias_price_dynamics.png")
    plt.close()


__all__ = [
    "compute_inertia_rate",
    "compute_default_adherence",
    "compute_active_rebalance_volume",
    "compute_underreaction_lag",
    "compute_momentum_offset",
    "compute_price_deviation",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
]
