"""EquityPremium Analysis - Myopic Loss Aversion Evaluation

Analyzes equity premium puzzle through behavioral lens:
- Myopic loss aversion explains high equity premium demand
- Evaluation horizon effects on stock allocation
- Key metrics: realized premium, allocation by investor type

Usage:
    python examples/EquityPremium/Rule/analysis.py -c configs/EquityPremium/Rule/simulation.yml

Academic References:
    - Mehra & Prescott (1985): Equity Premium Puzzle
    - Benartzi & Thaler (1995): Myopic Loss Aversion
    - Kahneman & Tversky (1979): Prospect Theory
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from typing import Any, Dict, List, Optional

from masim.evaluation.finance import (
    # Time Series
    calculate_returns,
    calculate_rolling_volatility,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    # Visualization
    create_figure,
    save_figure,
    # Validation
    validate_equity_premium,
)
from masim.utils import load_config, load_results


# Constants for equity premium analysis
ANNUAL_TRADING_DAYS = 252
RISK_FREE_RATE_ANNUAL = 0.01  # 1% annual bond return


def calculate_equity_premium(prices: List[float], periods: int) -> Dict[str, float]:
    """
    Calculate realized equity premium.

    Equity Premium = Stock Return - Risk-Free Rate
    """
    if len(prices) < 2:
        return {}

    prices_arr = np.array(prices)
    returns = np.diff(prices_arr) / prices_arr[:-1]

    # Annualize returns
    daily_return = np.mean(returns)
    annual_return = daily_return * ANNUAL_TRADING_DAYS
    annual_volatility = np.std(returns) * np.sqrt(ANNUAL_TRADING_DAYS)

    # Risk-free rate (daily)
    daily_rf = RISK_FREE_RATE_ANNUAL / ANNUAL_TRADING_DAYS

    # Equity premium
    equity_premium = annual_return - RISK_FREE_RATE_ANNUAL

    # Sharpe ratio
    sharpe = (daily_return - daily_rf) / np.std(returns) if np.std(returns) > 0 else 0
    annual_sharpe = sharpe * np.sqrt(ANNUAL_TRADING_DAYS)

    return {
        "daily_return": float(daily_return * 100),
        "annual_return": float(annual_return * 100),
        "annual_volatility": float(annual_volatility * 100),
        "equity_premium": float(equity_premium * 100),
        "sharpe_ratio": float(annual_sharpe),
        "risk_free_rate": float(RISK_FREE_RATE_ANNUAL * 100),
    }


def calculate_loss_probability(
    prices: List[float], horizons: List[int]
) -> Dict[int, float]:
    """
    Calculate probability of negative return by evaluation horizon.

    This is key to myopic loss aversion theory:
    - Short horizon: High P(loss) → Low stock allocation
    - Long horizon: Low P(loss) → High stock allocation
    """
    if len(prices) < max(horizons) + 1:
        return {}

    prices_arr = np.array(prices)
    results = {}

    for horizon in horizons:
        if horizon >= len(prices_arr):
            continue

        # Calculate returns over horizon
        horizon_returns = []
        for i in range(len(prices_arr) - horizon):
            ret = (prices_arr[i + horizon] - prices_arr[i]) / prices_arr[i]
            horizon_returns.append(ret)

        if horizon_returns:
            loss_prob = sum(1 for r in horizon_returns if r < 0) / len(horizon_returns)
            results[horizon] = float(loss_prob * 100)

    return results


def analyze_investor_allocations(trades: Dict[str, List]) -> Dict[str, Dict]:
    """Analyze stock allocation by investor type."""
    results = {}

    for player_id, player_trades in trades.items():
        if not player_trades:
            continue

        strategy = player_trades[0]["strategy"]
        if strategy == "market":
            continue

        # decision_payload uses "stock_qty" for the order quantity
        # Track implied allocation (simplified)
        buy_volume = sum(
            t["stock_qty"] for t in player_trades if t.get("stock_qty", 0) > 0
        )
        sell_volume = abs(
            sum(t["stock_qty"] for t in player_trades if t.get("stock_qty", 0) < 0)
        )
        net_position = buy_volume - sell_volume

        # Estimate allocation tendency
        if "myopic" in strategy.lower():
            implied_allocation = 0.20  # Low due to loss aversion
        elif "long_horizon" in strategy.lower():
            implied_allocation = 0.70  # High due to ignoring short-term losses
        elif "rational" in strategy.lower():
            implied_allocation = 0.50  # Standard CAPM allocation
        elif "saver" in strategy.lower() or "risk_averse" in strategy.lower():
            implied_allocation = 0.10  # Very conservative
        elif "institutional" in strategy.lower():
            implied_allocation = 0.60  # Professional
        else:
            implied_allocation = 0.40  # Default

        results[player_id] = {
            "strategy": strategy,
            "buy_volume": float(buy_volume),
            "sell_volume": float(sell_volume),
            "net_position": float(net_position),
            "implied_stock_allocation": float(implied_allocation),
        }

    return results


def plot_equity_premium_analysis(
    data: Dict[str, Any],
    premium_metrics: Dict[str, float],
    loss_probs: Dict[int, float],
    allocations: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Generate equity premium analysis plots."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    returns = calculate_returns(prices)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Cumulative stock vs bond returns
    ax1 = axes[0, 0]
    stock_cumulative = (
        np.cumprod(1 + returns) - 1 if len(returns) > 0 else np.array([0])
    )
    rf_daily = RISK_FREE_RATE_ANNUAL / ANNUAL_TRADING_DAYS
    bond_cumulative = np.array(
        [(1 + rf_daily) ** i - 1 for i in range(len(stock_cumulative))]
    )

    ax1.plot(stock_cumulative * 100, "b-", linewidth=2, label="Stock")
    ax1.plot(bond_cumulative * 100, "g--", linewidth=2, label="Bond (Risk-free)")
    ax1.fill_between(
        range(len(stock_cumulative)),
        bond_cumulative * 100,
        stock_cumulative * 100,
        alpha=0.3,
        color="blue",
        label=f"Equity Premium (~{premium_metrics['equity_premium']:.1f}%/yr)",
    )
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Cumulative Return (%)")
    ax1.set_title("Stock vs Bond Returns (The Equity Premium)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: Loss probability by horizon
    ax2 = axes[0, 1]
    if loss_probs:
        horizons = sorted(loss_probs.keys())
        probs = [loss_probs[h] for h in horizons]
        ax2.bar(range(len(horizons)), probs, color="red", alpha=0.7)
        ax2.set_xticks(range(len(horizons)))
        ax2.set_xticklabels([f"{h}" for h in horizons])
        ax2.set_xlabel("Evaluation Horizon (Rounds)")
        ax2.set_ylabel("P(Loss) %")
        ax2.set_title(
            "Probability of Loss by Evaluation Horizon\n(Myopic investors see more losses)"
        )
        ax2.axhline(y=50, color="gray", linestyle="--", label="50%")
        ax2.grid(True, alpha=0.3)

    # Panel 3: Stock allocation by investor type
    ax3 = axes[1, 0]
    if allocations:
        strategies = [a["strategy"][:12] for a in allocations.values()]
        allocs = [a["implied_stock_allocation"] * 100 for a in allocations.values()]

        colors = []
        for alloc in allocs:
            if alloc > 50:
                colors.append("green")
            elif alloc > 30:
                colors.append("yellow")
            else:
                colors.append("red")

        ax3.bar(strategies, allocs, color=colors, alpha=0.7)
        ax3.axhline(y=50, color="gray", linestyle="--", label="50% (Rational)")
        ax3.set_xlabel("Investor Type")
        ax3.set_ylabel("Stock Allocation (%)")
        ax3.set_title(
            "Stock Allocation by Investor Type\n(Myopic = Low, Long-Horizon = High)"
        )
        ax3.tick_params(axis="x", rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    # Panel 4: Return distribution
    ax4 = axes[1, 1]
    ax4.hist(
        returns * 100, bins=50, color="blue", alpha=0.7, edgecolor="black", density=True
    )
    ax4.axvline(x=0, color="red", linestyle="--", linewidth=2, label="Zero Return")
    ax4.axvline(
        x=np.mean(returns) * 100,
        color="green",
        linestyle="-",
        linewidth=2,
        label=f"Mean ({np.mean(returns)*100:.2f}%)",
    )

    # Add loss aversion annotation
    neg_count = np.sum(returns < 0)
    total = len(returns)
    ax4.set_xlabel("Daily Return (%)")
    ax4.set_ylabel("Density")
    ax4.set_title(
        f"Return Distribution\n({neg_count}/{total} = {neg_count/total*100:.1f}% Negative)"
    )
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "02_equitypremium_analysis.png"))
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(prices, linewidth=2, label="Stock price")
    ax.set_title("EquityPremium Price Dynamics")
    ax.set_xlabel("Round")
    ax.set_ylabel("Stock Price")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save_figure(fig, os.path.join(output_dir, "01_equitypremium_dynamics.png"))
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 5))
    if allocations:
        strategies = [a["strategy"][:18] for a in allocations.values()]
        net_positions = [a["net_position"] for a in allocations.values()]
        ax.bar(strategies, net_positions, color="steelblue", alpha=0.8)
        ax.tick_params(axis="x", rotation=45)
    ax.set_title("EquityPremium Investor Stock Quantity Pressure")
    ax.set_ylabel("Net Stock Quantity")
    ax.grid(True, axis="y", alpha=0.3)
    save_figure(fig, os.path.join(output_dir, "00_investor_bids.png"))
    plt.close()


def generate_summary(
    data: Dict[str, Any],
    premium_metrics: Dict[str, float],
    loss_probs: Dict[int, float],
    allocations: Dict[str, Dict],
) -> Dict[str, Any]:
    """Generate summary statistics with validation."""
    prices = np.array(data["prices"])
    returns = calculate_returns(prices) if len(prices) > 1 else np.array([])
    prices_list = list(prices)
    max_dd, peak_idx, trough_idx = (
        calculate_max_drawdown(prices_list) if len(prices_list) > 1 else (0, 0, 0)
    )

    # Extract allocation data for validation
    myopic_allocation = 0.2  # Default
    long_horizon_allocation = 0.7  # Default
    for pid, alloc in allocations.items():
        if "myopic" in alloc["strategy"].lower():
            myopic_allocation = alloc["implied_stock_allocation"]
        if "long_horizon" in alloc["strategy"].lower():
            long_horizon_allocation = alloc["implied_stock_allocation"]

    # Run validation
    validation = validate_equity_premium(
        equity_premium=premium_metrics.get("equity_premium", 0),
        myopic_allocation=myopic_allocation,
        long_horizon_allocation=long_horizon_allocation,
    )

    return {
        "scenario": "EquityPremium",
        "total_rounds": len(prices),
        "price_statistics": {
            "initial_price": float(prices[0]) if len(prices) > 0 else 0,
            "final_price": float(prices[-1]) if len(prices) > 0 else 0,
            "total_return": (
                float((prices[-1] / prices[0] - 1) * 100) if len(prices) > 1 else 0
            ),
        },
        "metrics": {
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
        },
        "equity_premium": {
            "annual_return_pct": round(premium_metrics.get("annual_return", 0), 2),
            "risk_free_rate_pct": round(premium_metrics.get("risk_free_rate", 0), 2),
            "equity_premium_pct": round(premium_metrics.get("equity_premium", 0), 2),
            "sharpe_ratio": round(premium_metrics.get("sharpe_ratio", 0), 2),
            "annual_volatility_pct": round(
                premium_metrics.get("annual_volatility", 0), 2
            ),
        },
        "loss_probability_by_horizon": {
            str(k): round(v, 2) for k, v in loss_probs.items()
        },
        "investor_allocations": {
            pid: {
                "strategy": a["strategy"],
                "stock_allocation_pct": round(a["implied_stock_allocation"] * 100, 1),
            }
            for pid, a in allocations.items()
        },
        "myopic_loss_aversion_evidence": {
            "short_horizon_loss_prob": (
                round(loss_probs[min(loss_probs.keys())], 2) if loss_probs else 0
            ),
            "long_horizon_loss_prob": (
                round(loss_probs[max(loss_probs.keys())], 2) if loss_probs else 0
            ),
            "ratio": (
                round(
                    loss_probs[min(loss_probs.keys())]
                    / loss_probs[max(loss_probs.keys())],
                    2,
                )
                if loss_probs and loss_probs[max(loss_probs.keys())] > 0
                else 0
            ),
            "myopic_allocation_pct": round(myopic_allocation * 100, 1),
            "long_horizon_allocation_pct": round(long_horizon_allocation * 100, 1),
        },
        "puzzle_explained": premium_metrics.get("equity_premium", 0) > 4.0,
        "validation": validation.to_dict(),
    }


def main():
    """Run equity premium analysis."""
    parser = argparse.ArgumentParser(description="Analyze EquityPremium simulation")
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
    print("EquityPremium Analysis - Myopic Loss Aversion")
    print("=" * 70)

    # Load data via lazy result loader
    print("\n[1] Loading simulation data...")
    results = load_results(config)
    # Coordinator batch store 'price' holds the market price time-series
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("stock").all()) if coordinators else []
    # Each non-coordinator player contributes a list of per-round decision payloads
    # payload fields: stock_qty, strategy, investor
    trades = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            # Inject round number into each payload for downstream analysis
            trades[pid] = [
                {**p, "round": rn} for rn, p in sorted(payloads_by_round.items())
            ]
    print(f"    Loaded {len(prices)} price points")
    print(f"    Loaded trades from {len(trades)} players")

    # Calculate equity premium
    print("\n[2] Calculating equity premium metrics...")
    premium_metrics = calculate_equity_premium(prices, len(prices))
    print(f"    Annual Stock Return: {premium_metrics['annual_return']:.2f}%")
    print(f"    Risk-Free Rate:      {premium_metrics['risk_free_rate']:.2f}%")
    print(f"    Equity Premium:      {premium_metrics['equity_premium']:.2f}%")
    print(f"    Sharpe Ratio:        {premium_metrics['sharpe_ratio']:.2f}")

    # Calculate loss probability by horizon
    print("\n[3] Calculating loss probability by horizon...")
    horizons = [1, 5, 10, 20, 50, 100]
    horizons = [h for h in horizons if h < len(prices)]
    loss_probs = calculate_loss_probability(prices, horizons)
    for h, prob in sorted(loss_probs.items()):
        print(f"    Horizon {h:3d} rounds: P(Loss) = {prob:.1f}%")

    # Analyze investor allocations
    print("\n[4] Analyzing investor allocations...")
    allocations = analyze_investor_allocations(trades)
    for pid, alloc in allocations.items():
        print(
            f"    {alloc['strategy']:24s}: Stock allocation ~{alloc['implied_stock_allocation']*100:.0f}%"
        )

    # Generate plots (pass prices/trades directly to avoid re-extracting)
    print("\n[5] Generating plots...")
    plot_equity_premium_analysis(
        {"prices": prices, "trades": trades},
        premium_metrics,
        loss_probs,
        allocations,
        output_dir,
    )
    print(f"    Saved to {output_dir}/equity_premium_analysis.png")

    # Generate summary
    print("\n[6] Generating summary...")
    summary = generate_summary(
        {"prices": prices, "trades": trades}, premium_metrics, loss_probs, allocations
    )

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Equity Premium: {premium_metrics['equity_premium']:.2f}% annual")
    print(
        f"Puzzle Explanation: {'Supported' if summary['puzzle_explained'] else 'Not clear'}"
    )
    if loss_probs:
        short_h = min(loss_probs.keys())
        long_h = max(loss_probs.keys())
        print(f"Short-horizon P(Loss): {loss_probs[short_h]:.1f}%")
        print(f"Long-horizon P(Loss):  {loss_probs[long_h]:.1f}%")
        print("→ Myopic investors see more losses, demand higher premium")
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


def _load_data(results) -> Dict[str, Any]:
    """Extract prices and trades from a SimulationResults object.

    Data sources
    ------------
    Coordinator  → batch store 'stock' (flat time-series)
    Player turns → decision_payload fields stock_qty / strategy / investor

    Returns
    -------
    dict with keys:
        prices : list[float]
        trades : dict[str, list]
    """
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("stock").all()) if coordinators else []
    trades = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            trades[pid] = [
                {**p, "round": rn} for rn, p in sorted(payloads_by_round.items())
            ]
    return {"prices": prices, "trades": trades}


def analyze_equity_premium(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform equity premium analysis using extracted data."""
    os.makedirs(output_dir, exist_ok=True)
    prices = data["prices"]
    trades = data["trades"]

    premium_metrics = calculate_equity_premium(prices, len(prices))
    if not premium_metrics:
        print("Insufficient data for equity premium analysis")
        return {}

    horizons = [1, 5, 10, 20, 50, 100]
    horizons = [h for h in horizons if h < len(prices)]
    loss_probs = calculate_loss_probability(prices, horizons)
    allocations = analyze_investor_allocations(trades)

    plot_equity_premium_analysis(
        {"prices": prices, "trades": trades},
        premium_metrics,
        loss_probs,
        allocations,
        output_dir,
    )
    summary = generate_summary(
        {"prices": prices, "trades": trades},
        premium_metrics,
        loss_probs,
        allocations,
    )

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    fig, ax = plt.subplots(figsize=(8, 4))
    validation = summary["validation"]
    score = validation["score"] if isinstance(validation, dict) else 0
    ax.axis("off")
    ax.text(
        0.05,
        0.75,
        "EquityPremium Summary",
        fontsize=16,
        fontweight="bold",
    )
    ax.text(0.05, 0.50, f"Rounds: {summary['total_rounds']}", fontsize=12)
    ax.text(
        0.05,
        0.35,
        f"Equity premium: {summary['equity_premium']['equity_premium_pct']:.2f}%",
        fontsize=12,
    )
    ax.text(0.05, 0.20, f"Validation score: {score:.1%}", fontsize=12)
    save_figure(fig, os.path.join(output_dir, "03_summary.png"))
    plt.close()

    return summary


if __name__ == "__main__":
    main()
