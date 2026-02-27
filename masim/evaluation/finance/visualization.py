"""
Financial Visualization Module

Professional, comprehensive visualization functions for financial simulation analysis.
All functions assume data is provided directly as input parameters.

Design Principles:
    1. Functions take data directly (no file loading)
    2. Consistent API: (data, output_path, **kwargs)
    3. Publication-quality output with sensible defaults
    4. Support for both display and file saving

Chart Categories:
    - Price Dynamics: Price series, fundamentals, investor bids
    - Returns Analysis: Returns, ACF, GARCH signature
    - Volatility Analysis: Volatility series, regime detection
    - Herding Analysis: CV, directional agreement, cascade
    - Agent Analysis: Strategy impact, contribution
    - Comprehensive: Multi-panel summaries
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict
import numpy as np

# Use Agg backend for server environments
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

# =============================================================================
# Constants and Style Configuration
# =============================================================================

# Color palettes
COLORS = {
    "price": "#1f77b4",  # Blue
    "fundamental": "#7f7f7f",  # Gray
    "return": "#2ca02c",  # Green
    "volatility": "#d62728",  # Red
    "volume": "#9467bd",  # Purple
    "positive": "#2ca02c",  # Green
    "negative": "#d62728",  # Red
}

# Line styles for cycling
LINE_STYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "<", ">", "p", "h", "*"]


# =============================================================================
# Utility Functions
# =============================================================================


def get_style_generator(n_series: int) -> List[Tuple]:
    """
    Generate distinct styles for multiple data series.

    Args:
        n_series: Number of distinct series

    Returns:
        List of (color, linestyle, marker) tuples
    """
    if n_series <= 10:
        cmap = plt.colormaps["tab10"]
    elif n_series <= 20:
        cmap = plt.colormaps["tab20"]
    else:
        cmap = plt.colormaps["hsv"]

    styles = []
    for i in range(n_series):
        color = cmap(i / max(n_series, 1))
        linestyle = LINE_STYLES[i % len(LINE_STYLES)]
        marker = MARKERS[i % len(MARKERS)]
        styles.append((color, linestyle, marker))

    return styles


def create_figure(
    nrows: int = 1,
    ncols: int = 1,
    figsize: Optional[Tuple[float, float]] = None,
    sharex: bool = False,
    sharey: bool = False,
) -> Tuple[Figure, Union[Axes, np.ndarray]]:
    """
    Create a figure with consistent styling.

    Args:
        nrows: Number of subplot rows
        ncols: Number of subplot columns
        figsize: Figure size (width, height) in inches
        sharex: Share x-axis across subplots
        sharey: Share y-axis across subplots

    Returns:
        (figure, axes) tuple
    """
    if figsize is None:
        # Default sizing: 7 inches per column, 4 inches per row
        figsize = (7 * ncols, 4 * nrows)

    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
    )

    return fig, axes


def save_figure(
    fig: Figure,
    output_path: str,
    dpi: int = 150,
    bbox_inches: str = "tight",
) -> str:
    """
    Save figure to file with consistent settings.

    Args:
        fig: Figure to save
        output_path: Output file path
        dpi: Resolution
        bbox_inches: Bounding box setting

    Returns:
        Path to saved file
    """
    fig.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
    plt.close(fig)
    print(f"Saved: {output_path}")
    return output_path


def _calculate_acf(series: List[float], max_lag: int = 20) -> List[float]:
    """Calculate autocorrelation function."""
    if len(series) < max_lag + 1:
        return []

    arr = np.array(series)
    mean = np.mean(arr)
    var = np.var(arr)

    if var == 0:
        return [0.0] * max_lag

    acf = []
    for lag in range(1, max_lag + 1):
        if len(arr) - lag < 1:
            break
        cov = np.mean((arr[lag:] - mean) * (arr[:-lag] - mean))
        acf.append(cov / var)

    return acf


# =============================================================================
# Price Dynamics
# =============================================================================


def plot_price_dynamics(
    prices: Dict[int, float],
    fundamental: Optional[float] = None,
    investor_bids: Optional[Dict[str, Dict[int, float]]] = None,
    output_path: Optional[str] = None,
    title: str = "Price Dynamics",
    show_deviation: bool = True,
) -> Optional[Figure]:
    """
    Plot market price dynamics with optional investor bids.

    Args:
        prices: {round: price} - Market price series
        fundamental: Fundamental value for reference line
        investor_bids: {investor_id: {round: bid_price}} - Optional investor bids
        output_path: Path to save figure (if None, returns Figure)
        title: Chart title
        show_deviation: Whether to show deviation subplot

    Returns:
        Figure if output_path is None, else None
    """
    n_rows = 2 if show_deviation else 1
    fig, axes = create_figure(nrows=n_rows, figsize=(14, 4 * n_rows))

    if n_rows == 1:
        axes = [axes]

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Main price plot
    ax = axes[0]
    ax.plot(
        rounds,
        price_values,
        color=COLORS["price"],
        linewidth=2,
        label="Market Price",
        zorder=10,
    )
    ax.axhline(
        y=fundamental,
        color=COLORS["fundamental"],
        linestyle="--",
        label=f"Fundamental ({fundamental})",
        alpha=0.7,
    )

    # Plot investor bids
    if investor_bids:
        styles = get_style_generator(len(investor_bids))
        for (inv_id, bids), (color, ls, marker) in zip(
            sorted(investor_bids.items()), styles
        ):
            inv_rounds = sorted(bids.keys())
            inv_prices = [bids[r] for r in inv_rounds]
            label = inv_id.replace("investor_", "").replace("_", " ")
            ax.plot(
                inv_rounds,
                inv_prices,
                color=color,
                linestyle=ls,
                marker=marker,
                markersize=3,
                linewidth=0.8,
                label=label,
                alpha=0.6,
            )

    ax.set_xlabel("Round", fontsize=11)
    ax.set_ylabel("Price", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)

    # Deviation subplot
    if show_deviation:
        ax2 = axes[1]
        deviation = [(p - fundamental) / fundamental * 100 for p in price_values]
        ax2.fill_between(
            rounds,
            deviation,
            0,
            where=[d >= 0 for d in deviation],
            color=COLORS["positive"],
            alpha=0.3,
            label="Overvalued",
        )
        ax2.fill_between(
            rounds,
            deviation,
            0,
            where=[d < 0 for d in deviation],
            color=COLORS["negative"],
            alpha=0.3,
            label="Undervalued",
        )
        ax2.plot(rounds, deviation, "k-", linewidth=1)
        ax2.axhline(y=0, color="gray", linestyle="-")
        ax2.set_xlabel("Round", fontsize=11)
        ax2.set_ylabel("Deviation from Fundamental (%)", fontsize=11)
        ax2.legend(loc="best")
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


# =============================================================================
# Returns Analysis
# =============================================================================


def plot_returns_analysis(
    prices: Dict[int, float],
    output_path: Optional[str] = None,
    title: str = "Returns Analysis",
    max_lag: int = 15,
) -> Optional[Figure]:
    """
    Plot comprehensive returns analysis with GARCH signature detection.

    Panels:
        1. Returns time series
        2. Squared returns (volatility proxy)
        3. Return ACF (should be ~0 for efficient market)
        4. Squared return ACF (should be >0 for GARCH effect)

    Args:
        prices: {round: price} - Market price series
        output_path: Path to save figure
        title: Chart title
        max_lag: Maximum lag for ACF calculation

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, ncols=2, figsize=(14, 10))

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Calculate returns
    returns = []
    for i in range(1, len(price_values)):
        if price_values[i - 1] > 0:
            returns.append(
                (price_values[i] - price_values[i - 1]) / price_values[i - 1]
            )
        else:
            returns.append(0)

    sq_returns = [r**2 for r in returns]
    return_rounds = rounds[1:]

    # Panel 1: Returns time series
    axes[0, 0].plot(
        return_rounds, returns, color=COLORS["return"], linewidth=0.8, alpha=0.7
    )
    axes[0, 0].axhline(y=0, color="gray", linestyle="--")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Return")
    axes[0, 0].set_title("Returns Over Time")
    axes[0, 0].grid(True, alpha=0.3)

    # Panel 2: Squared returns
    axes[0, 1].plot(
        return_rounds, sq_returns, color=COLORS["volatility"], linewidth=0.8, alpha=0.7
    )
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Squared Return")
    axes[0, 1].set_title("Squared Returns (Volatility Proxy)")
    axes[0, 1].grid(True, alpha=0.3)

    # Panel 3: Return ACF
    if len(returns) >= 20:
        return_acf = _calculate_acf(returns, max_lag)
        lags = list(range(1, len(return_acf) + 1))
        axes[1, 0].bar(lags, return_acf, color=COLORS["price"], alpha=0.7)
        axes[1, 0].axhline(y=0, color="gray", linestyle="-")
        # Confidence bounds
        conf = 1.96 / np.sqrt(len(returns))
        axes[1, 0].axhline(y=conf, color="red", linestyle="--", alpha=0.5)
        axes[1, 0].axhline(y=-conf, color="red", linestyle="--", alpha=0.5)
    axes[1, 0].set_xlabel("Lag")
    axes[1, 0].set_ylabel("Autocorrelation")
    axes[1, 0].set_title("Return ACF (Should be ~0 for Efficiency)")
    axes[1, 0].grid(True, alpha=0.3)

    # Panel 4: Squared Return ACF
    if len(sq_returns) >= 20:
        sq_acf = _calculate_acf(sq_returns, max_lag)
        lags = list(range(1, len(sq_acf) + 1))
        axes[1, 1].bar(lags, sq_acf, color=COLORS["volatility"], alpha=0.7)
        axes[1, 1].axhline(y=0, color="gray", linestyle="-")
    axes[1, 1].set_xlabel("Lag")
    axes[1, 1].set_ylabel("Autocorrelation")
    axes[1, 1].set_title("Squared Return ACF (>0 = GARCH Effect)")
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


# =============================================================================
# Volatility Analysis
# =============================================================================


def plot_volatility_analysis(
    prices: Dict[int, float],
    volatility: Optional[Dict[int, float]] = None,
    fundamental: Optional[float] = None,
    output_path: Optional[str] = None,
    title: str = "Volatility Analysis",
    window: int = 10,
) -> Optional[Figure]:
    """
    Plot volatility dynamics with regime highlighting.

    Args:
        prices: {round: price} - Market price series
        volatility: {round: volatility} - Pre-computed volatility (optional)
        output_path: Path to save figure
        title: Chart title
        window: Rolling window for volatility calculation

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, figsize=(14, 8), sharex=True)

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Calculate volatility if not provided
    if volatility is None:
        volatility = {}
        for i, r in enumerate(rounds):
            if i >= window - 1:
                window_prices = price_values[i - window + 1 : i + 1]
                volatility[r] = float(np.std(window_prices))

    vol_rounds = sorted(volatility.keys())
    vol_values = [volatility[r] for r in vol_rounds]

    # Price panel
    axes[0].plot(
        rounds, price_values, color=COLORS["price"], linewidth=1.5, label="Price"
    )
    if fundamental is not None:
        axes[0].axhline(
            y=fundamental,
            color=COLORS["fundamental"],
            linestyle="--",
            alpha=0.7,
            label="Fundamental",
        )
    axes[0].set_ylabel("Price", fontsize=11)
    axes[0].set_title(title, fontsize=13, fontweight="bold")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    # Volatility panel with regime highlighting
    if vol_values:
        avg_vol = np.mean(vol_values)
        high_threshold = avg_vol * 1.5
        low_threshold = avg_vol / 1.5

        axes[1].plot(
            vol_rounds,
            vol_values,
            color=COLORS["volatility"],
            linewidth=1.5,
            label="Volatility (σ)",
        )
        axes[1].axhline(
            y=avg_vol,
            color="gray",
            linestyle="--",
            label=f"Mean: {avg_vol:.3f}",
            alpha=0.7,
        )
        axes[1].axhline(
            y=high_threshold,
            color="orange",
            linestyle=":",
            label=f"High regime (>{high_threshold:.3f})",
            alpha=0.7,
        )

        # Highlight high volatility regimes
        for i, (r, v) in enumerate(zip(vol_rounds, vol_values)):
            if v > high_threshold:
                axes[1].axvspan(r - 0.5, r + 0.5, color="red", alpha=0.1)

    axes[1].set_xlabel("Round", fontsize=11)
    axes[1].set_ylabel("Volatility", fontsize=11)
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


# =============================================================================
# Herding Analysis
# =============================================================================


def plot_herding_metrics(
    cv_series: Dict[int, float],
    agreement_series: Dict[int, float],
    output_path: Optional[str] = None,
    title: str = "Herding Metrics",
) -> Optional[Figure]:
    """
    Plot herding detection metrics.

    Args:
        cv_series: {round: cv_value} - Coefficient of variation
        agreement_series: {round: agreement_value} - Directional agreement
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, figsize=(14, 8), sharex=True)

    # Bid Convergence (CV)
    if cv_series:
        cv_rounds = sorted(cv_series.keys())
        cv_values = [cv_series[r] for r in cv_rounds]
        axes[0].plot(
            cv_rounds, cv_values, color=COLORS["price"], linewidth=1.5, label="CV"
        )
        axes[0].axhline(
            y=0.05,
            color="red",
            linestyle="--",
            label="Strong Herding (CV<0.05)",
            alpha=0.7,
        )
        axes[0].axhline(
            y=0.10,
            color="orange",
            linestyle="--",
            label="Moderate Herding (CV<0.10)",
            alpha=0.7,
        )

        # Fill below threshold
        axes[0].fill_between(
            cv_rounds,
            cv_values,
            0.05,
            where=[v < 0.05 for v in cv_values],
            color="red",
            alpha=0.2,
        )

    axes[0].set_ylabel("Coefficient of Variation", fontsize=11)
    axes[0].set_title("Bid Convergence Index (CV) - Lower = More Herding")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(bottom=0)

    # Directional Agreement
    if agreement_series:
        da_rounds = sorted(agreement_series.keys())
        da_values = [agreement_series[r] for r in da_rounds]
        axes[1].plot(
            da_rounds, da_values, color=COLORS["return"], linewidth=1.5, label="DA"
        )
        axes[1].axhline(
            y=0.8,
            color="red",
            linestyle="--",
            label="Strong Alignment (DA>0.8)",
            alpha=0.7,
        )
        axes[1].fill_between(
            da_rounds,
            da_values,
            0.5,
            where=[v > 0.5 for v in da_values],
            color="green",
            alpha=0.2,
        )

    axes[1].set_xlabel("Round", fontsize=11)
    axes[1].set_ylabel("Directional Agreement", fontsize=11)
    axes[1].set_title("Directional Agreement - Higher = More Aligned")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(0, 1)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


def plot_bid_convergence(
    investor_bids: Dict[str, Dict[int, float]],
    prices: Dict[int, float],
    output_path: Optional[str] = None,
    title: str = "Bid Convergence Analysis",
) -> Optional[Figure]:
    """
    Plot investor bid convergence over time.

    Args:
        investor_bids: {investor_id: {round: bid_price}}
        prices: {round: price} - Market price for reference
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, figsize=(14, 8), sharex=True)

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Panel 1: All investor bids with market price
    axes[0].plot(
        rounds,
        price_values,
        color=COLORS["price"],
        linewidth=2,
        label="Market Price",
        zorder=10,
    )

    styles = get_style_generator(len(investor_bids))
    for (inv_id, bids), (color, ls, marker) in zip(
        sorted(investor_bids.items()), styles
    ):
        inv_rounds = sorted(bids.keys())
        inv_prices = [bids[r] for r in inv_rounds]
        label = inv_id.replace("investor_", "")
        axes[0].plot(
            inv_rounds,
            inv_prices,
            color=color,
            linestyle=ls,
            marker=marker,
            markersize=2,
            linewidth=0.8,
            label=label,
            alpha=0.6,
        )

    axes[0].set_ylabel("Price / Bid", fontsize=11)
    axes[0].set_title("Investor Bids vs Market Price")
    axes[0].legend(loc="best", fontsize=8, ncol=3)
    axes[0].grid(True, alpha=0.3)

    # Panel 2: Bid dispersion (std of bids per round)
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())

    dispersion = {}
    for r in sorted(all_rounds):
        bids_at_r = [bids[r] for bids in investor_bids.values() if r in bids]
        if len(bids_at_r) >= 2:
            dispersion[r] = float(np.std(bids_at_r))

    if dispersion:
        disp_rounds = sorted(dispersion.keys())
        disp_values = [dispersion[r] for r in disp_rounds]
        axes[1].fill_between(
            disp_rounds, disp_values, 0, color=COLORS["volume"], alpha=0.5
        )
        axes[1].plot(disp_rounds, disp_values, color=COLORS["volume"], linewidth=1.5)

    axes[1].set_xlabel("Round", fontsize=11)
    axes[1].set_ylabel("Bid Dispersion (σ)", fontsize=11)
    axes[1].set_title("Cross-Sectional Bid Dispersion - Lower = More Convergence")
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


# =============================================================================
# Agent Analysis
# =============================================================================


def plot_agent_activity(
    impact: Dict[str, Dict[str, float]],
    output_path: Optional[str] = None,
    title: str = "Agent Activity Analysis",
) -> Optional[Figure]:
    """
    Plot trading activity by strategy type.

    Args:
        impact: {strategy: {total_volume, net_direction, avg_trade_size, trade_count}}
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    if not impact:
        print(f"Skipped (no data): {output_path}")
        return None

    fig, axes = create_figure(nrows=1, ncols=2, figsize=(14, 6))

    strategies = list(impact.keys())
    volumes = [impact[s]["total_volume"] for s in strategies]
    net_dirs = [impact[s]["net_direction"] for s in strategies]

    # Panel 1: Total volume by strategy
    cmap = plt.colormaps["tab10"]
    colors = [cmap(i) for i in range(len(strategies))]
    axes[0].bar(strategies, volumes, color=colors)
    axes[0].set_xlabel("Strategy", fontsize=11)
    axes[0].set_ylabel("Total Volume", fontsize=11)
    axes[0].set_title("Trading Volume by Strategy")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].grid(True, alpha=0.3, axis="y")

    # Panel 2: Net direction by strategy
    colors_dir = [
        COLORS["positive"] if d >= 0 else COLORS["negative"] for d in net_dirs
    ]
    axes[1].bar(strategies, net_dirs, color=colors_dir)
    axes[1].axhline(y=0, color="gray", linestyle="-")
    axes[1].set_xlabel("Strategy", fontsize=11)
    axes[1].set_ylabel("Net Direction", fontsize=11)
    axes[1].set_title("Net Trading Direction by Strategy")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


def plot_strategy_contribution(
    contribution: Dict[str, Dict[str, float]],
    output_path: Optional[str] = None,
    title: str = "Strategy Contribution Analysis",
) -> Optional[Figure]:
    """
    Plot each strategy's contribution to market dynamics.

    Args:
        contribution: {strategy: {pro_bubble, pro_crash, stabilizing}}
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    if not contribution:
        print(f"Skipped (no data): {output_path}")
        return None

    fig, ax = create_figure(figsize=(12, 6))

    strategies = list(contribution.keys())
    pro_bubble = [contribution[s]["pro_bubble"] for s in strategies]
    pro_crash = [contribution[s]["pro_crash"] for s in strategies]
    stabilizing = [contribution[s]["stabilizing"] for s in strategies]

    x = np.arange(len(strategies))
    width = 0.25

    ax.bar(x - width, pro_bubble, width, label="Pro-Bubble", color="#ff7f0e")
    ax.bar(x, pro_crash, width, label="Pro-Crash", color="#d62728")
    ax.bar(x + width, stabilizing, width, label="Stabilizing", color="#2ca02c")

    ax.set_xlabel("Strategy", fontsize=11)
    ax.set_ylabel("Contribution Ratio", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(strategies, rotation=45, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


# =============================================================================
# Comprehensive Summary
# =============================================================================


def plot_multi_panel_summary(
    prices: Dict[int, float],
    volatility: Optional[Dict[int, float]] = None,
    investor_quantities: Optional[Dict[str, Dict[int, float]]] = None,
    fundamental: Optional[float] = None,
    output_path: Optional[str] = None,
    title: str = "Simulation Summary",
) -> Optional[Figure]:
    """
    Generate comprehensive 6-panel summary.

    Panels:
        1. Price dynamics
        2. Returns
        3. Volatility
        4. Price deviation from fundamental
        5. Trading volume
        6. Price distribution

    Args:
        prices: {round: price} - Market price series
        volatility: {round: volatility} - Optional volatility series
        investor_quantities: {investor_id: {round: quantity}} - Optional trading data
        fundamental: Fundamental value
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, ncols=3, figsize=(18, 10))

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Panel 1: Price
    axes[0, 0].plot(rounds, price_values, color=COLORS["price"], linewidth=1)
    axes[0, 0].axhline(
        y=fundamental, color=COLORS["fundamental"], linestyle="--", alpha=0.5
    )
    axes[0, 0].set_title("Price", fontsize=12)
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].grid(True, alpha=0.3)

    # Panel 2: Returns
    if len(price_values) > 1:
        returns = []
        for i in range(1, len(price_values)):
            if price_values[i - 1] > 0:
                returns.append(
                    (price_values[i] - price_values[i - 1]) / price_values[i - 1]
                )
            else:
                returns.append(0)
        axes[0, 1].plot(
            rounds[1:], returns, color=COLORS["return"], linewidth=0.8, alpha=0.7
        )
        axes[0, 1].axhline(y=0, color="gray", linestyle="--")
    axes[0, 1].set_title("Returns", fontsize=12)
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].grid(True, alpha=0.3)

    # Panel 3: Volatility
    if volatility:
        vol_rounds = sorted(volatility.keys())
        vol_values = [volatility[r] for r in vol_rounds]
        axes[0, 2].plot(vol_rounds, vol_values, color=COLORS["volatility"], linewidth=1)
    axes[0, 2].set_title("Volatility", fontsize=12)
    axes[0, 2].set_xlabel("Round")
    axes[0, 2].grid(True, alpha=0.3)

    # Panel 4: Price deviation from fundamental
    deviation = [(p - fundamental) / fundamental * 100 for p in price_values]
    axes[1, 0].fill_between(
        rounds,
        deviation,
        0,
        where=[d >= 0 for d in deviation],
        color=COLORS["positive"],
        alpha=0.3,
    )
    axes[1, 0].fill_between(
        rounds,
        deviation,
        0,
        where=[d < 0 for d in deviation],
        color=COLORS["negative"],
        alpha=0.3,
    )
    axes[1, 0].plot(rounds, deviation, "k-", linewidth=1)
    axes[1, 0].axhline(y=0, color="gray", linestyle="-")
    axes[1, 0].set_title("Price Deviation (%)", fontsize=12)
    axes[1, 0].set_xlabel("Round")
    axes[1, 0].grid(True, alpha=0.3)

    # Panel 5: Volume
    if investor_quantities:
        total_vol = defaultdict(float)
        for inv_qtys in investor_quantities.values():
            for r, qty in inv_qtys.items():
                total_vol[r] += abs(qty)
        vol_rounds = sorted(total_vol.keys())
        vol_values = [total_vol[r] for r in vol_rounds]
        axes[1, 1].bar(vol_rounds, vol_values, color=COLORS["volume"], alpha=0.6)
    axes[1, 1].set_title("Total Volume", fontsize=12)
    axes[1, 1].set_xlabel("Round")
    axes[1, 1].grid(True, alpha=0.3)

    # Panel 6: Price histogram
    axes[1, 2].hist(
        price_values, bins=20, color=COLORS["price"], alpha=0.7, edgecolor="black"
    )
    axes[1, 2].axvline(
        x=fundamental,
        color=COLORS["negative"],
        linestyle="--",
        label=f"Fundamental: {fundamental}",
    )
    axes[1, 2].axvline(
        x=np.mean(price_values),
        color=COLORS["positive"],
        linestyle="--",
        label=f"Mean: {np.mean(price_values):.2f}",
    )
    axes[1, 2].set_title("Price Distribution", fontsize=12)
    axes[1, 2].set_xlabel("Price")
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=16, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig


def plot_bubble_crash_analysis(
    prices: Dict[int, float],
    fundamental: Optional[float] = None,
    output_path: Optional[str] = None,
    title: str = "Bubble/Crash Analysis",
) -> Optional[Figure]:
    """
    Plot bubble/crash specific analysis.

    Panels:
        1. Price with bubble/crash phases highlighted
        2. Cumulative deviation from fundamental
        3. Price acceleration (second derivative)
        4. Bubble magnitude indicator

    Args:
        prices: {round: price} - Market price series
        fundamental: Fundamental value
        output_path: Path to save figure
        title: Chart title

    Returns:
        Figure if output_path is None, else None
    """
    fig, axes = create_figure(nrows=2, ncols=2, figsize=(14, 10))

    rounds = sorted(prices.keys())
    price_values = [prices[r] for r in rounds]

    # Panel 1: Price with phase highlighting
    deviation = [(p - fundamental) / fundamental * 100 for p in price_values]

    axes[0, 0].plot(rounds, price_values, color=COLORS["price"], linewidth=1.5)
    axes[0, 0].axhline(
        y=fundamental,
        color=COLORS["fundamental"],
        linestyle="--",
        alpha=0.7,
        label="Fundamental",
    )

    # Highlight bubble (>10% above) and crash (<10% below) phases
    for i, (r, d) in enumerate(zip(rounds, deviation)):
        if d > 10:
            axes[0, 0].axvspan(r - 0.5, r + 0.5, color="red", alpha=0.1)
        elif d < -10:
            axes[0, 0].axvspan(r - 0.5, r + 0.5, color="blue", alpha=0.1)

    axes[0, 0].set_title("Price with Bubble/Crash Phases", fontsize=12)
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Panel 2: Cumulative deviation
    cumulative_dev = np.cumsum([p - fundamental for p in price_values])
    axes[0, 1].fill_between(
        rounds,
        cumulative_dev,
        0,
        where=cumulative_dev >= 0,
        color=COLORS["positive"],
        alpha=0.5,
    )
    axes[0, 1].fill_between(
        rounds,
        cumulative_dev,
        0,
        where=cumulative_dev < 0,
        color=COLORS["negative"],
        alpha=0.5,
    )
    axes[0, 1].plot(rounds, cumulative_dev, "k-", linewidth=1)
    axes[0, 1].axhline(y=0, color="gray", linestyle="-")
    axes[0, 1].set_title("Cumulative Bubble Magnitude", fontsize=12)
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Cumulative Deviation")
    axes[0, 1].grid(True, alpha=0.3)

    # Panel 3: Price acceleration
    if len(price_values) >= 3:
        returns = np.diff(price_values) / np.array(price_values[:-1])
        acceleration = np.diff(returns)
        accel_rounds = rounds[2:]
        axes[1, 0].bar(
            accel_rounds,
            acceleration,
            color=[
                COLORS["positive"] if a >= 0 else COLORS["negative"]
                for a in acceleration
            ],
            alpha=0.7,
        )
        axes[1, 0].axhline(y=0, color="gray", linestyle="-")
    axes[1, 0].set_title("Price Acceleration (Momentum Change)", fontsize=12)
    axes[1, 0].set_xlabel("Round")
    axes[1, 0].set_ylabel("Acceleration")
    axes[1, 0].grid(True, alpha=0.3)

    # Panel 4: Rolling max drawdown
    if len(price_values) >= 10:
        window = min(20, len(price_values) // 2)
        drawdowns = []
        dd_rounds = []
        for i in range(window, len(price_values)):
            window_prices = price_values[i - window : i + 1]
            peak = max(window_prices)
            dd = (price_values[i] - peak) / peak * 100
            drawdowns.append(dd)
            dd_rounds.append(rounds[i])

        axes[1, 1].fill_between(
            dd_rounds, drawdowns, 0, color=COLORS["negative"], alpha=0.5
        )
        axes[1, 1].plot(dd_rounds, drawdowns, color=COLORS["negative"], linewidth=1)
        axes[1, 1].axhline(y=0, color="gray", linestyle="-")
    axes[1, 1].set_title("Rolling Drawdown (%)", fontsize=12)
    axes[1, 1].set_xlabel("Round")
    axes[1, 1].set_ylabel("Drawdown (%)")
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        return save_figure(fig, output_path)
    return fig
