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

import numpy as np

from masim.evaluation.finance import (
    calculate_returns,
    calculate_autocorrelation,
    calculate_rolling_volatility,
    calculate_max_drawdown,
    calculate_price_deviation,
    plot_price_dynamics,
    plot_returns_analysis,
    plot_multi_panel_summary,
    validate_reversal_effect,
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
    Player turns → decision_payload field quantity

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


def analyze_reversal(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform reversal effect analysis."""
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    volumes = data.get("volumes", {})
    investor_quantities = data.get("investor_quantities", {})

    if not market_prices:
        print("No market price data found")
        return {}

    # Fundamental value from simulation data
    fundamental_value = sum(fundamentals.values()) / len(fundamentals)

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=10)
    returns_list = list(returns.values())
    acf = calculate_autocorrelation(returns_list, max_lag=20)
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)
    deviation = calculate_price_deviation(market_prices, fundamental_value)

    # Reversal: negative long-lag autocorrelation (De Bondt & Thaler 1985)
    long_lag = 15 if len(acf) > 15 else (len(acf) - 1 if acf else 0)
    long_lag_acf = float(acf[long_lag - 1]) if long_lag > 0 and acf else 0.0
    reversal_detected = bool(long_lag_acf < -0.05) if acf else False

    # Run validation
    validation = validate_reversal_effect(
        autocorrelation_long=long_lag_acf,
        winner_loser_spread=None,  # Would need portfolio tracking
        total_rounds=len(market_prices),
    )

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    plot_price_dynamics(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "01_price.png"),
    )
    plot_returns_analysis(
        market_prices, output_path=os.path.join(output_dir, "02_returns.png")
    )
    plot_multi_panel_summary(
        market_prices,
        volatility=volatility,
        investor_quantities=investor_quantities,
        fundamental=fundamental_value,
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
        "scenario": "ReversalEffect",
        "total_rounds": len(market_prices),
        "fundamental_value": fundamental_value,
        "reversal_detected": reversal_detected,
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
            "max_deviation_pct": round(max(deviation.values()), 4) if deviation else 0,
            "final_deviation_pct": (
                round(list(deviation.values())[-1], 4) if deviation else 0
            ),
        },
        "autocorrelation": {
            "lag_1": round(acf[0], 4) if acf else None,
            "lag_5": round(acf[4], 4) if len(acf) > 4 else None,
            "lag_10": round(acf[9], 4) if len(acf) > 9 else None,
            "lag_15": round(acf[14], 4) if len(acf) > 14 else None,
            "lag_20": round(acf[19], 4) if len(acf) > 19 else None,
        },
        "interpretation": (
            "REVERSAL: Mean reversion detected" if reversal_detected else "No reversal"
        ),
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(
            summary,
            f,
            indent=2,
            default=lambda x: (
                int(x)
                if isinstance(x, (np.bool_, np.integer))
                else float(x) if isinstance(x, np.floating) else str(x)
            ),
        )

    print("\n" + "=" * 50)
    print("REVERSAL EFFECT ANALYSIS")
    print("=" * 50)
    print(f"Reversal Detected: {reversal_detected}")
    print(f"Short-lag ACF (lag-1): {acf[0]:.4f}" if acf else "")
    print(f"Long-lag ACF (lag-{long_lag}): {long_lag_acf:.4f}")
    print(f"Mean Reversion to Fundamental: {fundamental_value:.2f}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

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

    results = load_results(config)
    data = _load_data(results)
    return analyze_reversal(data, output_dir)


if __name__ == "__main__":
    main()
