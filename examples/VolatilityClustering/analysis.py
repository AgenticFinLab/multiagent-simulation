"""VolatilityClustering Simulation Analysis

Analyzes simulation results for GARCH-style volatility clustering patterns.
Tests whether volatility exhibits persistence (high vol → high vol).

Usage:
    python examples/VolatilityClustering/analysis.py -c configs/VolatilityClustering/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_garch_signature,
    calculate_volatility_persistence,
    calculate_return_clustering,
    detect_volatility_regimes,
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_multi_panel_summary,
)
from masim.utils import load_config, load_simulation_data


def analyze_volatility_clustering(
    data: Dict[str, Any], output_dir: str
) -> Dict[str, Any]:
    """Perform GARCH-style volatility clustering analysis."""
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    if not market_prices:
        print("No market price data found")
        return {}

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=10)

    # GARCH signature test
    garch_result = calculate_garch_signature(market_prices)

    # Volatility persistence
    persistence = calculate_volatility_persistence(volatility)

    # Return clustering
    clustering = calculate_return_clustering(returns)

    # Regime detection
    regimes = detect_volatility_regimes(volatility)

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    plot_price_dynamics(
        market_prices,
        output_path=os.path.join(output_dir, "01_price_dynamics.png"),
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

    # Compile summary
    summary = {
        "total_rounds": len(market_prices),
        "garch_signature": {
            "has_signature": garch_result["has_garch_signature"],
            "interpretation": garch_result["interpretation"],
        },
        "volatility_persistence": persistence,
        "return_clustering": clustering,
        "volatility_regimes": {
            "avg_vol": regimes["avg_vol"],
            "high_vol_episodes": len(regimes["high_vol_episodes"]),
            "low_vol_episodes": len(regimes["low_vol_episodes"]),
            "regime_persistence": regimes["regime_persistence"],
        },
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + "=" * 50)
    print("GARCH SIGNATURE ANALYSIS")
    print("=" * 50)
    print(f"Has GARCH Signature: {garch_result['has_garch_signature']}")
    print(f"Interpretation: {garch_result['interpretation']}")
    print(f"Vol Autocorr (lag-1): {persistence['vol_autocorr_1']:.4f}")
    print(f"Squared Return Autocorr: {clustering['sq_return_autocorr_1']:.4f}")
    print(f"High Vol Episodes: {len(regimes['high_vol_episodes'])}")

    return summary


def main():
    """Run VolatilityClustering analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze VolatilityClustering simulation"
    )
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
    summary = analyze_volatility_clustering(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
