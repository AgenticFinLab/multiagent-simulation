"""ShortSqueeze Analysis - Supply-Demand Imbalance Evaluation

Analyzes short squeeze dynamics:
- Short interest tracking and forced covering
- Positive feedback: covering → price rise → more covering
- Key metrics: squeeze ratio, short cover volume, days to cover

Usage:
    python examples/ShortSqueeze/Rule/analysis.py -c configs/ShortSqueeze/Rule/simulation.yml

Academic References:
    - GameStop Congressional Hearing Testimony (2021)
    - Porsche-VW Short Squeeze Case Study (2008)
    - SEC Report on GameStop Trading (2021)
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
    calculate_max_drawdown,
    # Visualization
    create_figure,
    save_figure,
    # Validation
    validate_short_squeeze,
)
from masim.utils import load_config, load_results


def calculate_squeeze_metrics(
    prices: List[float], trades: Dict[str, List]
) -> Dict[str, Any]:
    """
    Calculate short squeeze metrics.

    Key metrics:
    - Squeeze ratio: (Peak Price - Entry Price) / Entry Price
    - Short cover volume: Volume from forced covering
    - Days to cover: Shares short / Daily volume
    """
    if len(prices) < 10:
        return {}

    prices_arr = np.array(prices)
    entry_price = prices_arr[0]
    peak_price = np.max(prices_arr)
    peak_idx = np.argmax(prices_arr)
    final_price = prices_arr[-1]

    # Find short seller trades
    short_cover_volume = 0
    total_volume = 0
    short_positions = []

    for player_id, player_trades in trades.items():
        for trade in player_trades:
            strategy = trade["strategy"]
            qty = trade["quantity"]
            total_volume += abs(qty)

            if "short" in strategy.lower():
                if qty > 0:  # Short covering (buying to close)
                    short_cover_volume += qty

    # Calculate metrics
    squeeze_ratio = (peak_price - entry_price) / entry_price if entry_price > 0 else 0
    recovery_ratio = (
        (peak_price - final_price) / (peak_price - entry_price)
        if (peak_price - entry_price) > 0
        else 0
    )

    # Identify squeeze phases
    returns = np.diff(prices_arr) / prices_arr[:-1]
    cumulative_returns = np.cumsum(returns)

    # Find trigger point (sustained upward move)
    trigger_idx = 0
    for i in range(len(cumulative_returns)):
        if cumulative_returns[i] > 0.1:  # 10% cumulative gain
            trigger_idx = i
            break

    return {
        "entry_price": float(entry_price),
        "peak_price": float(peak_price),
        "peak_round": int(peak_idx),
        "final_price": float(final_price),
        "squeeze_ratio": float(squeeze_ratio),
        "squeeze_percentage": float(squeeze_ratio * 100),
        "recovery_ratio": float(recovery_ratio),
        "short_cover_volume": float(short_cover_volume),
        "total_volume": float(total_volume),
        "cover_ratio": (
            float(short_cover_volume / total_volume) if total_volume > 0 else 0
        ),
        "trigger_round": int(trigger_idx),
    }


def identify_squeeze_phases(prices: List[float]) -> Dict[str, Dict]:
    """Identify squeeze phases: setup, trigger, squeeze, peak, aftermath."""
    if len(prices) < 20:
        return {}

    prices_arr = np.array(prices)
    n = len(prices_arr)

    # Find key price levels
    peak_idx = int(np.argmax(prices_arr))
    peak_price = float(prices_arr[peak_idx])
    entry_price = float(prices_arr[0])

    # Define phase boundaries
    phases = {}

    # Setup: Initial stable period
    setup_end = min(int(n * 0.15), peak_idx - 1)
    phases["setup"] = {
        "start": 0,
        "end": setup_end,
        "avg_price": float(np.mean(prices_arr[: setup_end + 1])),
        "description": "Pre-squeeze stable period",
    }

    # Trigger: Start of sustained rise
    trigger_end = min(int(n * 0.3), peak_idx - 1)
    phases["trigger"] = {
        "start": setup_end + 1,
        "end": trigger_end,
        "price_change": float(
            (prices_arr[trigger_end] - prices_arr[setup_end])
            / prices_arr[setup_end]
            * 100
        ),
        "description": "Initial buying pressure",
    }

    # Squeeze: Rapid price increase
    phases["squeeze"] = {
        "start": trigger_end + 1,
        "end": peak_idx,
        "price_change": float(
            (peak_price - prices_arr[trigger_end]) / prices_arr[trigger_end] * 100
        ),
        "description": "Forced covering accelerates",
    }

    # Aftermath: Post-peak
    if peak_idx < n - 1:
        phases["aftermath"] = {
            "start": peak_idx + 1,
            "end": n - 1,
            "price_change": float((prices_arr[-1] - peak_price) / peak_price * 100),
            "description": "Price settles after covering",
        }

    return phases


def plot_squeeze_analysis(
    data: Dict[str, Any],
    squeeze_metrics: Dict[str, Any],
    phases: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Generate short squeeze analysis plots."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    # Calculate returns directly from prices array
    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
    volatility = calculate_rolling_volatility(prices, window=10)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Price dynamics with squeeze phases
    ax1 = axes[0, 0]
    ax1.plot(prices, "b-", linewidth=2, label="Price")

    # Mark phases with colored backgrounds
    colors = {
        "setup": "gray",
        "trigger": "yellow",
        "squeeze": "red",
        "aftermath": "green",
    }
    for phase_name, phase_data in phases.items():
        ax1.axvspan(
            phase_data["start"],
            phase_data["end"],
            alpha=0.2,
            color=colors[phase_name],
            label=f"{phase_name.title()}",
        )

    # Mark peak
    peak_idx = squeeze_metrics["peak_round"]
    ax1.axvline(
        x=peak_idx,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Peak @ R{peak_idx}",
    )
    ax1.scatter(
        [peak_idx], [squeeze_metrics["peak_price"]], color="red", s=100, zorder=5
    )

    ax1.set_xlabel("Round")
    ax1.set_ylabel("Price")
    ax1.set_title(
        f"Short Squeeze Dynamics (Squeeze: +{squeeze_metrics['squeeze_percentage']:.1f}%)"
    )
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel 2: Cumulative returns
    ax2 = axes[0, 1]
    cumulative = np.cumprod(1 + returns) - 1 if len(returns) > 0 else np.array([0])
    ax2.plot(cumulative * 100, "g-", linewidth=2)
    ax2.axhline(y=0, color="black", linestyle="-", linewidth=1)
    ax2.axhline(
        y=squeeze_metrics["squeeze_percentage"],
        color="red",
        linestyle="--",
        label="Peak Gain",
    )
    ax2.fill_between(
        range(len(cumulative)), 0, cumulative * 100, alpha=0.3, color="green"
    )
    ax2.set_xlabel("Round")
    ax2.set_ylabel("Cumulative Return (%)")
    ax2.set_title("Cumulative Returns (Short Sellers' Pain)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Panel 3: Volume analysis
    ax3 = axes[1, 0]
    volumes = []
    for player_id, player_trades in data["trades"].items():
        for trade in player_trades:
            volumes.append(abs(trade["quantity"]))

    if volumes:
        # Group by rounds (approximate)
        n_rounds = len(prices)
        vol_per_round = np.zeros(n_rounds)
        trades_per_round = n_rounds // len(volumes) if len(volumes) > 0 else 1
        for i, v in enumerate(volumes):
            idx = min(i * trades_per_round, n_rounds - 1)
            vol_per_round[idx] += v

        ax3.bar(range(len(vol_per_round)), vol_per_round, alpha=0.7, color="blue")
        ax3.set_xlabel("Round")
        ax3.set_ylabel("Volume")
        ax3.set_title("Trading Volume (Spikes = Forced Covering)")
        ax3.grid(True, alpha=0.3)

    # Panel 4: Volatility
    ax4 = axes[1, 1]
    if len(volatility) > 0:
        ax4.plot(volatility * 100, "purple", linewidth=1.5)
        ax4.fill_between(
            range(len(volatility)), 0, volatility * 100, alpha=0.3, color="purple"
        )
    ax4.set_xlabel("Round")
    ax4.set_ylabel("Rolling Volatility (%)")
    ax4.set_title("Volatility During Squeeze")
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "squeeze_analysis.png"))
    plt.close()


def generate_summary(
    data: Dict[str, Any],
    squeeze_metrics: Dict[str, Any],
    phases: Dict[str, Dict],
) -> Dict[str, Any]:
    """Generate summary statistics with validation."""
    prices = np.array(data["prices"])
    # Calculate returns directly from prices array
    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
    prices_list = list(prices)
    max_dd, peak_idx, trough_idx = (
        calculate_max_drawdown(prices_list) if len(prices_list) > 1 else (0, 0, 0)
    )

    # Detect feedback loop (price acceleration during squeeze phase)
    short_covering_detected = squeeze_metrics.get("cover_ratio", 0) > 0.2
    feedback_detected = (
        squeeze_metrics.get("squeeze_ratio", 0) > 0.5 and short_covering_detected
    )

    # Run validation
    validation = validate_short_squeeze(
        max_price_spike=squeeze_metrics.get("squeeze_percentage", 0),
        short_covering_detected=short_covering_detected,
        feedback_loop_detected=feedback_detected,
    )

    return {
        "scenario": "ShortSqueeze",
        "total_rounds": len(prices),
        "squeeze_metrics": squeeze_metrics,
        "phases": phases,
        "price_statistics": {
            "initial_price": float(prices[0]) if len(prices) > 0 else 0,
            "final_price": float(prices[-1]) if len(prices) > 0 else 0,
            "peak_price": float(np.max(prices)) if len(prices) > 0 else 0,
            "min_price": float(np.min(prices)) if len(prices) > 0 else 0,
            "total_return": (
                float((prices[-1] / prices[0] - 1) * 100) if len(prices) > 1 else 0
            ),
            "volatility": float(np.std(returns) * 100) if len(returns) > 0 else 0,
        },
        "metrics": {
            "max_drawdown": round(max_dd, 4),
            "peak_round": peak_idx,
            "trough_round": trough_idx,
        },
        "squeeze_detected": squeeze_metrics.get("squeeze_ratio", 0) > 0.5,
        "squeeze_intensity": (
            "EXTREME"
            if squeeze_metrics.get("squeeze_ratio", 0) > 2.0
            else (
                "STRONG"
                if squeeze_metrics.get("squeeze_ratio", 0) > 1.0
                else (
                    "MODERATE"
                    if squeeze_metrics.get("squeeze_ratio", 0) > 0.5
                    else "WEAK"
                )
            )
        ),
        "short_covering_detected": short_covering_detected,
        "feedback_loop_detected": feedback_detected,
        "validation": validation.to_dict(),
    }


def main():
    """Run short squeeze analysis."""
    parser = argparse.ArgumentParser(description="Analyze ShortSqueeze simulation")
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
    print("ShortSqueeze Analysis - Supply-Demand Imbalance")
    print("=" * 70)

    # Load data via lazy result loader
    print("\n[1] Loading simulation data...")
    results = load_results(config)
    # Coordinator batch store 'price' holds the market price time-series
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("price").all()) if coordinators else []
    # Each non-coordinator player contributes per-round decision payloads
    # payload fields: bid_price, quantity, strategy, investor
    trades = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            # Inject round number into each payload for downstream analysis
            trades[pid] = [
                {**p, "round": rn} for rn, p in sorted(payloads_by_round.items())
            ]
    data = {"prices": prices, "trades": trades}
    print(f"    Loaded {len(prices)} price points")
    print(f"    Loaded trades from {len(trades)} players")

    # Calculate squeeze metrics
    print("\n[2] Calculating squeeze metrics...")
    squeeze_metrics = calculate_squeeze_metrics(data["prices"], data["trades"])
    print(f"    Entry Price: ${squeeze_metrics['entry_price']:.2f}")
    print(
        f"    Peak Price:  ${squeeze_metrics['peak_price']:.2f} (Round {squeeze_metrics['peak_round']})"
    )
    print(f"    Squeeze:     +{squeeze_metrics['squeeze_percentage']:.1f}%")

    # Identify phases
    print("\n[3] Identifying squeeze phases...")
    phases = identify_squeeze_phases(data["prices"])
    for phase_name, phase_data in phases.items():
        print(
            f"    {phase_name.title():12s}: Rounds {phase_data['start']}-{phase_data['end']}"
        )

    # Generate plots
    print("\n[4] Generating plots...")
    plot_squeeze_analysis(data, squeeze_metrics, phases, output_dir)
    print(f"    Saved to {output_dir}/squeeze_analysis.png")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, squeeze_metrics, phases)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Squeeze Detected: {summary['squeeze_detected']}")
    print(f"Squeeze Intensity: {summary['squeeze_intensity']}")
    print(f"Max Squeeze: +{squeeze_metrics['squeeze_percentage']:.1f}%")
    print(f"Short Covering: {'Yes' if summary['short_covering_detected'] else 'No'}")
    print(f"Feedback Loop: {'Yes' if summary['feedback_loop_detected'] else 'No'}")
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


def _load_data(results) -> Dict[str, Any]:
    """Extract prices and trades from a SimulationResults object.

    Data sources
    ------------
    Coordinator  → batch store 'price' (flat time-series)
    Player turns → decision_payload fields bid_price / quantity / strategy / investor

    Returns
    -------
    dict with keys:
        prices : list[float]
        trades : dict[str, list]
    """
    coordinators = list(results.players_by_role("coordinator").values())
    prices = list(coordinators[0].batch("price").all()) if coordinators else []
    trades = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            trades[pid] = [
                {**p, "round": rn} for rn, p in sorted(payloads_by_round.items())
            ]
    return {"prices": prices, "trades": trades}


def analyze_short_squeeze(data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """Perform short squeeze analysis using extracted data."""
    os.makedirs(output_dir, exist_ok=True)
    prices = data["prices"]
    trades = data["trades"]

    squeeze_metrics = calculate_squeeze_metrics(prices, trades)
    if not squeeze_metrics:
        print("Insufficient data for squeeze analysis")
        return {}

    phases = identify_squeeze_phases(prices)
    plot_squeeze_analysis(data, squeeze_metrics, phases, output_dir)
    summary = generate_summary(data, squeeze_metrics, phases)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    main()
