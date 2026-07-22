#!/usr/bin/env python
"""Post-run metrics for the DotComBubble RuleLLM variant."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict

from masim.utils import load_config
from masim.evaluation import write_universal_summary

from examples.DotComBubble.Rule.analysis import (
    bubble_amplitude_index,
    bubble_duration,
    crash_severity,
    load_simulation_data,
    momentum_amplification_factor,
    recovery_time,
    short_seller_resistance,
)


DEFAULT_CONFIG = "configs/DotComBubble/RuleLLM/simulation.yml"
STANDARD_OUTPUT_FILES = ("summary.json", "dotcombubble_rulellm_dynamics.png")


def api_order_quality(
    agent_orders: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Measure required-field and value validity for RuleLLM API orders."""
    required = {"action", "bid_price", "quantity", "reasoning", "agent_type"}
    total = 0
    valid = 0
    for orders in agent_orders.values():
        for order in orders.values():
            total += 1
            try:
                price = float(order["bid_price"])
                quantity = float(order["quantity"])
                contract_ok = required.issubset(order)
                contract_ok = contract_ok and order["action"] in {"buy", "sell", "hold"}
                contract_ok = contract_ok and math.isfinite(price) and price > 0
                contract_ok = contract_ok and math.isfinite(quantity) and quantity >= 0
                contract_ok = contract_ok and quantity.is_integer()
                contract_ok = contract_ok and bool(str(order["reasoning"]).strip())
            except (KeyError, TypeError, ValueError):
                contract_ok = False
            valid += int(contract_ok)
    return {
        "applicable_to_api_or_rag": True,
        "total_orders": total,
        "valid_orders": valid,
        "contract_compliance_rate": valid / total if total else 0.0,
    }


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate every RuleLLM metric declared in ``analysis-bases.md §2``."""
    market = data["market_by_round"]
    if not market:
        raise ValueError("No market records found; run the simulation first")
    rounds = sorted(market)
    prices = [float(market[round_num]["price"]) for round_num in rounds]
    fundamental = float(market[rounds[0]]["fundamental"])
    if fundamental <= 0:
        raise ValueError("Recorded fundamental value must be positive")
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
        "MAF": momentum_amplification_factor(data["agent_orders"], bubble_rounds),
        "SSR": short_seller_resistance(short_orders, overvaluation_rounds),
        "RT": recovery_time(prices, fundamental),
        "AQR": api_order_quality(data["agent_orders"]),
    }


def create_visualizations(data: Dict[str, Any], output_path: str) -> None:
    """Write the RuleLLM price/fundamental path plot."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    market = data["market_by_round"]
    if not market:
        raise ValueError("Cannot plot empty market records")
    rounds = sorted(market)
    prices = [float(market[round_num]["price"]) for round_num in rounds]
    fundamentals = [float(market[round_num]["fundamental"]) for round_num in rounds]
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.plot(rounds, prices, label="Market price")
    axis.plot(rounds, fundamentals, "--", label="Fundamental value")
    axis.set(xlabel="Round", ylabel="Price", title="DotComBubble RuleLLM dynamics")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "dotcombubble_rulellm_dynamics.png", dpi=150)
    plt.close(figure)


def main() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Analyze DotComBubble RuleLLM results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    parser.add_argument(
        "-o", "--output-dir", default="EXPERIMENT/DotComBubble/RuleLLM/analysis"
    )
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    create_visualizations(data, str(output_dir))
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'RuleLLM'
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
        scenario='DotComBubble',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return metrics


__all__ = [
    "api_order_quality",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "STANDARD_OUTPUT_FILES",
    "main",
]


if __name__ == "__main__":
    main()
