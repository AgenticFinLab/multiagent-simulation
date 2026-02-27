"""FlashCrash Simulation Analysis

Analyzes flash crash dynamics - rapid crash with quick recovery.

Usage:
    python examples/FlashCrash/analysis.py -c configs/FlashCrash/simulation.yml
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
)
from masim.utils import load_config, load_simulation_data


def analyze_flash_crash(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    if not market_prices:
        return {}

    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=5)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Flash crash: rapid drop + quick recovery
    crash_speed = (trough_idx - peak_idx) if trough_idx > peak_idx else 0
    recovery_detected = (
        prices_list[-1] > prices_list[trough_idx] * 1.05
        if trough_idx < len(prices_list) - 1
        else False
    )
    flash_crash = max_dd < -5 and crash_speed < 10

    plot_price_dynamics(
        market_prices, output_path=os.path.join(output_dir, "01_price.png")
    )
    plot_volatility_analysis(
        market_prices,
        volatility,
        output_path=os.path.join(output_dir, "02_volatility.png"),
    )

    summary = {
        "flash_crash_detected": flash_crash,
        "max_drawdown": max_dd,
        "crash_duration_rounds": crash_speed,
        "recovery_detected": recovery_detected,
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(
        f"Flash Crash: {flash_crash}, Drawdown: {max_dd:.2f}%, Speed: {crash_speed} rounds"
    )
    return summary


def main():
    """Run FlashCrash analysis."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrash simulation")
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
    return analyze_flash_crash(data, output_dir)


if __name__ == "__main__":
    main()
