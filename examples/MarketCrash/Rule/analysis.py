"""MarketCrash Simulation Analysis

Analyzes simulation results for crash dynamics.
Detects panic selling cascades and crash depth/recovery patterns.

Usage:
    python examples/MarketCrash/Rule/analysis.py -c configs/MarketCrash/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_max_drawdown,
    calculate_autocorrelation,
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_bubble_crash_analysis,
    plot_multi_panel_summary,
    validate_market_crash,
)
from masim.utils import load_config, load_results


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert a batch store list to {round_num: value} (round_num starts at 1)."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Extract analysis-ready data dicts from a SimulationResults object.

    Data sources
    ------------
    Coordinator  → batch stores price / fundamental / volume  (flat time-series)
    Player turns → decision_payload fields bid_price / quantity

    Returns
    -------
    dict with keys:
        market_prices       : {round_num: float}
        fundamentals        : {round_num: float}
        volumes             : {round_num: float}
        investor_quantities : {player_id: {round_num: float}}
    """
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}
    volumes: Dict[int, float] = {}
    for player in results.players_by_role("coordinator").values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(_batch_to_rounds(player.batch("fundamental").all()))
        if "volume" in player.batch_store_names:
            volumes.update(_batch_to_rounds(player.batch("volume").all()))

    investor_quantities: Dict[str, Dict[int, float]] = {}
    for pid, player in results.players_by_role("player").items():
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "volumes": volumes,
        "investor_quantities": investor_quantities,
    }


def analyze_crash(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform market crash analysis."""
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    volumes = data.get("volumes", {})
    investor_quantities = data.get("investor_quantities", {})

    if not market_prices:
        print("No market price data found")
        return {}

    # Fundamental value from simulation data
    prices_list_tmp = [market_prices[r] for r in sorted(market_prices.keys())]
    if fundamentals:
        fundamental_value = sum(fundamentals.values()) / len(fundamentals)
    else:
        fundamental_value = prices_list_tmp[0]  # Use initial price as proxy

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=5)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)
    returns_list = list(returns.values())
    acf = (
        calculate_autocorrelation(returns_list, max_lag=10)
        if len(returns_list) > 10
        else []
    )

    # Crash detection
    crash_duration = (trough_idx - peak_idx) if trough_idx > peak_idx else 0
    crash_detected = max_dd < -15  # >15% drawdown = crash
    recovery_detected = (
        prices_list[-1] > prices_list[trough_idx] * 1.1
        if trough_idx < len(prices_list) - 1
        else False
    )

    # Run validation
    validation = validate_market_crash(
        max_drawdown=max_dd,
        crash_duration=crash_duration,
        recovery_detected=recovery_detected,
        total_rounds=len(market_prices),
    )

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    plot_price_dynamics(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "01_price.png"),
    )
    plot_volatility_analysis(
        market_prices,
        volatility,
        output_path=os.path.join(output_dir, "02_volatility.png"),
    )
    plot_bubble_crash_analysis(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "03_crash.png"),
    )
    plot_multi_panel_summary(
        market_prices,
        volatility=volatility,
        investor_quantities=investor_quantities,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "04_summary.png"),
    )

    # Calculate returns statistics
    returns_mean = sum(returns.values()) / len(returns) if returns else 0
    returns_std = (
        (sum((r - returns_mean) ** 2 for r in returns.values()) / len(returns)) ** 0.5
        if returns
        else 0
    )

    summary = {
        "scenario": "MarketCrash",
        "total_rounds": len(market_prices),
        "fundamental_value": fundamental_value,
        "crash_detected": crash_detected,
        "price": {
            "initial": round(prices_list[0], 4),
            "final": round(prices_list[-1], 4),
            "min": round(min(prices_list), 4),
            "max": round(max(prices_list), 4),
            "mean": round(sum(prices_list) / len(prices_list), 4),
        },
        "returns": {
            "mean": round(returns_mean, 6),
            "std": round(returns_std, 6),
        },
        "metrics": {
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
            "crash_duration": crash_duration,
            "crash_depth": round(min(prices_list), 4),
            "recovery_detected": recovery_detected,
            "return_autocorr_lag1": round(acf[0], 4) if acf else None,
        },
        "volatility": {
            "avg": (
                round(sum(volatility.values()) / len(volatility), 6)
                if volatility
                else 0
            ),
            "max": round(max(volatility.values()), 6) if volatility else 0,
        },
        "volume": {
            "total": sum(volumes.values()) if volumes else 0,
            "avg": round(sum(volumes.values()) / len(volumes), 4) if volumes else 0,
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("MARKET CRASH ANALYSIS")
    print("=" * 50)
    print(f"Crash Detected: {crash_detected}")
    print(f"Max Drawdown: {max_dd:.2f}%")
    print(f"Crash Duration: {crash_duration} rounds")
    print(f"Peak Round: {peak_idx}, Trough Round: {trough_idx}")
    print(f"Recovery: {'Yes' if recovery_detected else 'No'}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


def main():
    """Run MarketCrash analysis."""
    parser = argparse.ArgumentParser(description="Analyze MarketCrash simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    return analyze_crash(data, output_dir)


if __name__ == "__main__":
    main()
