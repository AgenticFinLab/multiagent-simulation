"""MarketCrash Simulation Analysis

Analyzes simulation results for crash dynamics.
Detects panic selling cascades and crash depth/recovery patterns.

Usage:
    python examples/MarketCrash/analysis.py -c configs/MarketCrash/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_max_drawdown,
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_bubble_crash_analysis,
)
from masim.utils import load_config, load_simulation_data


def analyze_crash(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]

    if not market_prices:
        return {}

    # Fundamental value from simulation data
    fundamental_value = sum(fundamentals.values()) / len(fundamentals)

    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=5)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Crash detection
    crash_detected = max_dd < -15  # >15% drawdown = crash

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

    summary = {
        "crash_detected": crash_detected,
        "max_drawdown": max_dd,
        "peak_round": peak_idx,
        "trough_round": trough_idx,
        "crash_depth": min(market_prices.values()) if market_prices else 0,
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Crash Detected: {crash_detected}, Max Drawdown: {max_dd:.2f}%")
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

    data = load_simulation_data(config)
    return analyze_crash(data, output_dir)


if __name__ == "__main__":
    main()
