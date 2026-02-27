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
    plot_price_dynamics,
    plot_returns_analysis,
    plot_multi_panel_summary,
)
from masim.utils import load_config, load_simulation_data


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

    summary = {
        "total_rounds": len(market_prices),
        "momentum_detected": momentum_detected,
        "autocorrelation": {
            "lag_1": acf[0] if len(acf) > 0 else 0,
            "lag_5": acf[4] if len(acf) > 4 else 0,
            "lag_10": acf[9] if len(acf) > 9 else 0,
        },
        "returns": {
            "mean": sum(returns.values()) / len(returns) if returns else 0,
            "total": sum(returns.values()) if returns else 0,
        },
        "interpretation": (
            "MOMENTUM: Winners continue winning"
            if momentum_detected
            else "No significant momentum"
        ),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("MOMENTUM ANALYSIS")
    print("=" * 50)
    print(f"Momentum Detected: {momentum_detected}")
    print(f"Return Autocorr (lag-1): {summary['autocorrelation']['lag_1']:.4f}")
    print(f"Return Autocorr (lag-5): {summary['autocorrelation']['lag_5']:.4f}")
    print(f"Interpretation: {summary['interpretation']}")

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
