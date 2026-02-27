"""MomentumEffect Simulation Analysis

Analyzes simulation results for momentum patterns.
Tests whether past winners continue to outperform (positive autocorrelation).

Usage:
    python examples/MomentumEffect/analysis.py -c configs/MomentumEffect/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_autocorrelation,
    calculate_rolling_autocorrelation,
    calculate_rolling_volatility,
    calculate_max_drawdown,
    plot_price_dynamics,
    plot_returns_analysis,
    plot_multi_panel_summary,
    validate_momentum_effect,
)
from masim.utils import load_config, load_simulation_data, get_investor_quantities


def analyze_momentum(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform momentum effect analysis."""
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    if not market_prices:
        print("No market price data found")
        return {}

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=10)

    # Autocorrelation for momentum detection
    returns_list = list(returns.values())
    acf = calculate_autocorrelation(returns_list, max_lag=10)

    # Rolling autocorrelation
    rolling_ac = calculate_rolling_autocorrelation(market_prices, lag=1, window=20)

    # Momentum detection: positive short-lag autocorrelation
    momentum_detected = acf[0] > 0.1 if acf else False

    # Calculate trend duration (average same-sign return streak)
    trend_durations = []
    current_streak = 1
    for i in range(1, len(returns_list)):
        if (returns_list[i] > 0) == (returns_list[i - 1] > 0):
            current_streak += 1
        else:
            trend_durations.append(current_streak)
            current_streak = 1
    trend_durations.append(current_streak)
    avg_trend_duration = (
        sum(trend_durations) / len(trend_durations) if trend_durations else 0
    )

    # Run validation
    validation = validate_momentum_effect(
        autocorrelation_lag1=acf[0] if acf else 0,
        trend_duration_avg=avg_trend_duration,
        total_rounds=len(market_prices),
    )

    # Calculate max drawdown
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    plot_price_dynamics(
        market_prices,
        output_path=os.path.join(output_dir, "01_price_dynamics.png"),
    )

    plot_returns_analysis(
        market_prices,
        output_path=os.path.join(output_dir, "02_returns_analysis.png"),
    )

    plot_multi_panel_summary(
        market_prices,
        volatility=volatility,
        output_path=os.path.join(output_dir, "03_summary.png"),
    )

    # Calculate returns statistics
    returns_mean = sum(returns.values()) / len(returns) if returns else 0
    returns_std = (
        (sum((r - returns_mean) ** 2 for r in returns.values()) / len(returns)) ** 0.5
        if returns
        else 0
    )

    summary = {
        "scenario": "MomentumEffect",
        "total_rounds": len(market_prices),
        "momentum_detected": momentum_detected,
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
            "total": round(sum(returns.values()), 6) if returns else 0,
        },
        "metrics": {
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
            "avg_trend_duration": round(avg_trend_duration, 2),
        },
        "autocorrelation": {
            "lag_1": round(acf[0], 4) if len(acf) > 0 else None,
            "lag_2": round(acf[1], 4) if len(acf) > 1 else None,
            "lag_5": round(acf[4], 4) if len(acf) > 4 else None,
            "lag_10": round(acf[9], 4) if len(acf) > 9 else None,
        },
        "interpretation": (
            "MOMENTUM: Winners continue winning"
            if momentum_detected
            else "No significant momentum"
        ),
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("MOMENTUM ANALYSIS")
    print("=" * 50)
    print(f"Momentum Detected: {momentum_detected}")
    print(
        f"Return Autocorr (lag-1): {summary['autocorrelation']['lag_1']:.4f}"
        if summary["autocorrelation"]["lag_1"]
        else ""
    )
    print(
        f"Return Autocorr (lag-5): {summary['autocorrelation']['lag_5']:.4f}"
        if summary["autocorrelation"]["lag_5"]
        else ""
    )
    print(f"Avg Trend Duration: {avg_trend_duration:.1f} rounds")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


def main():
    """Run MomentumEffect analysis."""
    parser = argparse.ArgumentParser(description="Analyze MomentumEffect simulation")
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

    data = load_simulation_data(config)
    summary = analyze_momentum(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
