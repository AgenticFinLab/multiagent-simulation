#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Analysis

Implements analysis-bases.md for the Rule variant.
Computes all 8 metrics defined in analysis-bases.md §2, generates
the 6 required visualizations, and writes summary.json for cross-variant comparison.

Usage:
    python examples/AnchoringEffect/Rule/analysis.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config


def _load_price_records(record_path: str) -> Tuple[List[float], List[float]]:
    """Load price and fundamental time series from market records.

    Args:
        record_path: Base experiment record directory path.

    Returns:
        Tuple of (prices, fundamentals) as float lists, sorted by round.
    """
    market_price_path = os.path.join(record_path, "market", "price")
    prices = []
    fundamentals = []

    if not os.path.exists(market_price_path):
        return prices, fundamentals

    for filename in sorted(os.listdir(market_price_path)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(market_price_path, filename)
        with open(filepath, "r", encoding="utf-8") as fh:
            record = json.load(fh)
        prices.append(record["price"])
        fundamentals.append(record["fundamental"])

    return prices, fundamentals


def _load_agent_records(record_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load per-agent decision records for all investor types.

    Args:
        record_path: Base experiment record directory path.

    Returns:
        Dict mapping agent_id to list of decision records sorted by round.
    """
    agent_records: Dict[str, List[Dict[str, Any]]] = {}

    if not os.path.exists(record_path):
        return agent_records

    for agent_dir in os.listdir(record_path):
        agent_path = os.path.join(record_path, agent_dir)
        if not os.path.isdir(agent_path) or agent_dir == "market":
            continue

        records = []
        for filename in sorted(os.listdir(agent_path)):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(agent_path, filename)
            with open(filepath, "r", encoding="utf-8") as fh:
                records.append(json.load(fh))

        if records:
            agent_records[agent_dir] = records

    return agent_records


def calculate_price_deviation(
    prices: List[float], fundamentals: List[float]
) -> Dict[str, float]:
    """Compute price deviation metrics — analysis-bases.md §2 Metric: Price Deviation.

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.

    Returns:
        Dict with keys: max_deviation_pct, final_deviation_pct, mean_deviation_pct.
    """
    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)

    deviation = (price_arr - fund_arr) / fund_arr

    return {
        "max_deviation_pct": float(np.max(np.abs(deviation)) * 100),
        "final_deviation_pct": float(deviation[-1] * 100),
        "mean_deviation_pct": float(np.mean(deviation) * 100),
    }


def calculate_mean_abs_deviation(
    prices: List[float], fundamentals: List[float]
) -> float:
    """Compute Mean Absolute Deviation (MAD) — analysis-bases.md §2 Metric: MAD.

    Formula: MAD = mean(|P(t) - F| / F)

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.

    Returns:
        MAD as a decimal fraction (not percentage).
    """
    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)

    return float(np.mean(np.abs(price_arr - fund_arr) / fund_arr))


def calculate_anchoring_persistence(
    prices: List[float], fundamentals: List[float]
) -> Dict[str, float]:
    """Estimate anchoring persistence (deviation half-life) — analysis-bases.md §2.

    Computes the number of rounds for |deviation| to decay to half its initial value.
    Uses exponential fit: |dev(t)| ~ |dev(0)| * exp(-t / half_life).

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.

    Returns:
        Dict with keys: half_life_rounds, initial_deviation_pct, final_deviation_pct.
    """
    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)

    abs_deviation = np.abs((price_arr - fund_arr) / fund_arr)
    initial_dev = float(abs_deviation[0]) if len(abs_deviation) > 0 else 0.0
    half_target = initial_dev / 2.0

    half_life = float(len(prices))
    for idx, dev in enumerate(abs_deviation):
        if dev <= half_target:
            half_life = float(idx)
            break

    return {
        "half_life_rounds": half_life,
        "initial_deviation_pct": initial_dev * 100,
        "final_deviation_pct": (
            float(abs_deviation[-1]) * 100 if len(abs_deviation) > 0 else 0.0
        ),
    }


def calculate_rolling_volatility(
    prices: List[float], window: int = 10
) -> Dict[str, float]:
    """Compute rolling volatility of returns — analysis-bases.md §2 Metric: Rolling Volatility.

    Args:
        prices: Market price time series.
        window: Rolling window size in rounds.

    Returns:
        Dict with keys: mean_rolling_vol_pct, max_rolling_vol_pct, final_rolling_vol_pct.
    """
    price_arr = np.array(prices)

    if len(price_arr) < 2:
        return {
            "mean_rolling_vol_pct": 0.0,
            "max_rolling_vol_pct": 0.0,
            "final_rolling_vol_pct": 0.0,
        }

    returns = np.diff(price_arr) / price_arr[:-1]
    rolling_vols = []

    for i in range(window - 1, len(returns)):
        window_returns = returns[i - window + 1 : i + 1]
        rolling_vols.append(float(np.std(window_returns)))

    if not rolling_vols:
        return {
            "mean_rolling_vol_pct": 0.0,
            "max_rolling_vol_pct": 0.0,
            "final_rolling_vol_pct": 0.0,
        }

    return {
        "mean_rolling_vol_pct": float(np.mean(rolling_vols) * 100),
        "max_rolling_vol_pct": float(np.max(rolling_vols) * 100),
        "final_rolling_vol_pct": float(rolling_vols[-1] * 100),
    }


def calculate_autocorrelation(prices: List[float], lag: int = 1) -> float:
    """Compute return autocorrelation — analysis-bases.md §2 Metric: Return Autocorrelation.

    Args:
        prices: Market price time series.
        lag: Lag order for autocorrelation (default: 1).

    Returns:
        Autocorrelation coefficient at specified lag.
    """
    price_arr = np.array(prices)

    if len(price_arr) < lag + 2:
        return 0.0

    returns = np.diff(price_arr) / price_arr[:-1]
    n = len(returns)

    if n <= lag:
        return 0.0

    returns_mean = np.mean(returns)
    returns_centered = returns - returns_mean
    autocov = np.mean(returns_centered[: n - lag] * returns_centered[lag:])
    variance = np.var(returns_centered)

    if variance < 1e-12:
        return 0.0

    return float(autocov / variance)


def calculate_max_drawdown(prices: List[float]) -> Dict[str, float]:
    """Compute maximum peak-to-trough drawdown — analysis-bases.md §2 Metric: Max Drawdown.

    Args:
        prices: Market price time series.

    Returns:
        Dict with keys: max_drawdown_pct, peak_price, trough_price.
    """
    price_arr = np.array(prices)

    if len(price_arr) < 2:
        return {"max_drawdown_pct": 0.0, "peak_price": 0.0, "trough_price": 0.0}

    peak = price_arr[0]
    max_drawdown = 0.0
    peak_price = price_arr[0]
    trough_price = price_arr[0]

    for price in price_arr:
        if price > peak:
            peak = price

        drawdown = (peak - price) / peak if peak > 0 else 0.0
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            peak_price = peak
            trough_price = price

    return {
        "max_drawdown_pct": float(max_drawdown * 100),
        "peak_price": float(peak_price),
        "trough_price": float(trough_price),
    }


def calculate_agent_volumes(
    agent_records: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, float]]:
    """Compute per-agent-type trading volume — analysis-bases.md §2 Metric: Agent-Type Volume.

    Args:
        agent_records: Dict mapping agent_id to list of decision records.

    Returns:
        Dict mapping agent_id to volume stats (total_buy, total_sell, total_volume).
    """
    volumes: Dict[str, Dict[str, float]] = {}

    for agent_id, records in agent_records.items():
        total_buy = 0.0
        total_sell = 0.0

        for record in records:
            action = record.get("action", "hold")
            quantity = float(record.get("quantity", 0.0))

            if action == "buy":
                total_buy += quantity
            elif action == "sell":
                total_sell += quantity

        volumes[agent_id] = {
            "total_buy": total_buy,
            "total_sell": total_sell,
            "total_volume": total_buy + total_sell,
        }

    return volumes


def calculate_anchoring_bias_magnitude(
    prices: List[float],
    fundamentals: List[float],
    adjustment_factor: float,
) -> float:
    """Compute anchoring bias magnitude — analysis-bases.md §2 Metric: Anchoring Bias Magnitude.

    Measures the gap between anchored perceived target and true fundamental,
    relative to true fundamental. Based on AnchoredTrader formula from
    simulation-bases.md §4.

    Formula: bias = |anchor + (F - anchor) * alpha - F| / F
           = |F - anchor| * (1 - alpha) / F
    Uses first price as anchor_price (simulation-bases.md §4 AnchoredTrader).

    Args:
        prices: Market price time series (prices[0] = anchor_price).
        fundamentals: Fundamental value time series.
        adjustment_factor: Alpha parameter from config (default 0.3).

    Returns:
        Mean anchoring bias magnitude as decimal fraction.
    """
    if not prices or not fundamentals:
        return 0.0

    anchor_price = prices[0]
    fund_arr = np.array(fundamentals)

    perceived_targets = anchor_price + (fund_arr - anchor_price) * adjustment_factor
    bias_magnitudes = np.abs(perceived_targets - fund_arr) / fund_arr

    return float(np.mean(bias_magnitudes))


def create_visualizations(
    prices: List[float],
    fundamentals: List[float],
    agent_records: Dict[str, List[Dict[str, Any]]],
    output_path: str,
) -> None:
    """Generate all analysis visualizations — analysis-bases.md §7 Visualization Catalogue.

    Produces 6 plots:
        1. Price vs. Fundamental (with deviation overlay)
        2. Anchoring Persistence (deviation decay)
        3. Rolling Volatility
        4. Return Distribution with autocorrelation annotation
        5. Agent-Type Trading Volume
        6. Anchoring Bias Magnitude over time

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.
        agent_records: Per-agent decision records.
        output_path: Directory to write PNG files.
    """
    if not prices:
        return

    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)
    rounds = np.arange(len(prices))
    deviation = (price_arr - fund_arr) / fund_arr * 100

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "AnchoringEffect Rule Variant — Analysis", fontsize=14, fontweight="bold"
    )

    # Plot 1: Price vs. Fundamental
    axes[0, 0].plot(rounds, price_arr, label="Market Price", color="steelblue")
    axes[0, 0].plot(
        rounds, fund_arr, label="Fundamental Value", color="darkgreen", linestyle="--"
    )
    axes[0, 0].set_title("Price vs. Fundamental")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Price Deviation (%) — primary anchoring signal
    axes[0, 1].plot(rounds, deviation, color="crimson")
    axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0, 1].axhline(
        y=3, color="orange", linestyle=":", alpha=0.7, label="3% threshold"
    )
    axes[0, 1].axhline(y=-3, color="orange", linestyle=":", alpha=0.7)
    axes[0, 1].set_title("Price Deviation from Fundamental (%)")
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Deviation (%)")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Rolling Volatility
    if len(prices) > 11:
        returns = np.diff(price_arr) / price_arr[:-1] * 100
        rolling_vols = [
            np.std(returns[max(0, i - 9) : i + 1]) for i in range(len(returns))
        ]
        axes[0, 2].plot(rounds[1:], rolling_vols, color="purple")
        axes[0, 2].set_title("Rolling Volatility (10-round window, %)")
        axes[0, 2].set_xlabel("Round")
        axes[0, 2].set_ylabel("Std Dev of Returns (%)")
        axes[0, 2].grid(True, alpha=0.3)

    # Plot 4: Return Distribution
    if len(prices) > 1:
        returns = np.diff(price_arr) / price_arr[:-1] * 100
        axes[1, 0].hist(
            returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1, 0].set_title("Return Distribution (%)")
        axes[1, 0].set_xlabel("Return (%)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].grid(True, alpha=0.3)

    # Plot 5: Agent-Type Trading Volume
    if agent_records:
        agent_ids = list(agent_records.keys())
        buy_vols = []
        sell_vols = []
        for agent_id in agent_ids:
            total_buy = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "buy"
            )
            total_sell = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "sell"
            )
            buy_vols.append(total_buy)
            sell_vols.append(total_sell)

        x_pos = np.arange(len(agent_ids))
        axes[1, 1].bar(
            x_pos - 0.2, buy_vols, 0.4, label="Buy", color="green", alpha=0.7
        )
        axes[1, 1].bar(
            x_pos + 0.2, sell_vols, 0.4, label="Sell", color="red", alpha=0.7
        )
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1, 1].set_title("Agent-Type Trading Volume")
        axes[1, 1].set_ylabel("Total Quantity")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

    # Plot 6: Absolute Deviation over time (persistence visualization)
    abs_deviation = np.abs(deviation)
    axes[1, 2].plot(rounds, abs_deviation, color="darkorange", label="|Deviation|")
    if len(abs_deviation) > 0:
        half_target = abs_deviation[0] / 2.0
        axes[1, 2].axhline(
            y=half_target,
            color="grey",
            linestyle=":",
            alpha=0.7,
            label="Half-life target",
        )
    axes[1, 2].set_title("Anchoring Persistence (|Deviation| Decay)")
    axes[1, 2].set_xlabel("Round")
    axes[1, 2].set_ylabel("|Deviation| (%)")
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_path, "anchoringeffect_rule_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    """Run full AnchoringEffect Rule analysis pipeline.

    Loads simulation records, computes all 8 metrics from analysis-bases.md §2,
    generates 6 visualizations, and writes summary.json for cross-variant comparison.
    """
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect Rule simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AnchoringEffect/Rule/simulation.yml",
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_path = config["setting"]["record_path"]

    prices, fundamentals = _load_price_records(record_path)

    if not prices:
        print("No simulation data found. Run simulation first.")
        return

    agent_records = _load_agent_records(record_path)

    adjustment_factor = config.get("extras", {}).get("adjustment_factor", 0.3)

    # Compute all 8 metrics from analysis-bases.md §2
    price_deviation = calculate_price_deviation(prices, fundamentals)
    mad = calculate_mean_abs_deviation(prices, fundamentals)
    persistence = calculate_anchoring_persistence(prices, fundamentals)
    rolling_vol = calculate_rolling_volatility(prices)
    autocorr = calculate_autocorrelation(prices)
    max_drawdown = calculate_max_drawdown(prices)
    agent_volumes = calculate_agent_volumes(agent_records)
    bias_magnitude = calculate_anchoring_bias_magnitude(
        prices, fundamentals, adjustment_factor
    )

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations(prices, fundamentals, agent_records, analysis_path)

    summary = {
        "variant": "Rule",
        "simulation": "AnchoringEffect",
        "rounds": len(prices),
        "metrics": {
            "price_deviation": price_deviation,
            "mean_absolute_deviation_pct": float(mad * 100),
            "anchoring_persistence": persistence,
            "rolling_volatility": rolling_vol,
            "return_autocorrelation_lag1": autocorr,
            "max_drawdown": max_drawdown,
            "agent_volumes": agent_volumes,
            "anchoring_bias_magnitude": float(bias_magnitude),
        },
    }

    summary_path = os.path.join(analysis_path, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    agent_volumes_path = os.path.join(analysis_path, "agent_volumes.json")
    with open(agent_volumes_path, "w", encoding="utf-8") as fh:
        json.dump(agent_volumes, fh, indent=2)

    print(f"Analysis complete. Results written to: {analysis_path}")
    print(f"MAD: {mad * 100:.2f}%")
    print(f"Half-life: {persistence['half_life_rounds']:.0f} rounds")
    print(f"Max drawdown: {max_drawdown['max_drawdown_pct']:.2f}%")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}")


if __name__ == "__main__":
    main()
