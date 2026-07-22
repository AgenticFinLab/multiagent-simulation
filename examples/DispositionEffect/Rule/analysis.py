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
import shutil

from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.finance import (
    # Time Series
    calculate_max_drawdown,
    # Visualization
    save_figure,
    # Validation
    validate_disposition_effect,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary


STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_dispositioneffect_dynamics.png",
    "02_dispositioneffect_analysis.png",
    "03_summary.png",
)


def _write_standard_named_outputs(output_dir: str) -> None:
    """Create fixed-name aliases required by the standard output contract."""
    aliases = {
        "fig3_trading_activity.png": "00_investor_bids.png",
        "fig1_price_dynamics.png": "01_dispositioneffect_dynamics.png",
        "fig2_pgr_plr_comparison.png": "02_dispositioneffect_analysis.png",
        "fig5_disposition_ratio.png": "03_summary.png",
    }
    for source, target in aliases.items():
        source_path = os.path.join(output_dir, source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"missing DispositionEffect analysis figure: {source_path}")
        shutil.copyfile(source_path, os.path.join(output_dir, target))


def calculate_pgr_plr(
    trades: List[Dict[str, Any]],
    prices: List[float],
    initial_position: float,
    initial_purchase_price: float,
    move_reference_on_buy: bool,
) -> Dict[str, float]:
    """
    Calculate Proportion of Gains/Losses Realized (PGR/PLR).

    PGR = Realized Gains / (Realized Gains + Paper Gains)
    PLR = Realized Losses / (Realized Losses + Paper Losses)

    Disposition Effect: PGR > PLR

    Price used: bid_price from trade record (the price the player observed
    when making the decision). Trade payloads must include bid_price and round.

    Reference point: fixed at initial_purchase_price for DispositionInvestor
    (move_reference=False on buys — matching players.py behavior).
    """
    realized_gains = 0
    paper_gains = 0
    realized_losses = 0
    paper_losses = 0

    # Track position and reference point from the expanded player config.
    position = float(initial_position)
    purchase_price = float(initial_purchase_price)
    total_cost = position * purchase_price

    if not prices:
        raise ValueError("prices must contain at least one market price")
    if position < 0 or purchase_price <= 0:
        raise ValueError("initial position must be non-negative and purchase price positive")

    price_by_round: Dict[int, float] = {idx + 1: p for idx, p in enumerate(prices)}

    for trade in trades:
        bid_price = float(trade["bid_price"])
        round_num = int(trade["round"])
        if bid_price > 0:
            current_price = bid_price
        elif round_num in price_by_round:
            current_price = price_by_round[round_num]
        else:
            raise ValueError(f"trade round {round_num} is outside price history")

        if current_price <= 0 or position <= 0 or purchase_price <= 0:
            continue

        quantity = float(trade["quantity"])
        unit_gain = current_price - purchase_price

        if quantity < 0:  # Selling — classify as realized
            realized_qty = min(abs(quantity), position)
            if unit_gain > 0:
                realized_gains += realized_qty * unit_gain
            elif unit_gain < 0:
                realized_losses += realized_qty * abs(unit_gain)

            # Remaining position after this sell — paper gain/loss
            remaining = max(0.0, position - realized_qty)
            if remaining > 0:
                if unit_gain > 0:
                    paper_gains += remaining * unit_gain
                elif unit_gain < 0:
                    paper_losses += remaining * abs(unit_gain)

            # Update position; cost basis reduces proportionally
            if position > 0:
                total_cost *= (position + quantity) / position
            position = max(0.0, position + quantity)

        elif quantity > 0:  # Buying
            total_cost += quantity * current_price
            position += quantity
            if move_reference_on_buy:
                purchase_price = total_cost / position

        else:  # HOLD — accumulate paper gains/losses only
            if position > 0:
                if unit_gain > 0:
                    paper_gains += position * unit_gain
                elif unit_gain < 0:
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
    if not prices:
        raise ValueError("data['prices'] must contain at least one price point")
    results = {}

    for player_id, trades in data["trades"].items():
        if not trades:
            continue

        strategy = trades[0]["strategy"]

        # Calculate PGR/PLR
        player_parameters = data["player_parameters"][player_id]
        metrics = calculate_pgr_plr(
            trades,
            prices,
            player_parameters["initial_position"],
            player_parameters["initial_purchase_price"],
            strategy != "DispositionInvestor",
        )

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

    if len(prices) < 2:
        raise ValueError("at least two prices are required for price dynamics")
    returns = np.diff(prices) / prices[:-1]
    rounds = np.arange(1, len(prices) + 1)
    fundamental_value = float(data["market_parameters"]["fundamental_value"])

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
        y=fundamental_value,
        color="#BDC3C7",
        linestyle="--",
        linewidth=1.2,
        label=f"Fundamental ({fundamental_value:g})",
    )
    ax.fill_between(
        rounds,
        prices,
        fundamental_value,
        where=(prices >= fundamental_value),
        alpha=0.12,
        color="#2ECC71",
        label="Above Fundamental",
    )
    ax.fill_between(
        rounds,
        prices,
        fundamental_value,
        where=(prices < fundamental_value),
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
        raise ValueError("strategy_results must contain at least one strategy")

    colors = _strategy_colors()
    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]
    pgr_vals = [res["pgr"] for _, res in items]
    plr_vals = [res["plr"] for _, res in items]
    dc_vals = [res["pgr"] - res["plr"] for _, res in items]
    _strat_colors = [
        colors.get(res["strategy"], "#7F8C8D") for _, res in items
    ]  # matplotlib styling fallback

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
    ax.set_xticks(x, labels=labels)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right")
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
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right")
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
        raise ValueError("strategy_results must contain at least one strategy")

    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]
    buy_counts = [res["buy_count"] for _, res in items]
    sell_counts = [res["sell_count"] for _, res in items]
    volumes = [res["total_volume"] for _, res in items]

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
    ax.set_xticks(x, labels=labels)
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right")
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
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right")
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
        raise ValueError("strategy_results must contain at least one strategy")

    _colors_fig5 = _strategy_colors()  # reserved for per-bar coloring
    items = [(pid, res) for pid, res in strategy_results.items()]
    labels = [_strategy_label(res["strategy"]) for _, res in items]

    ratios = [
        min(res["disposition_ratio"], 8.0) if res["plr"] > 0 else 0 for _, res in items
    ]
    realized_g = [res["realized_gains"] for _, res in items]
    realized_l = [res["realized_losses"] for _, res in items]
    paper_g = [res["paper_gains"] for _, res in items]
    paper_l = [res["paper_losses"] for _, res in items]

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
    ax.tick_params(axis="x", labelrotation=30, labelsize=9)
    plt.setp(ax.get_xticklabels(), ha="right")
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
    strategy_positions: Dict[str, List[List[float]]] = {}

    for player_id, trades in data["trades"].items():
        if not trades:
            continue
        strategy = trades[0]["strategy"]
        initial_position = float(
            data["player_parameters"][player_id]["initial_position"]
        )
        position = initial_position
        pos_by_round: Dict[int, float] = {1: position}  # start of sim
        for trade in sorted(trades, key=lambda t: t["round"]):
            rnd = trade["round"]
            position = max(0.0, position + trade["quantity"])
            pos_by_round[rnd] = position

        # Forward-fill
        all_rounds = list(range(1, len(prices) + 1))
        last_pos = initial_position
        positions = []
        for r in all_rounds:
            if r in pos_by_round:
                last_pos = pos_by_round[r]
            positions.append(last_pos)
        strategy_positions.setdefault(strategy, []).append(positions)

    if not strategy_positions:
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
    for strategy, position_series in strategy_positions.items():
        positions = np.mean(np.asarray(position_series), axis=0)
        color = colors.get(strategy, "#7F8C8D")
        label = _strategy_label(strategy)
        ax.plot(rounds, positions, color=color, linewidth=1.5, alpha=0.85, label=label)
    ax.set_ylabel("Shares Held")
    ax.set_title("A. Position Size Over Time")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Panel B: Portfolio value (position × price)
    ax = axes[1]
    for strategy, position_series in strategy_positions.items():
        positions = np.mean(np.asarray(position_series), axis=0)
        color = colors.get(strategy, "#7F8C8D")
        label = _strategy_label(strategy)
        port_values = [pos * price for pos, price in zip(positions, prices)]
        ax.plot(
            rounds, port_values, color=color, linewidth=1.5, alpha=0.85, label=label
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

    For each sell trade, computes gain/loss against that player's configured
    initial purchase price.
    This visualizes the disposition effect: sells clustered in gain territory.
    """
    prices = np.array(data["prices"])
    if len(prices) == 0:
        return

    colors = _strategy_colors()
    price_by_round = {i + 1: p for i, p in enumerate(prices)}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "Fig 7: Sell Events — Gain/Loss % at Realization",
        fontsize=13,
        fontweight="bold",
    )

    # Collect sell events per strategy type
    strategy_sell_data: Dict[str, List] = {}
    for player_id, trades in data["trades"].items():
        if not trades:
            continue
        strategy = trades[0]["strategy"]
        initial_purchase = float(
            data["player_parameters"][player_id]["initial_purchase_price"]
        )
        for trade in trades:
            if trade["quantity"] < 0:
                rnd = trade["round"]
                price_at_sell = float(trade["bid_price"])
                if price_at_sell <= 0:
                    if rnd not in price_by_round:
                        raise ValueError(
                            f"sell trade round {rnd} is outside price history"
                        )
                    price_at_sell = price_by_round[rnd]
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
    ax.set_xlabel("Round")
    ax.set_ylabel("Gain/Loss % at Sell (vs initial purchase price)")
    ax.set_title("A. Sell Events by Round\n(Disposition = more sales in gain territory)")
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


def aggregate_strategy_results(
    strategy_results: Dict[str, Dict], strategy_keyword: str
) -> Dict[str, Any]:
    """Aggregate all matching player instances before scenario validation."""
    matches = [
        result
        for result in strategy_results.values()
        if strategy_keyword in result["strategy"].lower()
    ]
    if not matches:
        raise ValueError(f"No strategy result matches {strategy_keyword!r}")

    realized_gains = sum(result["realized_gains"] for result in matches)
    realized_losses = sum(result["realized_losses"] for result in matches)
    paper_gains = sum(result["paper_gains"] for result in matches)
    paper_losses = sum(result["paper_losses"] for result in matches)
    gain_denominator = realized_gains + paper_gains
    loss_denominator = realized_losses + paper_losses
    pgr = realized_gains / gain_denominator if gain_denominator > 0 else 0.0
    plr = realized_losses / loss_denominator if loss_denominator > 0 else 0.0

    return {
        "strategy": matches[0]["strategy"],
        "player_count": len(matches),
        "pgr": pgr,
        "plr": plr,
        "disposition_ratio": pgr / plr if plr > 0 else float("inf"),
        "disposition_effect": pgr > plr,
        "realized_gains": realized_gains,
        "realized_losses": realized_losses,
        "paper_gains": paper_gains,
        "paper_losses": paper_losses,
        "buy_count": sum(result["buy_count"] for result in matches),
        "sell_count": sum(result["sell_count"] for result in matches),
        "total_volume": sum(result["total_volume"] for result in matches),
    }


def aggregate_all_strategies(
    strategy_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Aggregate player-instance metrics into one row per exact strategy."""
    strategy_names = sorted(
        {result["strategy"] for result in strategy_results.values()}
    )
    return {
        strategy: aggregate_strategy_results(strategy_results, strategy.lower())
        for strategy in strategy_names
    }


def holding_period_asymmetry(
    trades: List[Dict[str, Any]],
    initial_position: float,
    initial_purchase_price: float,
) -> Dict[str, float]:
    """Calculate quantity-weighted loser/winner holding periods using FIFO lots."""
    lots: List[List[float]] = [
        [float(initial_position), float(initial_purchase_price), 0.0]
    ]
    winner_rounds = winner_quantity = 0.0
    loser_rounds = loser_quantity = 0.0

    for trade in sorted(trades, key=lambda item: item["round"]):
        quantity = float(trade["quantity"])
        price = float(trade["bid_price"])
        round_num = float(trade["round"])
        if quantity > 0:
            lots.append([quantity, price, round_num])
            continue
        if quantity == 0:
            continue

        remaining = abs(quantity)
        while remaining > 1e-9:
            if not lots:
                raise ValueError("sell quantity exceeds reconstructed FIFO position")
            lot_quantity, lot_price, opened_round = lots[0]
            realized = min(remaining, lot_quantity)
            held_rounds = round_num - opened_round
            if held_rounds < 0:
                raise ValueError("trade rounds must be non-decreasing")
            if price > lot_price:
                winner_rounds += held_rounds * realized
                winner_quantity += realized
            elif price < lot_price:
                loser_rounds += held_rounds * realized
                loser_quantity += realized
            lot_quantity -= realized
            remaining -= realized
            if lot_quantity <= 1e-12:
                lots.pop(0)
            else:
                lots[0][0] = lot_quantity

    avg_winner = winner_rounds / winner_quantity if winner_quantity else 0.0
    avg_loser = loser_rounds / loser_quantity if loser_quantity else 0.0
    hpa = avg_loser / avg_winner if avg_winner > 0 else 0.0
    return {
        "avg_winner_holding_rounds": avg_winner,
        "avg_loser_holding_rounds": avg_loser,
        "holding_period_asymmetry": hpa,
    }


def terminal_wealth(
    trades: List[Dict[str, Any]],
    final_price: float,
    initial_cash: float,
    initial_position: float,
) -> float:
    """Reconstruct terminal mark-to-market wealth from signed orders."""
    cash = float(initial_cash)
    position = float(initial_position)
    for trade in trades:
        quantity = float(trade["quantity"])
        price = float(trade["bid_price"])
        if quantity != 0 and price <= 0:
            raise ValueError("non-zero trades must have a positive bid price")
        cash -= quantity * price
        position += quantity
    if position < -1e-9:
        raise ValueError("reconstructed terminal position cannot be negative")
    return cash + position * float(final_price)


def calculate_extended_metrics(
    data: Dict[str, Any], strategy_results: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate HPA, PDI, and TRI exactly as defined in analysis-bases.md."""
    holding_periods: Dict[str, Dict[str, float]] = {}
    wealth: Dict[str, float] = {}
    wealth_by_strategy: Dict[str, List[float]] = {}

    for player_id, trades in data["trades"].items():
        parameters = data["player_parameters"][player_id]
        holding_periods[player_id] = holding_period_asymmetry(
            trades,
            parameters["initial_position"],
            parameters["initial_purchase_price"],
        )
        wealth[player_id] = terminal_wealth(
            trades,
            data["prices"][-1],
            parameters["initial_cash"],
            parameters["initial_position"],
        )
        strategy = strategy_results[player_id]["strategy"]
        wealth_by_strategy.setdefault(strategy, []).append(wealth[player_id])

    disposition_wealth = [
        value
        for strategy, values in wealth_by_strategy.items()
        if "disposition" in strategy.lower()
        for value in values
    ]
    rational_wealth = [
        value
        for strategy, values in wealth_by_strategy.items()
        if "rational" in strategy.lower()
        for value in values
    ]
    if not disposition_wealth or not rational_wealth:
        raise ValueError(
            "Disposition and rational investor wealth are required"
        )
    mean_disposition = float(np.mean(disposition_wealth))
    mean_rational = float(np.mean(rational_wealth))
    if mean_rational == 0:
        raise ValueError("mean RationalInvestor wealth must be non-zero")
    pdi = (mean_rational - mean_disposition) / mean_rational

    disposition_result = aggregate_strategy_results(
        strategy_results, "disposition"
    )
    tax_result = aggregate_strategy_results(strategy_results, "tax")
    disposition_plr = float(disposition_result["plr"])
    tri = float(tax_result["plr"]) / disposition_plr if disposition_plr > 0 else 0.0
    return {
        "holding_periods": holding_periods,
        "terminal_wealth": wealth,
        "mean_disposition_wealth": mean_disposition,
        "mean_rational_wealth": mean_rational,
        "performance_drag_index": pdi,
        "tax_reversal_index": tri,
    }


def generate_summary(
    data: Dict[str, Any],
    strategy_results: Dict[str, Dict],
) -> Dict[str, Any]:
    """Generate summary statistics with validation."""
    prices = np.array(data["prices"])
    if len(prices) == 0:
        raise ValueError("data['prices'] must contain at least one price point")
    if len(prices) < 2:
        raise ValueError("data['prices'] must contain at least two price points")

    returns = np.diff(prices) / prices[:-1]
    prices_list = list(prices)
    max_dd, peak_idx, trough_idx = calculate_max_drawdown(prices_list)

    # Validate on all instances of each archetype, not whichever dictionary
    # entry happened to be encountered last.
    disp_result = aggregate_strategy_results(strategy_results, "disposition")
    rational_result = aggregate_strategy_results(strategy_results, "rational")

    # Extract PGR and PLR for validation
    pgr = disp_result["pgr"]
    plr = disp_result["plr"]
    disposition_coefficient = pgr - plr

    # Run validation
    validation = validate_disposition_effect(
        pgr=pgr,
        plr=plr,
        disposition_coefficient=disposition_coefficient,
    )

    extended_metrics = calculate_extended_metrics(data, strategy_results)

    return {
        "scenario": "DispositionEffect",
        "total_rounds": len(prices),
        "price_statistics": {
            "initial_price": float(prices[0]),
            "final_price": float(prices[-1]),
            "max_price": float(np.max(prices)),
            "min_price": float(np.min(prices)),
            "volatility": float(np.std(returns) * 100),
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
        "disposition_investor": disp_result,
        "rational_investor": rational_result,
        "disposition_effect_detected": disp_result["disposition_effect"],
        "extended_metrics": extended_metrics,
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


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load price and trade payloads from a completed DispositionEffect run."""
    results = load_results(config)
    coordinators = list(results.players_by_role("coordinator").values())
    if not coordinators:
        raise ValueError("No coordinator result found")

    prices = list(coordinators[0].batch("price").all())
    if not prices:
        raise ValueError("Coordinator price series is empty")

    trades = {}
    player_parameters: Dict[str, Dict[str, float]] = {}
    for pid, player in results.players_by_role("player").items():
        payloads_by_round = player.turns.payloads()
        if payloads_by_round:
            trades[pid] = [
                {**payload, "round": round_num}
                for round_num, payload in sorted(payloads_by_round.items())
            ]
            extras = config["players"][pid]["config"]["extras"]
            player_parameters[pid] = {
                "initial_cash": float(extras["initial_cash"]),
                "initial_position": float(extras["initial_position"]),
                "initial_purchase_price": float(extras["initial_purchase_price"]),
            }

    if not trades:
        raise ValueError("No player trade payloads found")

    market_id = coordinators[0].player_id
    market_extras = config["players"][market_id]["config"]["extras"]
    return {
        "prices": prices,
        "trades": trades,
        "player_parameters": player_parameters,
        "market_parameters": {
            "fundamental_value": float(market_extras["fundamental_value"]),
        },
    }


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate strategy-level metrics and summary validation."""
    strategy_results = analyze_by_strategy(data)
    summary = generate_summary(data, strategy_results)
    return {"strategy_results": strategy_results, "summary": summary}


def create_visualizations(data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str) -> None:
    """Create DispositionEffect analysis figures."""
    aggregated = aggregate_all_strategies(metrics["strategy_results"])
    plot_disposition_analysis(data, aggregated, output_dir)


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

    print("\n[1] Loading simulation data...")
    data = load_simulation_data(config)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded trades from {len(data['trades'])} players")

    print("\n[2] Calculating PGR/PLR metrics...")
    metrics = calculate_metrics(data)
    strategy_results = metrics["strategy_results"]

    for res in aggregate_all_strategies(strategy_results).values():
        print(
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    print("\n[3] Generating figures (7 plots)...")
    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)
    print(f"    All figures saved to: {output_dir}/")

    print("\n[4] Generating summary...")
    summary = metrics["summary"]

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
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rule'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='DispositionEffect',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "calculate_pgr_plr",
    "analyze_by_strategy",
    "aggregate_strategy_results",
    "aggregate_all_strategies",
    "holding_period_asymmetry",
    "terminal_wealth",
    "calculate_extended_metrics",
    "plot_disposition_analysis",
    "generate_summary",
    "main",
]
