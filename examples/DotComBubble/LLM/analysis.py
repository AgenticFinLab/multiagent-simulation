#!/usr/bin/env python
"""Post-run metrics for the DotComBubble LLM variant.

Usage:
    python -m examples.DotComBubble.LLM.analysis \
        -c configs/DotComBubble/LLM/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution


DEFAULT_CONFIG = "configs/DotComBubble/LLM/simulation.yml"


def bubble_amplitude_index(
    price_history: list[float], fundamental: float
) -> float:
    """Return maximum overvaluation relative to fundamental value."""
    if not price_history or fundamental <= 0:
        raise ValueError("BAI requires prices and a positive fundamental value")
    return max((price - fundamental) / fundamental for price in price_history)


def bubble_duration(
    price_history: list[float],
    fundamental: float,
    bubble_threshold: float = 0.10,
) -> int:
    """Count rounds above the configured overvaluation threshold."""
    if fundamental <= 0:
        raise ValueError("BD requires a positive fundamental value")
    return sum(
        (price - fundamental) / fundamental > bubble_threshold
        for price in price_history
    )


def crash_severity(price_history: list[float]) -> float:
    """Return the largest peak-to-subsequent-trough drawdown."""
    if not price_history:
        raise ValueError("CS requires at least one price")
    peak_index = max(range(len(price_history)), key=price_history.__getitem__)
    peak = price_history[peak_index]
    trough = min(price_history[peak_index:])
    return (peak - trough) / peak if peak > 0 else 0.0


def momentum_amplification_factor(
    agent_orders: Dict[str, Dict[int, Dict[str, Any]]],
    bubble_rounds: Iterable[int],
) -> float:
    """Return momentum-follower share of buy volume in bubble rounds."""
    selected = set(bubble_rounds)
    total_buy = 0.0
    momentum_buy = 0.0
    for player_id, orders in agent_orders.items():
        for round_num, order in orders.items():
            if round_num not in selected or order.get("action") != "buy":
                continue
            quantity = float(order["quantity"])
            total_buy += quantity
            if "momentumfollower" in player_id.lower():
                momentum_buy += quantity
    return momentum_buy / total_buy if total_buy > 0 else 0.0


def short_seller_resistance(
    short_seller_orders: Dict[int, Dict[str, Any]],
    overvaluation_rounds: Iterable[int],
) -> float:
    """Return sell frequency by the constrained short-seller archetype."""
    selected = set(overvaluation_rounds)
    if not selected:
        return 0.0
    sell_rounds = sum(
        round_num in selected
        and order.get("action") == "sell"
        and float(order["quantity"]) > 0
        for round_num, order in short_seller_orders.items()
    )
    return sell_rounds / len(selected)


def recovery_time(
    price_history: list[float],
    fundamental: float,
    recovery_threshold: float = 0.10,
) -> Optional[int]:
    """Return rounds from the post-peak trough to fundamental recovery."""
    if not price_history or fundamental <= 0:
        raise ValueError("RT requires prices and a positive fundamental value")
    peak_index = max(range(len(price_history)), key=price_history.__getitem__)
    trough_index = min(
        range(peak_index, len(price_history)), key=price_history.__getitem__
    )
    for index in range(trough_index + 1, len(price_history)):
        if abs((price_history[index] - fundamental) / fundamental) < recovery_threshold:
            return index - trough_index
    return None


def api_quality(agent_orders: Dict[str, Dict[int, Dict[str, Any]]]) -> Dict[str, Any]:
    """Measure the recorded LLM decision-contract compliance rate."""
    required = {"action", "bid_price", "quantity", "reasoning", "analysis"}
    total = 0
    valid = 0
    for orders in agent_orders.values():
        for order in orders.values():
            total += 1
            try:
                price = float(order["bid_price"])
                quantity = float(order["quantity"])
                contract_ok = required.issubset(order)
                contract_ok = contract_ok and order["action"] in {
                    "buy",
                    "sell",
                    "hold",
                }
                contract_ok = contract_ok and math.isfinite(price) and price > 0
                contract_ok = contract_ok and math.isfinite(quantity) and quantity >= 0
                contract_ok = contract_ok and bool(str(order["reasoning"]).strip())
            except (KeyError, TypeError, ValueError):
                contract_ok = False
            valid += int(contract_ok)
    return {
        "total_decisions": total,
        "valid_decisions": valid,
        "contract_compliance_rate": valid / total if total else 0.0,
    }


def _market_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    state = payload.get("market_data")
    return state if isinstance(state, dict) else payload


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load market paths and investor orders from MASim records."""
    results = load_results(config)
    market_players = results.players_by_role("coordinator")
    if not market_players and "market" in results.players:
        market_players = {"market": results.players["market"]}

    market_by_round: Dict[int, Dict[str, Any]] = {}
    for player in market_players.values():
        for round_num, payload in player.turns.payloads().items():
            state = _market_state(payload)
            if "price" in state and "fundamental" in state:
                market_by_round[round_num] = state

    agent_orders = {
        player_id: player.turns.payloads()
        for player_id, player in results.players_by_role("player").items()
    }
    return {"market_by_round": market_by_round, "agent_orders": agent_orders}


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate every metric declared in ``analysis-bases.md §2``."""
    market = data["market_by_round"]
    if not market:
        raise ValueError("No market records found; run the simulation first")
    rounds = sorted(market)
    prices = [float(market[round_num]["price"]) for round_num in rounds]
    fundamental = float(market[rounds[0]]["fundamental"])
    bubble_rounds = [
        round_num
        for round_num in rounds
        if (float(market[round_num]["price"]) - fundamental) / fundamental > 0.10
    ]
    overvaluation_rounds = [
        round_num
        for round_num in rounds
        if float(market[round_num]["price"]) > fundamental
    ]
    short_orders: Dict[int, Dict[str, Any]] = {}
    for player_id, orders in data["agent_orders"].items():
        if "shortseller" in player_id.lower():
            short_orders.update(orders)

    return {
        "BAI": bubble_amplitude_index(prices, fundamental),
        "BD": bubble_duration(prices, fundamental),
        "CS": crash_severity(prices),
        "MAF": momentum_amplification_factor(
            data["agent_orders"], bubble_rounds
        ),
        "SSR": short_seller_resistance(short_orders, overvaluation_rounds),
        "RT": recovery_time(prices, fundamental),
        "AQR": api_quality(data["agent_orders"]),
    }


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Write a price/fundamental path plot for visual inspection."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    market = data["market_by_round"]
    rounds = sorted(market)
    prices = [float(market[round_num]["price"]) for round_num in rounds]
    fundamentals = [
        float(market[round_num]["fundamental"]) for round_num in rounds
    ]
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.plot(rounds, prices, label="Market price")
    axis.plot(rounds, fundamentals, "--", label="Fundamental value")
    axis.set(xlabel="Round", ylabel="Price", title="DotComBubble LLM dynamics")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "dotcombubble_llm_dynamics.png", dpi=150)
    plt.close(figure)


def main() -> Dict[str, Any]:
    """Load one run, calculate metrics, and write auditable outputs."""
    parser = argparse.ArgumentParser(description="Analyze DotComBubble LLM results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    parser.add_argument(
        "-o",
        "--output-dir",
        default="EXPERIMENT/DotComBubble/LLM/analysis",
    )
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)

    # implement-simulation-skill §7.2 — LLM variants must expose an
    # action-distribution audit and inject it into summary.json.
    # ``data['agent_orders']`` is already the {agent_id: {round: payload}}
    # shape our shared helper accepts.
    metrics["llm_action_distribution"] = analyze_action_distribution(
        data.get("agent_orders", {})
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    create_visualizations(data, str(output_dir))
    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=str))
    return metrics


__all__ = [
    "bubble_amplitude_index",
    "bubble_duration",
    "crash_severity",
    "momentum_amplification_factor",
    "short_seller_resistance",
    "recovery_time",
    "api_quality",
    "analyze_action_distribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "main",
]


if __name__ == "__main__":
    main()
