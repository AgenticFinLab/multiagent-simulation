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
    calculate_autocorrelation,
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_multi_panel_summary,
    validate_flash_crash,
)
from masim.utils import load_config, load_simulation_data, get_investor_quantities


def analyze_flash_crash(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform flash crash analysis."""
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    volumes = data.get("volumes", {})

    if not market_prices:
        print("No market price data found")
        return {}

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=5)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)
    returns_list = list(returns.values())
    acf = (
        calculate_autocorrelation(returns_list, max_lag=5)
        if len(returns_list) > 5
        else []
    )

    # Flash crash: rapid drop + quick recovery
    crash_speed = (trough_idx - peak_idx) if trough_idx > peak_idx else 0
    recovery_detected = (
        prices_list[-1] > prices_list[trough_idx] * 1.05
        if trough_idx < len(prices_list) - 1
        else False
    )
    flash_crash = max_dd < -5 and crash_speed < 10

    # Run validation
    validation = validate_flash_crash(
        max_drawdown=max_dd,
        crash_duration=crash_speed,
        recovery_detected=recovery_detected,
        total_rounds=len(market_prices),
    )

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    plot_price_dynamics(
        market_prices, output_path=os.path.join(output_dir, "01_price.png")
    )
    plot_volatility_analysis(
        market_prices,
        volatility,
        output_path=os.path.join(output_dir, "02_volatility.png"),
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
        "scenario": "FlashCrash",
        "total_rounds": len(market_prices),
        "flash_crash_detected": flash_crash,
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
            "crash_duration_rounds": crash_speed,
            "recovery_detected": recovery_detected,
            "peak_round": peak_idx,
            "trough_round": trough_idx,
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
    print("FLASH CRASH ANALYSIS")
    print("=" * 50)
    print(f"Flash Crash Detected: {flash_crash}")
    print(f"Max Drawdown: {max_dd:.2f}%")
    print(f"Crash Duration: {crash_speed} rounds")
    print(f"Recovery: {'Yes' if recovery_detected else 'No'}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

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
