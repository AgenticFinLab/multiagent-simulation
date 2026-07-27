#!/usr/bin/env python
"""Liquidity Dry-up simulation analysis helpers and Rule entry point.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_liquiditydryup_dynamics.png,
02_liquiditydryup_analysis.png, and 03_summary.png.
"""

import json
import math
import os
from typing import Any, Dict, Iterable, List, Mapping

from examples.standard_rule_analysis import load_results, run_standard_analysis
from masim.utils.config import load_config


def _longest_true_run(flags: Iterable[bool]) -> int:
    """Return the longest consecutive run of true values."""
    longest = current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        longest = max(longest, current)
    return longest


def liquidity_ratio_index(
    liquidity_history: Iterable[float], normal_liquidity: float
) -> List[float]:
    """Return round-level liquidity divided by calibrated normal depth."""
    if normal_liquidity <= 0:
        raise ValueError("normal_liquidity must be positive")
    return [float(value) / normal_liquidity for value in liquidity_history]


def market_maker_withdrawal_fraction(provisions: Iterable[float]) -> float:
    """Return the share of market-maker decisions providing zero depth."""
    values = [max(0.0, float(value)) for value in provisions]
    return sum(value == 0.0 for value in values) / len(values) if values else 0.0


def market_price_impact(
    returns: Iterable[float], volumes: Iterable[float]
) -> float:
    """Return mean absolute return per unit of executed order volume."""
    impacts = [
        abs(float(ret)) / float(volume)
        for ret, volume in zip(returns, volumes)
        if float(volume) > 0
    ]
    return sum(impacts) / len(impacts) if impacts else 0.0


def price_amplitude_dislocation(
    prices: Iterable[float],
    fundamental: float,
    lri_history: Iterable[float],
    threshold: float = 0.5,
) -> float:
    """Return peak absolute fundamental deviation during dry-up rounds."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    dry_deviations = [
        abs((float(price) - fundamental) / fundamental)
        for price, lri in zip(prices, lri_history)
        if float(lri) < threshold
    ]
    return max(dry_deviations) if dry_deviations else 0.0


def liquidity_persistence_duration(
    lri_history: Iterable[float], threshold: float = 0.5
) -> int:
    """Return the longest consecutive dry-up episode."""
    return _longest_true_run(float(value) < threshold for value in lri_history)


def wealth_distribution_index(terminal_wealth: Iterable[float]) -> float:
    """Return the Gini coefficient of non-negative terminal wealth."""
    values = sorted(max(0.0, float(value)) for value in terminal_wealth)
    total = sum(values)
    if not values or total == 0:
        return 0.0
    weighted = sum((index + 1) * value for index, value in enumerate(values))
    return (2 * weighted) / (len(values) * total) - (len(values) + 1) / len(values)


def liquidity_provider_index(
    liquidity_by_archetype: Mapping[str, float],
) -> Dict[str, float]:
    """Return each archetype's share of positive provided liquidity."""
    total = sum(max(0.0, float(value)) for value in liquidity_by_archetype.values())
    if total == 0:
        return {}
    return {
        archetype: max(0.0, float(value)) / total
        for archetype, value in liquidity_by_archetype.items()
        if float(value) > 0
    }


def _market_rows(results: Any) -> List[Mapping[str, Any]]:
    """Return recorded market broadcasts in round order."""
    rows = results.players["market"].turns.field("market_data")
    return [rows[index] for index in sorted(rows)]


def _normal_liquidity(config: Mapping[str, Any]) -> float:
    """Derive normal depth from the configured market base and maker capacity."""
    players = config["players"]
    market_base = float(players["market"]["config"]["extras"]["base_liquidity"])
    maker_capacity = 0.0
    for player_id, player in players.items():
        if player_id == "market" or player.get("archetype") != "market-maker":
            continue
        maker_capacity += float(player["config"]["extras"]["base_liquidity"])
    return market_base + maker_capacity


def calculate_liquidity_metrics(config_path: str) -> Dict[str, Any]:
    """Calculate the scenario metrics declared in analysis-bases.md."""
    config = load_config(config_path)
    results = load_results(config)
    market_rows = _market_rows(results)
    normal_liquidity = _normal_liquidity(config)

    liquidity_ratios = liquidity_ratio_index(
        (row["liquidity"] for row in market_rows), normal_liquidity
    )
    player_rows: Dict[str, Dict[int, float]] = {}
    liquidity_by_archetype: Dict[str, float] = {}
    maker_provisions: List[float] = []
    terminal_wealth: List[float] = []
    final_price = float(market_rows[-1]["price"])
    for player_id, player in results.players.items():
        if player_id == "market":
            continue
        quantities = {
            int(round_num): abs(float(value))
            for round_num, value in player.turns.field("quantity").items()
        }
        player_rows[player_id] = quantities
        provisions = [
            max(0.0, float(value))
            for value in player.turns.field("provides_liquidity").values()
        ]
        archetype = config["players"][player_id].get("archetype", "unknown")
        liquidity_by_archetype[archetype] = (
            liquidity_by_archetype.get(archetype, 0.0) + sum(provisions)
        )
        if archetype == "market-maker":
            maker_provisions.extend(provisions)
        extras = config["players"][player_id]["config"]["extras"]
        cash = float(extras["initial_cash"])
        position = float(extras["initial_position"])
        for round_num, quantity in player.turns.field("quantity").items():
            price = float(market_rows[int(round_num) - 1]["price"])
            signed_quantity = float(quantity)
            cash -= signed_quantity * price
            position += signed_quantity
        terminal_wealth.append(cash + position * final_price)

    volumes = [
        sum(rounds.get(round_num, 0.0) for rounds in player_rows.values())
        for round_num in range(1, len(market_rows) + 1)
    ]
    lpi = liquidity_provider_index(liquidity_by_archetype)

    metrics: Dict[str, Any] = {
        "normal_liquidity": normal_liquidity,
        "lri_minimum": min(liquidity_ratios),
        "lri_mean": sum(liquidity_ratios) / len(liquidity_ratios),
        "market_maker_withdrawal_fraction": market_maker_withdrawal_fraction(
            maker_provisions
        ),
        "mean_price_impact": market_price_impact(
            (row["return"] for row in market_rows), volumes
        ),
        "peak_absolute_deviation_during_dryup": price_amplitude_dislocation(
            (row["price"] for row in market_rows),
            float(market_rows[-1]["fundamental"]),
            liquidity_ratios,
        ),
        "liquidity_persistence_duration": liquidity_persistence_duration(
            liquidity_ratios
        ),
        "wealth_distribution_index": wealth_distribution_index(terminal_wealth),
        "liquidity_provision_index": lpi,
    }
    if not all(
        math.isfinite(float(value))
        for key, value in metrics.items()
        if key != "liquidity_provision_index"
    ):
        raise ValueError("LiquidityDryup analysis produced a non-finite metric")
    return metrics


def run_liquidity_analysis(config_path: str) -> Dict[str, Any]:
    """Generate standard outputs and append scenario-specific metrics."""
    summary = run_standard_analysis("LiquidityDryup", config_path)
    summary["liquidity_dryup_metrics"] = calculate_liquidity_metrics(config_path)
    output_dir = os.path.join(os.path.dirname(summary["record_path"]), "analysis")
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def main():
    """Run the standard analysis output contract for this variant."""
    return run_liquidity_analysis("configs/LiquidityDryup/Rule/simulation.yml")


if __name__ == "__main__":
    main()
