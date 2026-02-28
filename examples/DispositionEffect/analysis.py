"""DispositionEffect Analysis - Prospect Theory Trading Evaluation

Analyzes disposition effect (Shefrin & Statman 1985):
- Sell winners too early, hold losers too long
- Key metrics: PGR (Proportion of Gains Realized), PLR (Proportion of Losses Realized)
- Disposition effect present when PGR > PLR

Usage:
    python examples/DispositionEffect/analysis.py -c configs/DispositionEffect/simulation.yml

Academic References:
    - Shefrin & Statman (1985): Original disposition effect paper
    - Kahneman & Tversky (1979): Prospect theory foundation
    - Odean (1998): Empirical evidence from trading data
"""

import argparse
import glob
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from typing import Any, Dict, List, Optional

from masim.evaluation.finance import (
    # Time Series
    calculate_returns,
    calculate_rolling_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    # Visualization
    plot_price_dynamics,
    create_figure,
    save_figure,
    # Validation
    validate_disposition_effect,
)
from masim.utils import load_config


def load_simulation_data(record_dir: str) -> Dict[str, Any]:
    """Load simulation data from record directory."""
    data = {"prices": [], "trades": defaultdict(list), "rounds": []}
    price_data = {}  # round -> price mapping

    # Load price history from market turns data
    market_turns_dir = os.path.join(record_dir, "market", "turns")
    if os.path.exists(market_turns_dir):
        for f in sorted(glob.glob(os.path.join(market_turns_dir, "*.json"))):
            if "store-information" in f:
                continue
            with open(f, encoding="utf-8") as fp:
                try:
                    turn_block = json.load(fp)
                    for turn_key, turn_data in turn_block.items():
                        round_num = turn_data.get("round_num", 0)
                        turn_result = turn_data.get("turn_result", {})
                        step_results = turn_result.get("step_results", [])
                        for step in step_results:
                            payload = step.get("decision_payload", {})
                            market_data = payload.get("market_data", {})
                            if "price" in market_data:
                                price_data[round_num] = market_data["price"]
                except (json.JSONDecodeError, KeyError):
                    continue
    
    # Sort by round and extract prices
    for round_num in sorted(price_data.keys()):
        data["prices"].append(price_data[round_num])

    # Load turn data from all players
    turns_pattern = os.path.join(record_dir, "*", "turns", "*.json")
    for f in sorted(glob.glob(turns_pattern)):
        if "store-information" in f:
            continue
        with open(f, encoding="utf-8") as fp:
            try:
                turn_data = json.load(fp)
                player_id = f.split(os.sep)[-3]
                if "strategy" in turn_data:
                    data["trades"][player_id].append(turn_data)
            except (json.JSONDecodeError, KeyError):
                continue

    return data


def calculate_pgr_plr(trades: List[Dict], prices: List[float]) -> Dict[str, float]:
    """
    Calculate Proportion of Gains/Losses Realized (PGR/PLR).

    PGR = Realized Gains / (Realized Gains + Paper Gains)
    PLR = Realized Losses / (Realized Losses + Paper Losses)

    Disposition Effect: PGR > PLR
    """
    realized_gains = 0
    paper_gains = 0
    realized_losses = 0
    paper_losses = 0

    # Track positions and purchase prices
    position = 30.0  # Initial position
    purchase_price = 100.0  # Initial reference point

    for i, trade in enumerate(trades):
        if i >= len(prices):
            break

        current_price = prices[i]
        quantity = trade["quantity"]

        # Calculate gain/loss at current price
        if position > 0 and purchase_price > 0:
            unit_gain = current_price - purchase_price

            if quantity < 0:  # Selling
                realized_qty = min(abs(quantity), position)
                if unit_gain > 0:
                    realized_gains += realized_qty * unit_gain
                else:
                    realized_losses += realized_qty * abs(unit_gain)

            # Paper gains/losses (unrealized)
            remaining = position - abs(quantity) if quantity < 0 else position
            if remaining > 0:
                if unit_gain > 0:
                    paper_gains += remaining * unit_gain
                else:
                    paper_losses += remaining * abs(unit_gain)

        # Update position (simplified)
        position = max(0, position + quantity)
        if quantity > 0 and current_price > 0:
            # Update reference price (average cost)
            total_cost = (
                purchase_price * (position - quantity) + current_price * quantity
            )
            purchase_price = total_cost / position if position > 0 else current_price

    # Calculate PGR and PLR
    pgr = (
        realized_gains / (realized_gains + paper_gains)
        if (realized_gains + paper_gains) > 0
        else 0
    )
    plr = (
        realized_losses / (realized_losses + paper_losses)
        if (realized_losses + paper_losses) > 0
        else 0
    )

    return {
        "pgr": pgr,
        "plr": plr,
        "disposition_ratio": pgr / plr if plr > 0 else float("inf"),
        "disposition_effect": pgr > plr,
        "realized_gains": realized_gains,
        "realized_losses": realized_losses,
        "paper_gains": paper_gains,
        "paper_losses": paper_losses,
    }


def analyze_by_strategy(data: Dict[str, Any]) -> Dict[str, Dict]:
    """Analyze disposition metrics by strategy type."""
    prices = data["prices"]
    results = {}

    for player_id, trades in data["trades"].items():
        if not trades:
            continue

        strategy = trades[0]["strategy"]

        # Calculate PGR/PLR
        metrics = calculate_pgr_plr(trades, prices)

        # Calculate trading activity
        buy_count = sum(1 for t in trades if t["quantity"] > 0)
        sell_count = sum(1 for t in trades if t["quantity"] < 0)
        total_volume = sum(abs(t["quantity"]) for t in trades)

        results[player_id] = {
            "strategy": strategy,
            **metrics,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "total_volume": total_volume,
        }

    return results


def plot_disposition_analysis(
    data: Dict[str, Any],
    strategy_results: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Generate disposition effect analysis plots."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    # Calculate returns directly from prices array
    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])

    # Figure 1: Price dynamics with news events
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Price dynamics
    ax1 = axes[0, 0]
    ax1.plot(prices, "b-", linewidth=1.5, label="Price")
    ax1.axhline(y=100, color="gray", linestyle="--", alpha=0.5, label="Fundamental")
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Price")
    ax1.set_title("Price Dynamics with News Shocks")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: PGR vs PLR comparison
    ax2 = axes[0, 1]
    strategies = []
    pgr_values = []
    plr_values = []
    for pid, res in strategy_results.items():
        if res["strategy"] != "market":
            strategies.append(res["strategy"][:12])
            pgr_values.append(res["pgr"])
            plr_values.append(res["plr"])

    x = np.arange(len(strategies))
    width = 0.35
    ax2.bar(
        x - width / 2,
        pgr_values,
        width,
        label="PGR (Gains Realized)",
        color="green",
        alpha=0.7,
    )
    ax2.bar(
        x + width / 2,
        plr_values,
        width,
        label="PLR (Losses Realized)",
        color="red",
        alpha=0.7,
    )
    ax2.set_xlabel("Strategy")
    ax2.set_ylabel("Proportion")
    ax2.set_title("Disposition Effect: PGR vs PLR\n(PGR > PLR = Disposition Effect)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(strategies, rotation=45, ha="right")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Panel 3: Returns distribution
    ax3 = axes[1, 0]
    ax3.hist(returns * 100, bins=50, color="blue", alpha=0.7, edgecolor="black")
    ax3.axvline(x=0, color="red", linestyle="--", linewidth=2, label="Zero Return")
    ax3.set_xlabel("Return (%)")
    ax3.set_ylabel("Frequency")
    ax3.set_title("Return Distribution")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Panel 4: Disposition ratio by strategy
    ax4 = axes[1, 1]
    disp_ratios = [
        res["disposition_ratio"]
        for pid, res in strategy_results.items()
        if res["strategy"] != "market"
    ]
    disp_ratios = [min(r, 5) for r in disp_ratios]  # Cap at 5 for visualization

    colors = ["red" if r > 1 else "green" for r in disp_ratios]
    ax4.bar(strategies, disp_ratios, color=colors, alpha=0.7)
    ax4.axhline(
        y=1,
        color="black",
        linestyle="--",
        linewidth=2,
        label="No Disposition (PGR=PLR)",
    )
    ax4.set_xlabel("Strategy")
    ax4.set_ylabel("Disposition Ratio (PGR/PLR)")
    ax4.set_title("Disposition Ratio by Strategy\n(>1 = Disposition Effect)")
    ax4.set_xticklabels(strategies, rotation=45, ha="right")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "disposition_analysis.png"))
    plt.close()


def generate_summary(
    data: Dict[str, Any],
    strategy_results: Dict[str, Dict],
) -> Dict[str, Any]:
    """Generate summary statistics with validation."""
    prices = np.array(data["prices"])
    # Calculate returns directly from prices array
    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
    prices_list = list(prices)
    max_dd, peak_idx, trough_idx = (
        calculate_max_drawdown(prices_list) if len(prices_list) > 1 else (0, 0, 0)
    )

    # Find disposition investor
    disp_result = None
    rational_result = None
    for pid, res in strategy_results.items():
        if "disposition" in res["strategy"]:
            disp_result = res
        if "rational" in res["strategy"]:
            rational_result = res

    # Extract PGR and PLR for validation
    pgr = disp_result["pgr"] if disp_result else 0
    plr = disp_result["plr"] if disp_result else 0
    disposition_coefficient = pgr - plr

    # Run validation
    validation = validate_disposition_effect(
        pgr=pgr,
        plr=plr,
        disposition_coefficient=disposition_coefficient,
    )

    return {
        "scenario": "DispositionEffect",
        "total_rounds": len(prices),
        "price_statistics": {
            "initial_price": float(prices[0]) if len(prices) > 0 else 0,
            "final_price": float(prices[-1]) if len(prices) > 0 else 0,
            "max_price": float(np.max(prices)) if len(prices) > 0 else 0,
            "min_price": float(np.min(prices)) if len(prices) > 0 else 0,
            "volatility": float(np.std(returns) * 100) if len(returns) > 0 else 0,
        },
        "metrics": {
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
        },
        "disposition_metrics": {
            "pgr": round(pgr, 4),
            "plr": round(plr, 4),
            "disposition_coefficient": round(disposition_coefficient, 4),
            "disposition_ratio": round(pgr / plr, 4) if plr > 0 else None,
        },
        "disposition_investor": disp_result if disp_result else {},
        "rational_investor": rational_result if rational_result else {},
        "disposition_effect_detected": (
            disp_result["disposition_effect"] if disp_result else False
        ),
        "strategy_comparison": {
            pid: {
                "strategy": res["strategy"],
                "pgr": round(res["pgr"], 4),
                "plr": round(res["plr"], 4),
                "disposition_ratio": round(min(res["disposition_ratio"], 99), 2),
            }
            for pid, res in strategy_results.items()
            if res["strategy"] != "market"
        },
        "validation": validation.to_dict(),
    }


def main():
    """Run disposition effect analysis."""
    parser = argparse.ArgumentParser(description="Analyze DispositionEffect simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("DispositionEffect Analysis - Prospect Theory Trading")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded trades from {len(data['trades'])} players")

    # Analyze by strategy
    print("\n[2] Calculating PGR/PLR metrics...")
    strategy_results = analyze_by_strategy(data)

    for pid, res in strategy_results.items():
        print(
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    # Generate plots
    print("\n[3] Generating plots...")
    plot_disposition_analysis(data, strategy_results, output_dir)
    print(f"    Saved to {output_dir}/disposition_analysis.png")

    # Generate summary
    print("\n[4] Generating summary...")
    summary = generate_summary(data, strategy_results)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Disposition Effect Detected: {summary['disposition_effect_detected']}")
    if summary["disposition_investor"]:
        disp = summary["disposition_investor"]
        print(f"Disposition Investor: PGR={disp['pgr']:.3f}, PLR={disp['plr']:.3f}")
        print(
            f"  -> Sells winners {disp['pgr']/disp['plr']:.1f}x more readily than losers"
            if disp["plr"] > 0
            else ""
        )
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()
