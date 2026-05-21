"""AssetBubble Simulation Analysis

Analyzes simulation results for bubble formation and crash dynamics.
Detects positive feedback loops and price deviation from fundamental.

Usage:
    python examples/AssetBubble/Rule/analysis.py -c configs/AssetBubble/Rule/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.finance import (
    calculate_returns,
    calculate_rolling_volatility,
    calculate_price_deviation,
    calculate_max_drawdown,
    calculate_bubble_magnitude,
    calculate_autocorrelation,
    plot_price_dynamics,
    plot_bubble_crash_analysis,
    plot_multi_panel_summary,
    validate_asset_bubble,
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
    Player turns → decision_payload fields bid_price / quantity

    Returns
    -------
    dict with keys:
        market_prices       : {round_num: float}
        fundamentals        : {round_num: float}
        volumes             : {round_num: float}
        investor_quantities : {player_id: {round_num: float}}
        investor_bids       : {player_id: {round_num: float}}
    """
    # --- market (coordinator) player: read from batch stores ---
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

    # --- non-coordinator (investor) players: read from turn decision_payloads ---
    # payload fields: bid_price (submitted order price), quantity (signed order size)
    investor_quantities: Dict[str, Dict[int, float]] = {}
    investor_bids: Dict[str, Dict[int, float]] = {}
    for pid, player in results.players_by_role("player").items():
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "volumes": volumes,
        "investor_quantities": investor_quantities,
        "investor_bids": investor_bids,
    }


_BID_COLORS = [
    "#3a86ff",
    "#ff006e",
    "#8338ec",
    "#06d6a0",
    "#fb5607",
    "#ff595e",
    "#1982c4",
    "#6a4c93",
    "#ffca3a",
    "#8ac926",
    "#e07a5f",
    "#3d405b",
    "#81b29a",
    "#f2cc8f",
    "#264653",
    "#e63946",
    "#457b9d",
    "#2a9d8f",
    "#e9c46a",
    "#f4a261",
]


def analyze_bubble(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform bubble/crash analysis."""
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    volumes = data["volumes"]
    investor_quantities = data["investor_quantities"]

    if not market_prices:
        print("No market price data found")
        return {}

    # Fundamental value must come from simulation data
    prices_list_tmp = [market_prices[r] for r in sorted(market_prices.keys())]
    if not fundamentals:
        raise ValueError("No fundamental data recorded - simulation data is incomplete")
    fundamental_value = sum(fundamentals.values()) / len(fundamentals)

    # Calculate metrics
    returns = calculate_returns(market_prices)
    volatility = calculate_rolling_volatility(market_prices, window=10)
    deviation = calculate_price_deviation(market_prices, fundamental_value)
    bubble = calculate_bubble_magnitude(market_prices, fundamental_value)
    returns_list = list(returns.values())
    autocorr = (
        calculate_autocorrelation(returns_list, max_lag=5)
        if len(returns_list) > 5
        else []
    )

    prices_list = [market_prices[r] for r in sorted(market_prices.keys())]
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Bubble detection
    if not deviation:
        raise ValueError(
            "No deviation data computed - price deviation calculation failed"
        )
    max_deviation = max(deviation.values())
    if not bubble:
        raise ValueError(
            "No bubble magnitude data computed - bubble calculation failed"
        )
    max_bubble = max(bubble.values())
    bubble_detected = max_deviation > 20  # >20% deviation = bubble

    # Run validation
    validation = validate_asset_bubble(
        market_prices=market_prices,
        fundamental=fundamental_value,
        max_deviation_pct=max_deviation,
        max_drawdown=max_dd,
        total_rounds=len(market_prices),
    )

    # Generate plots
    print(f"Generating analysis plots in {output_dir}/")

    # --- Plot 0: Investor Bid Curves (PRIMARY headline chart) ---
    investor_bids = data["investor_bids"]
    rounds_sorted = sorted(market_prices.keys())
    _rounds_arr = np.array(rounds_sorted)
    _prices_arr = np.array([market_prices[r] for r in rounds_sorted])
    fig0, ax0 = plt.subplots(figsize=(16, 8))
    fig0.suptitle(
        "AssetBubble Rule \u2014 Investor Bidding Curves",
        fontsize=14,
        fontweight="bold",
    )
    ax0.plot(
        _rounds_arr,
        _prices_arr,
        color="#f0a500",
        linewidth=2.5,
        label="Market Price",
        zorder=10,
    )
    ax0.axhline(
        y=fundamental_value,
        color="darkgreen",
        linestyle="--",
        linewidth=1.2,
        label=f"Fundamental (F={fundamental_value:.2f})",
        alpha=0.8,
    )
    for _i, (_pid, _bids) in enumerate(sorted(investor_bids.items())):
        _br = sorted(_bids.keys())
        _bv = [float(_bids[r]) for r in _br]
        ax0.plot(
            _br,
            _bv,
            marker="o",
            markersize=2,
            linewidth=0.9,
            color=_BID_COLORS[_i % len(_BID_COLORS)],
            alpha=0.8,
            label=_pid.replace("_", " ").title(),
        )
    ax0.set_xlabel("Round", fontsize=12)
    ax0.set_ylabel("Price", fontsize=12)
    ax0.set_title("Market Price & Individual Investor Bids", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=min(5, len(investor_bids) + 2),
        fontsize=8,
        frameon=True,
        framealpha=0.7,
    )
    plt.tight_layout()
    _p0 = os.path.join(output_dir, "00_investor_bids.png")
    plt.savefig(_p0, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {_p0}")

    plot_price_dynamics(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "01_assetbubble_dynamics.png"),
    )

    plot_bubble_crash_analysis(
        market_prices,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "02_assetbubble_analysis.png"),
    )

    plot_multi_panel_summary(
        market_prices,
        volatility=volatility,
        investor_quantities=investor_quantities,
        fundamental=fundamental_value,
        output_path=os.path.join(output_dir, "03_summary.png"),
    )

    summary = {
        "scenario": "AssetBubble",
        "total_rounds": len(market_prices),
        "fundamental_value": fundamental_value,
        "bubble_detected": bubble_detected,
        "metrics": {
            "max_deviation_pct": round(max_deviation, 4),
            "max_bubble_magnitude": round(max_bubble, 4),
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
            "crash_duration": trough_idx - peak_idx if trough_idx > peak_idx else 0,
            "return_autocorr_lag1": round(autocorr[0], 4),
        },
        "price": {
            "initial": round(prices_list[0], 4),
            "final": round(prices_list[-1], 4),
            "min": round(min(prices_list), 4),
            "max": round(max(prices_list), 4),
            "mean": round(sum(prices_list) / len(prices_list), 4),
        },
        "returns": {
            "mean": round(sum(returns.values()) / len(returns), 6),
            "std": round(
                (
                    sum(
                        (r - sum(returns.values()) / len(returns)) ** 2
                        for r in returns.values()
                    )
                    / len(returns)
                )
                ** 0.5,
                6,
            ),
        },
        "volume": {
            "total": sum(volumes.values()),
            "avg": round(sum(volumes.values()) / len(volumes), 4),
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("BUBBLE ANALYSIS")
    print("=" * 50)
    print(f"Bubble Detected: {bubble_detected}")
    print(f"Max Price Deviation: {max_deviation:.2f}%")
    print(f"Max Drawdown (Crash): {max_dd:.2f}%")
    print(f"Peak Price: {max(market_prices.values()):.2f}")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


def main():
    """Run AssetBubble analysis."""
    parser = argparse.ArgumentParser(description="Analyze AssetBubble simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    # Load config and derive paths
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Load results lazily, then extract analysis dicts
    results = load_results(config)
    data = _load_data(results)
    summary = analyze_bubble(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
