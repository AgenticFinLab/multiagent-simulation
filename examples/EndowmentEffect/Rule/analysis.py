"""EndowmentEffect analysis.

The Rule analysis module is the authoritative implementation for loading run
artifacts, computing endowment-effect metrics, and writing summary outputs.
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.finance import save_figure
from masim.utils import load_config, load_results


def price_deviation(price_history: List[float], fundamental: float) -> List[float]:
    """Return per-round signed deviation from fundamental value."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not price_history:
        raise ValueError("price_history must not be empty")
    return [(price - fundamental) / fundamental for price in price_history]


def mean_absolute_deviation(price_history: List[float], fundamental: float) -> float:
    """Return mean absolute price deviation from fundamental."""
    deviations = price_deviation(price_history, fundamental)
    return float(np.mean(np.abs(deviations)))


def volume_suppression_ratio(actual_volume: List[float], rational_volume: float) -> float:
    """Return actual volume divided by a rational-volume benchmark."""
    if not actual_volume:
        raise ValueError("actual_volume must not be empty")
    if rational_volume <= 0:
        raise ValueError("rational_volume must be positive")
    return sum(actual_volume) / (rational_volume * len(actual_volume))


def endowment_premium_capture_rate(
    price_history: List[float], fundamental: float, endowment_premium: float
) -> float:
    """Return fraction of rounds below the endowed-holder selling threshold."""
    if not price_history:
        raise ValueError("price_history must not be empty")
    threshold = fundamental * (1 + endowment_premium)
    return sum(1 for price in price_history if price < threshold) / len(price_history)


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load prices and player order payloads from a completed simulation."""
    results = load_results(config)
    coordinators = list(results.players_by_role("coordinator").values())
    if not coordinators:
        raise ValueError("No coordinator result found")

    prices = list(coordinators[0].batch("price").all())
    if not prices:
        raise ValueError("Coordinator price series is empty")

    trades: Dict[str, List[Dict[str, Any]]] = {}
    for player_id, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            trades[player_id] = [
                {**payload, "round": round_num}
                for round_num, payload in sorted(payloads_by_round.items())
            ]

    if not trades:
        raise ValueError("No player order payloads found")

    return {"prices": prices, "trades": trades}


def _strategy_summary(trades: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    summary = {}
    for player_id, payloads in trades.items():
        if not payloads:
            continue
        strategy = payloads[0]["strategy"]
        buy_volume = sum(p["quantity"] for p in payloads if p["action"] == "buy")
        sell_volume = sum(p["quantity"] for p in payloads if p["action"] == "sell")
        total_volume = buy_volume + sell_volume
        summary[player_id] = {
            "strategy": strategy,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "total_volume": total_volume,
            "trade_count": sum(1 for p in payloads if p["quantity"] > 0),
        }
    if not summary:
        raise ValueError("No strategy payloads available")
    return summary


def calculate_metrics(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate EndowmentEffect metrics from loaded run artifacts."""
    prices = data["prices"]
    coordinator = config["players"]["coordinator"]
    market_extras = coordinator["extras"]
    fundamental = float(market_extras["fundamental_value"])
    endowment_premium = float(
        config["players"]["player_1"]["extras"]["endowment_premium"]
    )
    deviations = price_deviation(prices, fundamental)
    volumes = [
        sum(abs(p["quantity"]) for payloads in data["trades"].values() for p in payloads if p["round"] == round_num)
        for round_num in range(1, len(prices) + 1)
    ]
    strategy_summary = _strategy_summary(data["trades"])
    rational_volume = max(1.0, np.mean([res["total_volume"] for res in strategy_summary.values()]))
    return {
        "total_rounds": len(prices),
        "fundamental": fundamental,
        "price_deviation": deviations,
        "mean_absolute_deviation": mean_absolute_deviation(prices, fundamental),
        "volume_suppression_ratio": volume_suppression_ratio(volumes, rational_volume),
        "endowment_premium_capture_rate": endowment_premium_capture_rate(
            prices, fundamental, endowment_premium
        ),
        "strategy_summary": strategy_summary,
        "price_statistics": {
            "initial_price": float(prices[0]),
            "final_price": float(prices[-1]),
            "max_price": float(max(prices)),
            "min_price": float(min(prices)),
        },
    }


def create_visualizations(data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str) -> None:
    """Create price-deviation and trading-volume figures."""
    os.makedirs(output_dir, exist_ok=True)
    prices = data["prices"]
    rounds = list(range(1, len(prices) + 1))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rounds, prices, label="Market Price")
    ax.axhline(metrics["fundamental"], linestyle="--", color="gray", label="Fundamental")
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.set_title("EndowmentEffect Price Path")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_figure(fig, os.path.join(output_dir, "price_path.png"))
    plt.close(fig)

    labels = [res["strategy"] for res in metrics["strategy_summary"].values()]
    volumes = [res["total_volume"] for res in metrics["strategy_summary"].values()]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, volumes)
    ax.set_ylabel("Total Volume")
    ax.set_title("EndowmentEffect Trading Volume by Strategy")
    ax.tick_params(axis="x", rotation=30)
    save_figure(fig, os.path.join(output_dir, "strategy_volume.png"))
    plt.close(fig)


def main() -> Dict[str, Any]:
    """Run EndowmentEffect analysis."""
    parser = argparse.ArgumentParser(description="Analyze EndowmentEffect simulation")
    parser.add_argument("-c", "--config", required=True, help="Path to simulation YAML")
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    output_dir = os.path.join(os.path.dirname(record_dir), "analysis")
    data = load_simulation_data(config)
    metrics = calculate_metrics(data, config)
    create_visualizations(data, metrics, output_dir)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved EndowmentEffect analysis summary to {summary_path}")
    return metrics


if __name__ == "__main__":
    main()


__all__ = [
    "price_deviation",
    "mean_absolute_deviation",
    "volume_suppression_ratio",
    "endowment_premium_capture_rate",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "main",
]
