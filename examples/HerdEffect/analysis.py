"""HerdEffect Simulation Analysis

Analyzes simulation results using the centralized evaluation module.

Usage:
    python examples/HerdEffect/analysis.py -c configs/HerdEffect/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_price_deviation,
    calculate_max_drawdown,
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
    calculate_cascade_measure,
    calculate_cross_sectional_std,
    detect_herding_episodes,
    calculate_volume_metrics,
    calculate_bubble_magnitude,
    plot_price_dynamics,
    plot_herding_metrics,
    plot_volatility_analysis,
    plot_multi_panel_summary,
    validate_herd_effect,
)
from masim.utils import (
    load_config,
    load_simulation_data,
    get_investor_quantities,
    get_investor_bids,
)


def analyze_herding(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """
    Perform comprehensive herding analysis.

    Args:
        data: Simulation data dictionary
        output_dir: Output directory for plots

    Returns:
        Summary statistics dictionary
    """
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_bids = get_investor_bids(data)
    investor_quantities = get_investor_quantities(data)

    if not market_prices:
        print("No market price data found")
        return {}

    # Fundamental value from simulation data
    fundamental_value = sum(fundamentals.values()) / len(fundamentals)

    # ===========================================
    # 1. Calculate Core Metrics
    # ===========================================

    # Returns and volatility
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=10)
    deviation = calculate_price_deviation(market_prices, fundamental_value)

    # Drawdown analysis
    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # ===========================================
    # 2. Herding Metrics
    # ===========================================

    cv_series = {}
    agreement_series = {}
    cascade_series = {}

    if investor_bids:
        cv_series = calculate_bid_convergence_cv(investor_bids)
        agreement_series = calculate_directional_agreement(investor_bids)
        cascade_series = calculate_cascade_measure(
            investor_bids, market_prices, fundamental_value
        )
        cross_std = calculate_cross_sectional_std(investor_bids)

        # Detect herding episodes
        herding_episodes = detect_herding_episodes(
            cv_series, threshold=0.10, min_duration=3
        )
    else:
        herding_episodes = []

    # ===========================================
    # 3. Volume Metrics
    # ===========================================

    volume_metrics = {}
    if investor_quantities:
        volume_metrics = calculate_volume_metrics(investor_quantities)

    # Bubble magnitude
    bubble = calculate_bubble_magnitude(market_prices, fundamental_value)

    # ===========================================
    # 4. Generate Visualizations
    # ===========================================

    print(f"Generating analysis plots in {output_dir}/")

    # Plot 1: Price dynamics
    plot_price_dynamics(
        market_prices,
        fundamental=fundamental_value,
        investor_bids=investor_bids,
        output_path=os.path.join(output_dir, "01_price_dynamics.png"),
    )

    # Plot 2: Herding metrics
    if cv_series and agreement_series:
        plot_herding_metrics(
            cv_series,
            agreement_series,
            output_path=os.path.join(output_dir, "02_herding_metrics.png"),
        )

    # Plot 3: Volatility analysis
    if volatility:
        plot_volatility_analysis(
            market_prices,
            volatility,
            output_path=os.path.join(output_dir, "03_volatility.png"),
        )

    # Plot 4: Multi-panel summary
    plot_multi_panel_summary(
        market_prices,
        volatility=volatility,
        investor_quantities=investor_quantities,
        output_path=os.path.join(output_dir, "04_summary.png"),
    )

    # ===========================================
    # 5. Run Validation
    # ===========================================

    avg_cv = sum(cv_series.values()) / len(cv_series) if cv_series else 0
    avg_agreement = (
        sum(agreement_series.values()) / len(agreement_series)
        if agreement_series
        else 0
    )
    max_dev = max(deviation.values()) if deviation else 0

    validation = validate_herd_effect(
        avg_cv=avg_cv,
        avg_agreement=avg_agreement,
        max_deviation=max_dev,
        herding_episodes=len(herding_episodes),
        total_rounds=len(market_prices),
    )

    # ===========================================
    # 6. Compile Summary Statistics
    # ===========================================

    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    returns_mean = sum(returns.values()) / len(returns) if returns else 0
    returns_std = (
        (sum((r - returns_mean) ** 2 for r in returns.values()) / len(returns)) ** 0.5
        if returns
        else 0
    )

    summary = {
        "scenario": "HerdEffect",
        "total_rounds": len(market_prices),
        "fundamental_value": fundamental_value,
        "price": {
            "initial": round(prices_list[0], 4) if prices_list else 0,
            "final": round(prices_list[-1], 4) if prices_list else 0,
            "min": round(min(prices_list), 4) if prices_list else 0,
            "max": round(max(prices_list), 4) if prices_list else 0,
            "mean": round(sum(prices_list) / len(prices_list), 4) if prices_list else 0,
        },
        "returns": {
            "mean": round(returns_mean, 6),
            "std": round(returns_std, 6),
        },
        "metrics": {
            "max_deviation_pct": round(max_dev, 4),
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
        },
        "herding": {
            "avg_cv": round(avg_cv, 4),
            "min_cv": round(min(cv_series.values()), 4) if cv_series else None,
            "max_cv": round(max(cv_series.values()), 4) if cv_series else None,
            "avg_agreement": round(avg_agreement, 4),
            "max_agreement": (
                round(max(agreement_series.values()), 4) if agreement_series else None
            ),
            "episodes_detected": len(herding_episodes),
            "episode_rounds": herding_episodes,
        },
        "volume": volume_metrics if volume_metrics else {},
        "bubble_magnitude_final": round(list(bubble.values())[-1], 4) if bubble else 0,
        "validation": validation.to_dict(),
    }

    # Save summary to JSON
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAnalysis complete! Results saved to {output_dir}/")
    print(f"  - 01_price_dynamics.png")
    print(f"  - 02_herding_metrics.png")
    print(f"  - 03_volatility.png")
    print(f"  - 04_summary.png")
    print(f"  - summary.json")

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    print(f"Total Rounds: {summary['total_rounds']}")
    print(
        f"Price Range: {summary['price_range']['min']:.2f} - {summary['price_range']['max']:.2f}"
    )
    print(f"Final Price: {summary['price_range']['final']:.2f}")
    print(f"Max Drawdown: {max_dd:.2f}%")
    print(f"Avg Bid CV: {summary['herding']['avg_cv']:.4f}")
    print(f"Avg Directional Agreement: {summary['herding']['avg_agreement']:.4f}")
    print(f"Herding Episodes: {summary['herding']['episodes_detected']}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


def main():
    """Run HerdEffect analysis."""
    parser = argparse.ArgumentParser(description="Analyze HerdEffect simulation")
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

    print(f"Loading simulation data...")
    data = load_simulation_data(config)
    summary = analyze_herding(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
