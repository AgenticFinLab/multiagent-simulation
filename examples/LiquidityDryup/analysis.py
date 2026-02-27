"""LiquidityDryup Analysis - Market Maker Inventory Model Evaluation

Analyzes liquidity dry-up dynamics:
- Market maker inventory pressure and withdrawal
- Illiquidity spiral: less liquidity → more impact → more withdrawal
- Key metrics: bid-ask spread, price impact, liquidity provision

Usage:
    python examples/LiquidityDryup/analysis.py -c configs/LiquidityDryup/simulation.yml

Academic References:
    - Grossman & Miller (1988): Market Maker Model
    - Amihud & Mendelson (1986): Liquidity Premium
    - Brunnermeier & Pedersen (2009): Illiquidity Spiral
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
    calculate_max_drawdown,
    calculate_liquidity_metrics,
    # Visualization
    create_figure,
    save_figure,
)
from masim.utils import load_config


def load_simulation_data(record_dir: str) -> Dict[str, Any]:
    """Load simulation data from record directory."""
    data = {"prices": [], "trades": defaultdict(list), "volumes": []}

    # Load price history
    price_dir = os.path.join(record_dir, "market", "price")
    if os.path.exists(price_dir):
        for f in sorted(glob.glob(os.path.join(price_dir, "*.json"))):
            with open(f, encoding="utf-8") as fp:
                batch = json.load(fp)
                data["prices"].extend(batch)

    # Load turn data from all players
    turns_pattern = os.path.join(record_dir, "*", "turns", "*.json")
    for f in sorted(glob.glob(turns_pattern)):
        with open(f, encoding="utf-8") as fp:
            try:
                turn_data = json.load(fp)
                player_id = f.split(os.sep)[-3]
                if "strategy" in turn_data:
                    data["trades"][player_id].append(turn_data)
            except (json.JSONDecodeError, KeyError):
                continue

    return data


def calculate_liquidity_states(
    prices: List[float], trades: Dict[str, List]
) -> List[Dict]:
    """
    Calculate liquidity state for each round.

    Liquidity = Base + MM_Provided
    States: Normal (>100), Reduced (50-100), Dry-up (<50), Crisis (<20)
    """
    if len(prices) < 2:
        return []

    prices_arr = np.array(prices)
    returns = np.diff(prices_arr) / prices_arr[:-1]

    # Calculate rolling volatility
    window = 10
    rolling_vol = np.zeros(len(returns))
    for i in range(len(returns)):
        start = max(0, i - window + 1)
        rolling_vol[i] = np.std(returns[start : i + 1]) * 100 if i > 0 else 0

    states = []
    for i, vol in enumerate(rolling_vol):
        # Simulate MM behavior based on volatility
        if vol < 1.5:
            mm_liquidity = 50  # Full provision
            state = "NORMAL"
        elif vol < 2.5:
            mm_liquidity = 25  # Reduced
            state = "REDUCED"
        elif vol < 3.5:
            mm_liquidity = 10  # Minimal
            state = "DRY_UP"
        else:
            mm_liquidity = 0  # Withdrawn
            state = "CRISIS"

        base_liquidity = 50
        total_liquidity = base_liquidity + mm_liquidity

        # Calculate implied price impact
        impact_factor = 100 / total_liquidity if total_liquidity > 0 else 10

        states.append(
            {
                "round": i,
                "volatility": float(vol),
                "mm_liquidity": float(mm_liquidity),
                "total_liquidity": float(total_liquidity),
                "impact_factor": float(impact_factor),
                "state": state,
            }
        )

    return states


def calculate_amihud_illiquidity(prices: List[float], volumes: List[float]) -> float:
    """
    Calculate Amihud (2002) illiquidity measure.

    ILLIQ = (1/N) × Σ |r_t| / volume_t

    Higher ILLIQ = less liquid market
    """
    if len(prices) < 2:
        return 0.0

    prices_arr = np.array(prices)
    returns = np.abs(np.diff(prices_arr) / prices_arr[:-1])

    if len(volumes) == 0 or len(volumes) != len(returns):
        # Use uniform volume if not provided
        volumes = np.ones(len(returns)) * 100

    volumes_arr = np.array(volumes[: len(returns)])
    volumes_arr[volumes_arr == 0] = 1  # Avoid division by zero

    illiq = np.mean(returns / volumes_arr)
    return float(illiq)


def identify_dryup_episodes(states: List[Dict]) -> List[Dict]:
    """Identify liquidity dry-up episodes."""
    episodes = []
    in_dryup = False
    episode_start = 0

    for i, state in enumerate(states):
        if state["state"] in ["DRY_UP", "CRISIS"] and not in_dryup:
            in_dryup = True
            episode_start = i
        elif state["state"] in ["NORMAL", "REDUCED"] and in_dryup:
            in_dryup = False
            episodes.append(
                {
                    "start": episode_start,
                    "end": i - 1,
                    "duration": i - episode_start,
                    "min_liquidity": min(
                        s["total_liquidity"] for s in states[episode_start:i]
                    ),
                    "max_impact": max(
                        s["impact_factor"] for s in states[episode_start:i]
                    ),
                }
            )

    # Handle ongoing episode
    if in_dryup:
        episodes.append(
            {
                "start": episode_start,
                "end": len(states) - 1,
                "duration": len(states) - episode_start,
                "min_liquidity": min(
                    s["total_liquidity"] for s in states[episode_start:]
                ),
                "max_impact": max(s["impact_factor"] for s in states[episode_start:]),
            }
        )

    return episodes


def plot_liquidity_analysis(
    data: Dict[str, Any],
    liquidity_states: List[Dict],
    episodes: List[Dict],
    output_dir: str,
) -> None:
    """Generate liquidity analysis plots."""
    prices = np.array(data["prices"])
    if len(prices) == 0 or len(liquidity_states) == 0:
        return

    returns = calculate_returns(prices)
    volatility = [s["volatility"] for s in liquidity_states]
    liquidity = [s["total_liquidity"] for s in liquidity_states]
    impact = [s["impact_factor"] for s in liquidity_states]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Price with liquidity states
    ax1 = axes[0, 0]
    ax1.plot(prices, "b-", linewidth=1.5, label="Price")

    # Color background by liquidity state
    state_colors = {
        "NORMAL": "green",
        "REDUCED": "yellow",
        "DRY_UP": "orange",
        "CRISIS": "red",
    }
    prev_state = None
    start_idx = 0
    for i, state in enumerate(liquidity_states):
        if state["state"] != prev_state:
            if prev_state is not None:
                ax1.axvspan(start_idx, i, alpha=0.2, color=state_colors[prev_state])
            prev_state = state["state"]
            start_idx = i
    if prev_state is not None:
        ax1.axvspan(
            start_idx,
            len(liquidity_states),
            alpha=0.2,
            color=state_colors[prev_state],
        )

    ax1.set_xlabel("Round")
    ax1.set_ylabel("Price")
    ax1.set_title("Price Dynamics with Liquidity States")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Panel 2: Liquidity provision
    ax2 = axes[0, 1]
    ax2.plot(liquidity, "g-", linewidth=2, label="Total Liquidity")
    ax2.axhline(y=100, color="green", linestyle="--", alpha=0.5, label="Normal Level")
    ax2.axhline(y=50, color="orange", linestyle="--", alpha=0.5, label="Reduced Level")
    ax2.axhline(y=20, color="red", linestyle="--", alpha=0.5, label="Crisis Level")
    ax2.fill_between(range(len(liquidity)), 0, liquidity, alpha=0.3, color="green")

    # Mark dry-up episodes
    for ep in episodes:
        ax2.axvspan(ep["start"], ep["end"], alpha=0.3, color="red")

    ax2.set_xlabel("Round")
    ax2.set_ylabel("Liquidity")
    ax2.set_title("Market Liquidity (Red = Dry-up Episodes)")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Panel 3: Price impact factor
    ax3 = axes[1, 0]
    ax3.plot(impact, "r-", linewidth=1.5)
    ax3.fill_between(range(len(impact)), 1, impact, alpha=0.3, color="red")
    ax3.axhline(y=1, color="gray", linestyle="--", label="Normal Impact")
    ax3.set_xlabel("Round")
    ax3.set_ylabel("Impact Factor (x)")
    ax3.set_title("Price Impact Multiplier\n(Higher = Orders move price more)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Panel 4: Volatility
    ax4 = axes[1, 1]
    ax4.plot(volatility, "purple", linewidth=1.5, label="Rolling Volatility (%)")
    ax4.axhline(y=2.0, color="orange", linestyle="--", label="MM Reduce Threshold")
    ax4.axhline(y=3.0, color="red", linestyle="--", label="MM Withdraw Threshold")
    ax4.fill_between(range(len(volatility)), 0, volatility, alpha=0.3, color="purple")
    ax4.set_xlabel("Round")
    ax4.set_ylabel("Volatility (%)")
    ax4.set_title("Volatility (Triggers MM Withdrawal)")
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "liquidity_analysis.png"))
    plt.close()


def generate_summary(
    data: Dict[str, Any],
    liquidity_states: List[Dict],
    episodes: List[Dict],
) -> Dict[str, Any]:
    """Generate summary statistics."""
    prices = np.array(data["prices"])
    returns = calculate_returns(prices) if len(prices) > 1 else np.array([])

    # Count state occurrences
    state_counts = defaultdict(int)
    for state in liquidity_states:
        state_counts[state["state"]] += 1

    total_rounds = len(liquidity_states)

    return {
        "price_statistics": {
            "initial_price": float(prices[0]) if len(prices) > 0 else 0,
            "final_price": float(prices[-1]) if len(prices) > 0 else 0,
            "max_price": float(np.max(prices)) if len(prices) > 0 else 0,
            "min_price": float(np.min(prices)) if len(prices) > 0 else 0,
            "volatility": float(np.std(returns) * 100) if len(returns) > 0 else 0,
        },
        "liquidity_statistics": {
            "avg_liquidity": (
                float(np.mean([s["total_liquidity"] for s in liquidity_states]))
                if liquidity_states
                else 0
            ),
            "min_liquidity": (
                float(min(s["total_liquidity"] for s in liquidity_states))
                if liquidity_states
                else 0
            ),
            "max_impact": (
                float(max(s["impact_factor"] for s in liquidity_states))
                if liquidity_states
                else 0
            ),
        },
        "state_distribution": {
            state: {
                "count": count,
                "percentage": (
                    round(count / total_rounds * 100, 1) if total_rounds > 0 else 0
                ),
            }
            for state, count in state_counts.items()
        },
        "dryup_episodes": {
            "count": len(episodes),
            "total_duration": sum(ep["duration"] for ep in episodes),
            "worst_episode": (
                max(episodes, key=lambda x: x["duration"]) if episodes else None
            ),
        },
        "dryup_detected": len(episodes) > 0,
        "dryup_severity": (
            "SEVERE"
            if any(ep["min_liquidity"] < 20 for ep in episodes)
            else (
                "MODERATE"
                if len(episodes) > 2
                else "MILD" if len(episodes) > 0 else "NONE"
            )
        ),
    }


def main():
    """Run liquidity dry-up analysis."""
    parser = argparse.ArgumentParser(description="Analyze LiquidityDryup simulation")
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
    print("LiquidityDryup Analysis - Market Maker Inventory Model")
    print("=" * 70)

    # Load data
    print("\n[1] Loading simulation data...")
    data = load_simulation_data(record_dir)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded trades from {len(data['trades'])} players")

    # Calculate liquidity states
    print("\n[2] Calculating liquidity states...")
    liquidity_states = calculate_liquidity_states(data["prices"], data["trades"])

    state_summary = defaultdict(int)
    for s in liquidity_states:
        state_summary[s["state"]] += 1
    for state, count in state_summary.items():
        pct = count / len(liquidity_states) * 100 if liquidity_states else 0
        print(f"    {state:10s}: {count:4d} rounds ({pct:.1f}%)")

    # Identify dry-up episodes
    print("\n[3] Identifying dry-up episodes...")
    episodes = identify_dryup_episodes(liquidity_states)
    print(f"    Found {len(episodes)} dry-up episodes")
    for i, ep in enumerate(episodes):
        print(
            f"    Episode {i + 1}: Rounds {ep['start']}-{ep['end']} "
            f"(duration: {ep['duration']}, min liquidity: {ep['min_liquidity']:.0f})"
        )

    # Generate plots
    print("\n[4] Generating plots...")
    plot_liquidity_analysis(data, liquidity_states, episodes, output_dir)
    print(f"    Saved to {output_dir}/liquidity_analysis.png")

    # Generate summary
    print("\n[5] Generating summary...")
    summary = generate_summary(data, liquidity_states, episodes)

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Dry-up Detected: {summary['dryup_detected']}")
    print(f"Severity: {summary['dryup_severity']}")
    print(f"Episodes: {summary['dryup_episodes']['count']}")
    print(
        f"Total Duration in Dry-up: {summary['dryup_episodes']['total_duration']} rounds"
    )

    return summary


if __name__ == "__main__":
    main()
