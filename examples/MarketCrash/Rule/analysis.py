#!/usr/bin/env python
"""Market Crash Rule Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_marketcrash_dynamics.png,
02_marketcrash_analysis.png, and 03_summary.png.
"""

import json
import os
from typing import Dict, Iterable, List

from examples.standard_rule_analysis import load_results, run_standard_analysis
from masim.utils.config import load_config


def maximum_drawdown(prices: Iterable[float]) -> float:
    """Return positive peak-to-trough drawdown as a fraction."""
    peak = 0.0
    worst = 0.0
    for price in prices:
        peak = max(peak, float(price))
        if peak > 0:
            worst = max(worst, (peak - float(price)) / peak)
    return worst


def largest_one_round_drop(prices: List[float]) -> float:
    """Return the largest negative one-round return as a positive fraction."""
    return max(
        (previous - current) / previous
        for previous, current in zip(prices, prices[1:])
        if previous > 0
    )


def minimum_liquidity(liquidity: Iterable[float]) -> float:
    """Return the minimum normalised liquidity level."""
    return min(float(value) for value in liquidity)


def volatility_spike_ratio(volatility: Iterable[float]) -> float:
    """Return peak-to-floor volatility ratio over the run."""
    values = [float(value) for value in volatility]
    floor = min(values)
    return max(values) / floor if floor > 0 else float("inf")


def bottom_fisher_absorption(quantities: Dict[int, float]) -> float:
    """Return cumulative positive BottomFisher quantity."""
    return sum(max(0.0, float(quantity)) for quantity in quantities.values())


def _batch(player, name: str) -> List[float]:
    """Load one coordinator HistoryBuffer as a list."""
    return [float(value) for value in player.batch(name).all()]


def calculate_crash_metrics(config_path: str) -> Dict[str, float]:
    """Calculate the scenario-specific metrics declared by the target."""
    config = load_config(config_path)
    results = load_results(config)
    market = results.players["market"]
    prices = _batch(market, "price")
    liquidity = _batch(market, "liquidity")
    volatility = _batch(market, "volatility")
    bottom = results.players["rule_bottom_fisher"].turns.field("quantity")
    return {
        "maximum_drawdown": maximum_drawdown(prices),
        "largest_one_round_drop": largest_one_round_drop(prices),
        "minimum_liquidity": minimum_liquidity(liquidity),
        "volatility_spike_ratio": volatility_spike_ratio(volatility),
        "bottom_fisher_absorption": bottom_fisher_absorption(bottom),
    }


def main():
    """Run standard outputs and append MarketCrash acceptance metrics."""
    config_path = "configs/MarketCrash/Rule/simulation.yml"
    summary = run_standard_analysis("MarketCrash", config_path)
    crash_metrics = calculate_crash_metrics(config_path)
    summary["crash_metrics"] = crash_metrics
    output_dir = os.path.dirname(summary["record_path"])
    summary_path = os.path.join(output_dir, "analysis", "summary.json")
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print("\nMARKETCRASH ACCEPTANCE METRICS")
    for name, value in crash_metrics.items():
        print(f"{name}: {value:.4f}")
    return summary


if __name__ == "__main__":
    main()
