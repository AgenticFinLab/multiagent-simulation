"""DispositionEffect Analysis - Prospect Theory Trading Evaluation

Analyzes disposition effect (Shefrin & Statman 1985):
- Sell winners too early, hold losers too long
- Key metrics: PGR (Proportion of Gains Realized), PLR (Proportion of Losses Realized)
- Disposition effect present when PGR > PLR

Usage:
    python examples/DispositionEffect/Rule/analysis.py -c configs/DispositionEffect/Rule/simulation.yml

Academic References:
    - Shefrin & Statman (1985): Original disposition effect paper
    - Kahneman & Tversky (1979): Prospect theory foundation
    - Odean (1998): Empirical evidence from trading data

Output figures (saved to EXPERIMENT/DispositionEffect/analysis/):
    fig1_price_dynamics.png      - Price path, fundamental, rolling volatility
    fig2_pgr_plr_comparison.png  - PGR vs PLR grouped bars + disposition coefficient
    fig3_trading_activity.png    - Buy/sell counts and net volume per strategy
    fig4_return_distribution.png - Return histogram + normal overlay + stats
    fig5_disposition_ratio.png   - PGR/PLR ratio bars + DC magnitude per strategy
    fig6_portfolio_evolution.png - Position and cash trajectory per investor type
    fig7_sell_gain_loss.png      - Scatter of gain/loss % at each sell event
"""

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from typing import Any, Dict, List

from masim.evaluation.finance import (
    # Time Series
    calculate_max_drawdown,
    # Visualization
    save_figure,
    # Validation
    validate_disposition_effect,
)
from masim.utils import load_config, load_results


def calculate_pgr_plr(trades: List[Dict], prices: List[float]) -> Dict[str, float]:
    """
    Calculate Proportion of Gains/Losses Realized (PGR/PLR).

    PGR = Realized Gains / (Realized Gains + Paper Gains)
    PLR = Realized Losses / (Realized Losses + Paper Losses)

    Disposition Effect: PGR > PLR

    Price used: bid_price from trade record (the price the player observed
    when making the decision). Falls back to market price by round if absent.

    Reference point: fixed at initial_purchase_price for DispositionInvestor
    (move_reference=False on buys — matching players.py behavior).
    """
    realized_gains = 0
    paper_gains = 0
    realized_losses = 0
    paper_losses = 0

    # Track position and reference point
    position = 30.0  # matches initial_position in players.yml
    purchase_price = 100.0  # matches initial_purchase_price — fixed reference
    total_cost = position * purchase_price

    # Build round→market price lookup as fallback
    use_round_lookup = trades and "round" in trades[0]
    price_by_round: Dict[int, float] = {}
    if use_round_lookup and prices:
        for idx, p in enumerate(prices):
            price_by_round[idx + 1] = p

    for i, trade in enumerate(trades):
        # Prefer bid_price recorded in trade payload (price player actually observed)
        bid_price = trade.get("bid_price", 0)
        if bid_price > 0:
            current_price = bid_price
        elif use_round_lookup:
            round_num = trade.get("round", i + 1)
            current_price = price_by_round.get(
                round_num, prices[min(i, len(prices) - 1)] if prices else 0
            )
        else:
            if i >= len(prices):
                break
            current_price = prices[i]

        if current_price <= 0 or position <= 0 or purchase_price <= 0:
            continue

        quantity = trade["quantity"]
        unit_gain = current_price - purchase_price

        if quantity < 0:  # Selling — classify as realized
            realized_qty = min(abs(quantity), position)
            if unit_gain > 0:
                realized_gains += realized_qty * unit_gain
            else:
                realized_losses += realized_qty * abs(unit_gain)

            # Remaining position after this sell — paper gain/loss
            remaining = max(0.0, position - realized_qty)
            if remaining > 0:
                if unit_gain > 0:
                    paper_gains += remaining * unit_gain
                else:
                    paper_losses += remaining * abs(unit_gain)

            # Update position; cost basis reduces proportionally
            if position > 0:
                total_cost *= (position + quantity) / position
            position = max(0.0, position + quantity)

        elif quantity > 0:  # Buying
            # move_reference=False: DispositionInvestor preserves original purchase_price
            # as behavioral anchor — do NOT update purchase_price on buys.
            # This matches players.py update_reference_point(move_reference=False).
            total_cost += quantity * current_price
            position += quantity
            # purchase_price intentionally NOT updated here

        else:  # HOLD — accumulate paper gains/losses only
            if position > 0:
                if unit_gain > 0:
                    paper_gains += position * unit_gain
                else:
                    paper_losses += position * abs(unit_gain)

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


def _strategy_label(strategy: str) -> str:
    """Short display label for a strategy name."""
    labels = {
        "DispositionInvestor": "Disposition",
        "RationalInvestor": "Rational",
        "TaxAwareInvestor": "TaxAware",
        "IndexHolder": "Index",
        "InstitutionalInvestor": "Institutional",
    }
    return labels.get(strategy, strategy[:11])


def _strategy_colors() -> Dict[str, str]:
    return {
        "DispositionInvestor": "#E74C3C",
        "RationalInvestor": "#2ECC71",
        "TaxAwareInvestor": "#3498DB",
        "IndexHolder": "#95A5A6",
        "InstitutionalInvestor": "#9B59B6",
    }


def plot_fig1_price_dynamics(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 1: Price path with fundamental, rolling volatility, and return series."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
    rounds = np.arange(1, len(prices) + 1)

    # Rolling 20-round volatility (annualized as pct)
    vol_window = 20
    rolling_vol = np.array(
        [
            np.std(returns[max(0, i - vol_window) : i]) * 100
            for i in range(1, len(returns) + 1)
        ]
    )

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=False)
    fig.suptitle("Fig 1: Price Dynamics", fontsize=14, fontweight="bold")

    # Panel A: Price + fundamental
    ax = axes[0]
    ax.plot(rounds, prices, color="#2C3E50", linewidth=1.5, label="Market Price")
    ax.axhline(
        y=100.0,
        color="#BDC3C7",
        linestyle="--",
        linewidth=1.2,
        label="Fundamental (100)",
    )
    ax.fill_between(
        rounds,
        prices,
        100.0,
        where=(prices >= 100.0),
        alpha=0.12,
        color="#2ECC71",
        label="Above Fundamental",
    )
    ax.fill_between(
        rounds,
        prices,
        100.0,
        where=(prices < 100.0),
        alpha=0.12,
        color="#E74C3C",
        label="Below Fundamental",
    )
    ax.set_ylabel("Price")
    ax.set_title("A. Price Path vs Fundamental Value")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel B: Per-round returns
    ax = axes[1]
    ret_rounds = np.arange(2, len(prices) + 1)
    colors_bar = ["#E74C3C" if r < 0 else "#2ECC71" for r in returns]
    ax.bar(ret_rounds, returns * 100, color=colors_bar, alpha=0.7, width=0.8)
    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_ylabel("Return (%)")
    ax.set_title("B. Per-Round Returns")
    ax.grid(True, alpha=0.3)

    # Panel C: Rolling volatility
    ax = axes[2]
    vol_rounds = np.arange(2, len(prices) + 1)
    ax.plot(
        vol_rounds,
        rolling_vol,
        color="#E67E22",
        linewidth=1.5,
        label=f"Rolling {vol_window}-round Std (%)",
    )
    ax.fill_between(vol_rounds, rolling_vol, alpha=0.2, color="#E67E22")
    ax.set_xlabel("Round")
    ax.set_ylabel("Volatility (%)")
    ax.set_title(f"C. Rolling {vol_window}-Round Volatility")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig1_price_dynamics.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig2_pgr_plr_comparison(
    strategy_results: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Fig 2: PGR vs PLR grouped bars + disposition coefficient per strategy."""
    if not strategy_results:
        return

    colors = _strategy_colors()
    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]
    pgr_vals = [res["pgr"] for _, res in items]
    plr_vals = [res["plr"] for _, res in items]
    dc_vals = [res["pgr"] - res["plr"] for _, res in items]
    _strat_colors = [
        colors.get(res["strategy"], "#7F8C8D") for _, res in items
    ]  # reserved

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Fig 2: PGR vs PLR — Disposition Effect Measurement (Odean 1998)",
        fontsize=13,
        fontweight="bold",
    )

    # Panel A: Grouped PGR/PLR bars
    ax = axes[0]
    x = np.arange(len(labels))
    width = 0.35
    bars_pgr = ax.bar(
        x - width / 2,
        pgr_vals,
        width,
        label="PGR (Gains Realized)",
        color="#27AE60",
        alpha=0.85,
        edgecolor="white",
    )
    bars_plr = ax.bar(
        x + width / 2,
        plr_vals,
        width,
        label="PLR (Losses Realized)",
        color="#C0392B",
        alpha=0.85,
        edgecolor="white",
    )
    # Annotate values
    for bar in bars_pgr:
        h = bar.get_height()
        if h > 0.005:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.005,
                f"{h:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )
    for bar in bars_plr:
        h = bar.get_height()
        if h > 0.005:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.005,
                f"{h:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Proportion")
    ax.set_title("A. PGR vs PLR by Strategy\n(PGR > PLR = Disposition Effect)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(0, max(max(pgr_vals + plr_vals, default=0) * 1.2, 0.1))

    # Panel B: Disposition Coefficient (PGR - PLR)
    ax = axes[1]
    bar_colors = ["#E74C3C" if dc > 0 else "#3498DB" for dc in dc_vals]
    bars = ax.bar(labels, dc_vals, color=bar_colors, alpha=0.85, edgecolor="white")
    for bar, dc in zip(bars, dc_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (0.003 if dc >= 0 else -0.008),
            f"{dc:+.3f}",
            ha="center",
            va="bottom" if dc >= 0 else "top",
            fontsize=8,
        )
    ax.axhline(y=0, color="black", linewidth=1)
    ax.axhline(
        y=0.05, color="#F39C12", linestyle=":", linewidth=1, label="DC=0.05 (weak)"
    )
    ax.axhline(
        y=0.10, color="#E67E22", linestyle=":", linewidth=1, label="DC=0.10 (moderate)"
    )
    ax.axhline(
        y=0.15, color="#E74C3C", linestyle=":", linewidth=1, label="DC=0.15 (strong)"
    )
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Disposition Coefficient (PGR - PLR)")
    ax.set_title("B. Disposition Coefficient per Strategy\n(>0.10 = meaningful effect)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig2_pgr_plr_comparison.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig3_trading_activity(
    strategy_results: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Fig 3: Buy/sell event counts and total traded volume per strategy."""
    if not strategy_results:
        return

    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]
    buy_counts = [res.get("buy_count", 0) for _, res in items]
    sell_counts = [res.get("sell_count", 0) for _, res in items]
    volumes = [res.get("total_volume", 0) for _, res in items]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Fig 3: Trading Activity by Strategy", fontsize=13, fontweight="bold")

    # Panel A: Buy vs Sell event counts
    ax = axes[0]
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(
        x - width / 2,
        buy_counts,
        width,
        label="Buy Events",
        color="#2ECC71",
        alpha=0.85,
    )
    ax.bar(
        x + width / 2,
        sell_counts,
        width,
        label="Sell Events",
        color="#E74C3C",
        alpha=0.85,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Number of Events")
    ax.set_title("A. Buy vs Sell Event Counts")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel B: Total traded volume
    ax = axes[1]
    bar_colors = [
        _strategy_colors().get(res["strategy"], "#7F8C8D") for _, res in items
    ]
    ax.bar(labels, volumes, color=bar_colors, alpha=0.85, edgecolor="white")
    for i, v in enumerate(volumes):
        ax.text(
            i,
            v + max(volumes, default=0) * 0.01,
            f"{v:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Total Shares Traded")
    ax.set_title("B. Total Trading Volume")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig3_trading_activity.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig4_return_distribution(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 4: Return distribution histogram with normal overlay and stats panel."""
    prices = np.array(data["prices"])
    if len(prices) < 2:
        return

    returns = np.diff(prices) / prices[:-1] * 100  # in percent

    mean_r = np.mean(returns)
    std_r = np.std(returns)
    skew_r = float(np.mean(((returns - mean_r) / std_r) ** 3)) if std_r > 0 else 0
    kurt_r = float(np.mean(((returns - mean_r) / std_r) ** 4)) - 3 if std_r > 0 else 0

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Fig 4: Return Distribution", fontsize=13, fontweight="bold")

    # Panel A: Histogram + normal overlay
    ax = axes[0]
    ax.hist(
        returns, bins=40, density=True, color="#3498DB", alpha=0.7, edgecolor="white"
    )
    x_range = np.linspace(returns.min(), returns.max(), 200)
    normal_pdf = (1 / (std_r * np.sqrt(2 * np.pi))) * np.exp(
        -0.5 * ((x_range - mean_r) / std_r) ** 2
    )
    ax.plot(x_range, normal_pdf, "r-", linewidth=2, label="Normal fit")
    ax.axvline(x=0, color="black", linestyle="--", linewidth=1, label="Zero")
    ax.axvline(
        x=mean_r,
        color="#E67E22",
        linestyle="-",
        linewidth=1.5,
        label=f"Mean={mean_r:.3f}%",
    )
    ax.set_xlabel("Return (%)")
    ax.set_ylabel("Density")
    ax.set_title("A. Return Distribution with Normal Overlay")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel B: Statistics text panel
    ax = axes[1]
    ax.axis("off")
    stats_text = (
        "Return Statistics\n"
        "─────────────────────────\n"
        f"Total rounds:    {len(prices)}\n"
        f"Mean return:     {mean_r:+.4f}%\n"
        f"Std deviation:   {std_r:.4f}%\n"
        f"Skewness:        {skew_r:+.4f}\n"
        f"Excess kurtosis: {kurt_r:+.4f}\n"
        f"Min return:      {returns.min():+.4f}%\n"
        f"Max return:      {returns.max():+.4f}%\n"
        f"\n"
        f"Positive rounds: {(returns > 0).sum()} ({(returns > 0).mean()*100:.1f}%)\n"
        f"Negative rounds: {(returns < 0).sum()} ({(returns < 0).mean()*100:.1f}%)\n"
    )
    ax.text(
        0.05,
        0.95,
        stats_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="#ECF0F1", alpha=0.8),
    )
    ax.set_title("B. Summary Statistics")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_return_distribution.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig5_disposition_ratio(
    strategy_results: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Fig 5: PGR/PLR ratio bars + gain/loss pool breakdown per strategy."""
    if not strategy_results:
        return

    _colors_fig5 = _strategy_colors()  # reserved for per-bar coloring
    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]

    ratios = [
        min(res["disposition_ratio"], 8.0) if res["plr"] > 0 else 0 for _, res in items
    ]
    realized_g = [res.get("realized_gains", 0) for _, res in items]
    realized_l = [res.get("realized_losses", 0) for _, res in items]
    paper_g = [res.get("paper_gains", 0) for _, res in items]
    paper_l = [res.get("paper_losses", 0) for _, res in items]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "Fig 5: Disposition Ratio & Gain/Loss Pool Breakdown",
        fontsize=13,
        fontweight="bold",
    )

    # Panel A: Disposition ratio (PGR/PLR)
    ax = axes[0]
    bar_colors = [
        "#E74C3C" if r > 1 else ("#3498DB" if r < 1 else "#95A5A6") for r in ratios
    ]
    bars = ax.bar(labels, ratios, color=bar_colors, alpha=0.85, edgecolor="white")
    for bar, r in zip(bars, ratios):
        if r > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                r + 0.05,
                f"{r:.2f}x",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.axhline(
        y=1,
        color="black",
        linestyle="--",
        linewidth=1.5,
        label="PGR = PLR (no disposition)",
    )
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("PGR / PLR  (capped at 8x)")
    ax.set_title(
        "A. Disposition Ratio\n(Red >1 = disposition effect; Blue <1 = reverse)"
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel B: Stacked gain/loss pool (realized vs paper)
    ax = axes[1]
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(
        x - width / 2,
        realized_g,
        width,
        label="Realized Gains",
        color="#27AE60",
        alpha=0.9,
    )
    ax.bar(
        x - width / 2,
        paper_g,
        width,
        bottom=realized_g,
        color="#A9DFBF",
        alpha=0.7,
        label="Paper Gains",
    )
    ax.bar(
        x + width / 2,
        realized_l,
        width,
        label="Realized Losses",
        color="#C0392B",
        alpha=0.9,
    )
    ax.bar(
        x + width / 2,
        paper_l,
        width,
        bottom=realized_l,
        color="#F1948A",
        alpha=0.7,
        label="Paper Losses",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Cumulative $ Value")
    ax.set_title(
        "B. Gain/Loss Pool Breakdown\n(Realized vs Paper — drives PGR/PLR denominator)"
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig5_disposition_ratio.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig6_portfolio_evolution(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 6: Reconstruct and plot position trajectory per investor type."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    colors = _strategy_colors()
    # Build round->price lookup (available for future per-round portfolio valuation)
    _ = {i + 1: p for i, p in enumerate(prices)}
    player_positions: Dict[str, Dict[int, float]] = {}
    player_strategies: Dict[str, str] = {}

    for player_id, trades in data["trades"].items():
        if not trades:
            continue
        strategy = trades[0]["strategy"]
        player_strategies[player_id] = strategy

        position = 30.0  # initial_position
        pos_by_round: Dict[int, float] = {1: position}  # start of sim
        for trade in sorted(trades, key=lambda t: t["round"]):
            rnd = trade["round"]
            position = max(0.0, position + trade["quantity"])
            pos_by_round[rnd] = position

        # Forward-fill
        all_rounds = list(range(1, len(prices) + 1))
        last_pos = 30.0
        positions = []
        for r in all_rounds:
            if r in pos_by_round:
                last_pos = pos_by_round[r]
            positions.append(last_pos)
        player_positions[player_id] = positions

    if not player_positions:
        return

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle(
        "Fig 6: Portfolio Position Evolution by Investor Type",
        fontsize=13,
        fontweight="bold",
    )
    rounds = list(range(1, len(prices) + 1))

    # Panel A: Position size over time
    ax = axes[0]
    for player_id, positions in player_positions.items():
        strategy = player_strategies[player_id]
        color = colors.get(strategy, "#7F8C8D")
        label = f"{_strategy_label(strategy)} ({player_id.split('_')[-1]})"
        ax.plot(rounds, positions, color=color, linewidth=1.5, alpha=0.85, label=label)
    ax.axhline(
        y=30.0,
        color="black",
        linestyle=":",
        linewidth=1,
        alpha=0.5,
        label="Initial position (30)",
    )
    ax.set_ylabel("Shares Held")
    ax.set_title("A. Position Size Over Time")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Panel B: Portfolio value (position × price)
    ax = axes[1]
    for player_id, positions in player_positions.items():
        strategy = player_strategies[player_id]
        color = colors.get(strategy, "#7F8C8D")
        label = _strategy_label(strategy)
        port_values = [pos * price for pos, price in zip(positions, prices)]
        ax.plot(
            rounds, port_values, color=color, linewidth=1.5, alpha=0.85, label=label
        )
    ax.axhline(
        y=3000.0,
        color="black",
        linestyle=":",
        linewidth=1,
        alpha=0.5,
        label="Initial equity value (30 × 100)",
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Equity Value ($)")
    ax.set_title("B. Equity Value (Position × Price)")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig6_portfolio_evolution.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_fig7_sell_gain_loss(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 7: Scatter of gain/loss % at each sell event, colored by strategy.

    For each sell trade, computes the approximate gain/loss % by comparing
    bid_price at the sell round against the initial purchase price (100.0).
    This visualizes the disposition effect: sells clustered in gain territory.
    """
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    colors = _strategy_colors()
    price_by_round = {i + 1: p for i, p in enumerate(prices)}
    initial_purchase = 100.0

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Fig 7: Sell Events — Gain/Loss % at Realization",
        fontsize=13,
        fontweight="bold",
    )

    # Collect sell events per strategy type
    strategy_sell_data: Dict[str, List] = {}
    for _pid, trades in data["trades"].items():
        strategy = trades[0]["strategy"] if trades else "Unknown"
        for trade in trades:
            if trade["quantity"] < 0:
                rnd = trade["round"]
                price_at_sell = price_by_round.get(
                    rnd, trade.get("bid_price", initial_purchase)
                )
                gain_loss_pct = (
                    (price_at_sell - initial_purchase) / initial_purchase * 100
                )
                if strategy not in strategy_sell_data:
                    strategy_sell_data[strategy] = []
                strategy_sell_data[strategy].append(
                    (rnd, gain_loss_pct, abs(trade["quantity"]))
                )

    # Panel A: Scatter (round vs gain/loss % at sell)
    ax = axes[0]
    for strategy, events in strategy_sell_data.items():
        if not events:
            continue
        rnds, gls, _ = zip(*events)
        color = colors.get(strategy, "#7F8C8D")
        ax.scatter(
            rnds,
            gls,
            color=color,
            alpha=0.7,
            s=30,
            label=_strategy_label(strategy),
            edgecolors="white",
            linewidths=0.3,
        )
    ax.axhline(y=0, color="black", linewidth=1)
    ax.axhline(
        y=5,
        color="#F39C12",
        linestyle=":",
        linewidth=1,
        label="+5% gain threshold (Disposition)",
    )
    ax.axhline(
        y=-30,
        color="#C0392B",
        linestyle=":",
        linewidth=1,
        label="-30% loss threshold (Disposition)",
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Gain/Loss % at Sell (vs initial purchase price)")
    ax.set_title("A. Sell Events by Round\n(Disposition = sells clustered above +5%)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel B: Distribution of gain/loss % at sell (violin or histogram per strategy)
    ax = axes[1]
    all_gl_by_strategy = []
    strategy_names_for_violin = []
    for strategy, events in strategy_sell_data.items():
        if len(events) >= 2:
            _, gls, _ = zip(*events)
            all_gl_by_strategy.append(list(gls))
            strategy_names_for_violin.append(_strategy_label(strategy))

    if all_gl_by_strategy:
        vp = ax.violinplot(all_gl_by_strategy, showmedians=True, showmeans=False)
        for i, (body, strat) in enumerate(zip(vp["bodies"], strategy_names_for_violin)):
            strategy_key = next(
                (
                    k
                    for k, v in {s: _strategy_label(s) for s in colors}.items()
                    if v == strat
                ),
                None,
            )
            body.set_facecolor(colors.get(strategy_key, "#7F8C8D"))
            body.set_alpha(0.7)
        ax.axhline(y=0, color="black", linewidth=1)
        ax.axhline(y=5, color="#F39C12", linestyle=":", linewidth=1)
        ax.axhline(y=-30, color="#C0392B", linestyle=":", linewidth=1)
        ax.set_xticks(range(1, len(strategy_names_for_violin) + 1))
        ax.set_xticklabels(
            strategy_names_for_violin, rotation=30, ha="right", fontsize=9
        )
    else:
        ax.text(
            0.5,
            0.5,
            "Insufficient sell events\nfor distribution plot",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=11,
            color="gray",
        )

    ax.set_ylabel("Gain/Loss % at Sell")
    ax.set_title("B. Distribution of Gain/Loss % at Sell\n(Violin plot per strategy)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig7_sell_gain_loss.png")
    save_figure(fig, path)
    plt.close()
    print(f"    Saved: {path}")


def plot_disposition_analysis(
    data: Dict[str, Any],
    strategy_results: Dict[str, Dict],
    output_dir: str,
) -> None:
    """Generate all 7 disposition effect analysis figures."""
    plot_fig1_price_dynamics(data, output_dir)
    plot_fig2_pgr_plr_comparison(strategy_results, output_dir)
    plot_fig3_trading_activity(strategy_results, output_dir)
    plot_fig4_return_distribution(data, output_dir)
    plot_fig5_disposition_ratio(strategy_results, output_dir)
    plot_fig6_portfolio_evolution(data, output_dir)
    plot_fig7_sell_gain_loss(data, output_dir)


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

    # Analyze by strategy
    print("\n[2] Calculating PGR/PLR metrics...")
    strategy_results = analyze_by_strategy(data)

    for _, res in strategy_results.items():
        print(
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    # Generate plots
    print("\n[3] Generating figures (7 plots)...")
    plot_disposition_analysis(data, strategy_results, output_dir)
    print(f"    All figures saved to: {output_dir}/")

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
