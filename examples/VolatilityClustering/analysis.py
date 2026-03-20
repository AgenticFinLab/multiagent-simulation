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
    calculate_max_drawdown,
    calculate_autocorrelation,
    plot_price_dynamics,
    plot_volatility_analysis,
    plot_multi_panel_summary,
    validate_volatility_clustering,
)
from masim.utils import load_config, load_results


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert a batch store list to {round_num: value} (round_num starts at 1)."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Extract market prices from a SimulationResults object.

    Data source: coordinator batch store 'price'.

    Returns
    -------
    dict with keys:
        market_prices : {round_num: float}
    """
    market_prices: Dict[int, float] = {}
    for player in results.players_by_role("coordinator").values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
    return {"market_prices": market_prices}


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

    # Calculate max drawdown
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Clustering ratio
    sq_acf = clustering.get("sq_return_autocorr_1", 0)
    ret_acf = garch_result.get("return_autocorr_lag1", 0.001)
    clustering_ratio = sq_acf / abs(ret_acf) if abs(ret_acf) > 0.001 else sq_acf * 100

    # Run validation
    validation = validate_volatility_clustering(
        return_acf=ret_acf,
        squared_return_acf=sq_acf,
        clustering_ratio=clustering_ratio,
    )

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

    # Calculate returns statistics
    returns_mean = sum(returns.values()) / len(returns) if returns else 0
    returns_std = (
        (sum((r - returns_mean) ** 2 for r in returns.values()) / len(returns)) ** 0.5
        if returns
        else 0
    )

    # Compile summary
    summary = {
        "scenario": "VolatilityClustering",
        "total_rounds": len(market_prices),
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
        },
        "garch_signature": {
            "has_signature": garch_result["has_garch_signature"],
            "interpretation": garch_result["interpretation"],
            "return_acf_lag1": round(ret_acf, 4),
            "squared_return_acf": round(sq_acf, 4),
            "clustering_ratio": round(clustering_ratio, 2),
        },
        "volatility_persistence": {
            "vol_autocorr_1": round(persistence.get("vol_autocorr_1", 0), 4),
            "vol_autocorr_5": round(persistence.get("vol_autocorr_5", 0), 4),
        },
        "return_clustering": {
            "sq_return_autocorr_1": round(clustering.get("sq_return_autocorr_1", 0), 4),
            "abs_return_autocorr_1": round(
                clustering.get("abs_return_autocorr_1", 0), 4
            ),
        },
        "volatility_regimes": {
            "avg_vol": round(regimes.get("avg_vol", 0), 6),
            "high_vol_episodes": len(regimes.get("high_vol_episodes", [])),
            "low_vol_episodes": len(regimes.get("low_vol_episodes", [])),
            "regime_persistence": round(regimes.get("regime_persistence", 0), 4),
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + "=" * 50)
    print("GARCH SIGNATURE ANALYSIS")
    print("=" * 50)
    print(f"Has GARCH Signature: {garch_result['has_garch_signature']}")
    print(f"Interpretation: {garch_result['interpretation']}")
    print(f"Return ACF (lag-1): {ret_acf:.4f}")
    print(f"Squared Return ACF: {sq_acf:.4f}")
    print(f"Clustering Ratio: {clustering_ratio:.2f}")
    print(f"Vol Autocorr (lag-1): {persistence.get('vol_autocorr_1', 0):.4f}")
    print(f"High Vol Episodes: {len(regimes.get('high_vol_episodes', []))}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

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

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_volatility_clustering(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
