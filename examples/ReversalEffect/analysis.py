"""ReversalEffect Simulation Analysis

Analyzes long-term reversal patterns (mean reversion).
Tests whether past losers outperform past winners.

Usage:
    python examples/ReversalEffect/analysis.py -c configs/ReversalEffect/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_autocorrelation,
    plot_price_dynamics,
    plot_returns_analysis,
)
from masim.utils import load_config, load_simulation_data


def analyze_reversal(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]

    if not market_prices:
        return {}

    # Fundamental value from simulation data
    fundamental_value = sum(fundamentals.values()) / len(fundamentals)

    returns = calculate_returns(market_prices)
    returns_list = list(returns.values())
    acf = calculate_autocorrelation(returns_list, max_lag=20)

    # Reversal: negative long-lag autocorrelation
    reversal_detected = acf[9] < -0.1 if len(acf) > 9 else False

    plot_price_dynamics(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "01_price.png"),
    )
    plot_returns_analysis(
        market_prices, output_path=os.path.join(output_dir, "02_returns.png")
    )

    summary = {
        "reversal_detected": reversal_detected,
        "autocorrelation": {
            "lag_1": acf[0] if acf else 0,
            "lag_10": acf[9] if len(acf) > 9 else 0,
        },
        "interpretation": (
            "REVERSAL: Mean reversion detected" if reversal_detected else "No reversal"
        ),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Reversal Detected: {reversal_detected}")
    return summary


def main():
    """Run ReversalEffect analysis."""
    parser = argparse.ArgumentParser(description="Analyze ReversalEffect simulation")
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
    return analyze_reversal(data, output_dir)


if __name__ == "__main__":
    main()
