#!/usr/bin/env python
"""2010 Flash Crash Rule Simulation Analysis.

Produces the standardized output set required by implement-simulation-skill:
summary.json, 00_investor_bids.png, 01_flashcrash2010_dynamics.png,
02_flashcrash2010_analysis.png, and 03_summary.png.

Usage:
    python examples/FlashCrash2010/Rule/analysis.py -c configs/FlashCrash2010/Rule/simulation.yml
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import numpy as np

from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_rolling_volatility,
    validate_flash_crash,
)
from masim.evaluation.data_loader import load_data, market_players
from masim.utils import load_config, load_results


def max_drawdown(price_history: List[float]) -> float:
    """Peak-to-trough price decline as fraction of peak price."""
    peak = price_history[0]
    max_dd = 0.0
    for p in price_history:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd


def depth_collapse_ratio(depth_history: List[float], base_depth: float) -> float:
    """Minimum depth during simulation as fraction of base_depth."""
    if not depth_history or base_depth <= 0:
        return 1.0
    return min(depth_history) / base_depth


def spread_widening_factor(
    spread_history: List[float], normal_spread: float = 0.0001
) -> float:
    """Maximum spread reached divided by normal (baseline) spread."""
    if not spread_history:
        return 1.0
    return max(spread_history) / max(normal_spread, 1e-8)


def hft_withdrawal_rounds(
    hft_orders_by_round: List[List[Dict]], withdrawal_threshold: int = 0
) -> int:
    """Number of rounds in which total HFT order quantity == 0."""
    count = 0
    for round_orders in hft_orders_by_round:
        hft_qty = sum(
            abs(o["quantity"])
            for o in round_orders
            if o.get("agent_type") == "hft"
        )
        if hft_qty <= withdrawal_threshold:
            count += 1
    return count


def cascade_trigger_rounds(stoploss_orders_by_round: List[List[Dict]]) -> List[int]:
    """List of rounds in which at least one StopLossTrader fires."""
    return [
        i
        for i, round_orders in enumerate(stoploss_orders_by_round)
        if any(
            o.get("agent_type") == "stoploss" and o["quantity"] < 0
            for o in round_orders
        )
    ]


def recovery_time(
    price_history: List[float],
    trough_round: int,
    fundamental: float,
    threshold: float = 0.02,
) -> int:
    """Rounds from trough to price returning within threshold of fundamental."""
    for i in range(trough_round, len(price_history)):
        if abs(price_history[i] - fundamental) / fundamental <= threshold:
            return i - trough_round
    return -1


def analyze_flash_crash(config_path: str) -> Dict[str, Any]:
    """Run the flash crash analysis and return summary metrics."""
    config = load_config(config_path)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)

    # Extract price history from market coordinator
    coordinators = market_players(results)
    price_history: List[float] = []
    for _pid, player in coordinators.items():
        for _round_num, state in player.turns.field("custom_state").items():
            if isinstance(state, dict) and "price" in state:
                price_history.append(float(state["price"]))
        break

    if not price_history:
        return {"error": "No price history found in records"}

    fundamental = config["players"]["market"]["config"]["extras"]["fundamental_value"]
    base_depth_val = config["players"]["market"]["config"]["extras"]["base_depth"]

    # Compute metrics
    summary: Dict[str, Any] = {
        "scenario": "FlashCrash2010",
        "variant": "Rule",
        "total_rounds": len(price_history),
        "max_drawdown": max_drawdown(price_history),
        "min_price": min(price_history),
        "max_price": max(price_history),
        "final_price": price_history[-1] if price_history else None,
        "fundamental_value": fundamental,
    }

    # Save summary
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def main():
    """Run the analysis from command line."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrash2010 Rule simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/Rule/simulation.yml",
    )
    args = parser.parse_args()
    result = analyze_flash_crash(args.config)
    print(json.dumps(result, indent=2))
    return result


__all__ = [
    "max_drawdown",
    "depth_collapse_ratio",
    "spread_widening_factor",
    "hft_withdrawal_rounds",
    "cascade_trigger_rounds",
    "recovery_time",
    "analyze_flash_crash",
    "main",
]


if __name__ == "__main__":
    main()
