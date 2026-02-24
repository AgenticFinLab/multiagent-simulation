"""HerdEffect Analysis - Emergent Herding Metrics & Visualization

Reads simulation results from communication storage and generates:
1. Price dynamics charts (market price & investor bids)
2. Emergent Herding Detection Metrics:
   - Bid Convergence Index (CV): 出价收敛度，CV↓ = 行为趋同
   - Directional Agreement: 方向一致性，DA > 0.8 = 强羊群
   - Information Cascade Measure: 信息级联强度
   - Price Deviation: 价格偏离基本面程度
   - Cross-Sectional Standard Deviation (LSV-inspired)
   - Rolling Volatility
   - Autocorrelation (momentum persistence)

Emergent Herding Model:
   - NO explicit HerdingInvestor
   - Herding EMERGES from Momentum + Aggressive positive feedback
   - Key metrics detect behavioral convergence without imitation

References:
- Bikhchandani, Hirshleifer, Welch (1992): Information Cascades
- Lakonishok, Shleifer, Vishny (1992): LSV Herding Measure
- Chang, Cheng, Khorana (2000): CSAD measure
- Jegadeesh & Titman (1993): Momentum effect
- De Long et al. (1990): Noise trader model

Usage:
    python examples/HerdEffect/analysis.py -c configs/HerdEffect/simulation.yml"""

import argparse
import json
import os
import glob
from collections import defaultdict

import matplotlib
import numpy as np
import yaml

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from scipy import stats

# Constants
FUNDAMENTAL_VALUE = 100.0  # Must match Market.FUNDAMENTAL_VALUE in players.py

# Line styles for cycling
LINE_STYLES = ["-", "--", "-.", ":"]
MARKERS = ["o", "s", "^", "D", "v", "<", ">", "p", "h", "*"]


def get_style_generator(n_players: int):
    """
    Generate colors and line styles for n players.

    Returns:
        List of (color, linestyle, marker) tuples
    """
    # Use colormap to generate distinct colors
    if n_players <= 10:
        cmap = plt.colormaps["tab10"]
    elif n_players <= 20:
        cmap = plt.colormaps["tab20"]
    else:
        cmap = plt.colormaps["hsv"]

    styles = []
    for i in range(n_players):
        color = cmap(i / max(n_players, 1))
        linestyle = LINE_STYLES[i % len(LINE_STYLES)]
        marker = MARKERS[i % len(MARKERS)]
        styles.append((color, linestyle, marker))

    return styles


def load_config(config_path: str) -> dict:
    """Load simulation config with !include support."""

    class IncludeLoader(yaml.SafeLoader):
        pass

    def include_constructor(loader, node):
        filename = loader.construct_scalar(node)
        base_dir = os.path.dirname(loader.stream.name)
        filepath = os.path.join(base_dir, filename)
        with open(filepath, "r") as f:
            return yaml.load(f, IncludeLoader)

    IncludeLoader.add_constructor("!include", include_constructor)

    with open(config_path, "r") as f:
        return yaml.load(f, IncludeLoader)


def get_paths_from_config(config: dict) -> tuple:
    """
    Extract data_dir and output_dir from config.

    Returns:
        (data_dir, output_dir)
    """
    # Get communication storage path for reading data
    data_dir = config["communication"]["storage_path"]

    # Get base path from record_path (e.g., "EXPERIMENT/HerdEffect/records" -> "EXPERIMENT/HerdEffect")
    record_path = config["setting"]["record_path"]
    base_path = os.path.dirname(record_path)
    output_dir = os.path.join(base_path, "analysis")

    return data_dir, output_dir


def load_messages(data_dir: str) -> list:
    """Load all messages from msg_block_*.json files."""
    messages = []
    pattern = os.path.join(data_dir, "msg_block_*.json")

    for filepath in sorted(glob.glob(pattern)):
        with open(filepath, "r") as f:
            data = json.load(f)
            for msg_id, msg_data in data.items():
                encoded = json.loads(msg_data["encoded"])
                messages.append(encoded)

    return messages


def extract_price_data(messages: list) -> dict:
    """
    Extract market prices and investor bids per round.

    Returns:
        {
            "market_price": {round: price},
            "investor_bids": {investor_id: {round: bid_price}},
            "investor_quantities": {investor_id: {round: quantity}}
        }
    """
    market_price = {}
    investor_bids = defaultdict(dict)
    investor_quantities = defaultdict(dict)

    for msg in messages:
        sender = msg["sender_id"]
        payload = msg["payload"]
        content = payload["content"]
        content_type = payload["content_type"]
        round_num = msg["extras"]["round_num"]

        if content_type == "market_price" and sender == "market":
            market_price[round_num] = content["price"]

        elif content_type == "investor_bid":
            investor_bids[sender][round_num] = content["bid_price"]
            investor_quantities[sender][round_num] = content["quantity"]

    return {
        "market_price": market_price,
        "investor_bids": dict(investor_bids),
        "investor_quantities": dict(investor_quantities),
    }


# =============================================================================
# Herd Effect Metrics Calculation
# =============================================================================


def calculate_price_deviation(market_prices: dict, fundamental: float = FUNDAMENTAL_VALUE) -> dict:
    """
    Calculate price deviation from fundamental value.
    
    Formula: deviation_t = (P_t - F) / F
    
    Returns:
        {round: deviation_pct}
    """
    deviation = {}
    for r, price in market_prices.items():
        deviation[r] = (price - fundamental) / fundamental * 100
    return deviation


def calculate_bid_convergence_cv(investor_bids: dict) -> dict:
    """
    Calculate Bid Convergence Index using Coefficient of Variation (CV).
    
    Formula: CV_t = std(Bid_1,t, ..., Bid_N,t) / mean(Bid_1,t, ..., Bid_N,t)
    
    Interpretation:
        - CV ↓ = bids converging = herding forming
        - CV < 0.05 = strong herding
        - CV > 0.15 = dispersed opinions (normal market)
    
    Returns:
        {round: cv_value}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    
    cv_series = {}
    for r in sorted(all_rounds):
        bids_at_r = [bids[r] for bids in investor_bids.values() if r in bids]
        if len(bids_at_r) >= 2:
            mean_bid = np.mean(bids_at_r)
            if mean_bid > 0:
                cv_series[r] = np.std(bids_at_r) / mean_bid
    return cv_series


def calculate_directional_agreement(investor_bids: dict) -> dict:
    """
    Calculate Directional Agreement - measures behavioral alignment.
    
    Formula: DA_t = |Σ(sign(Bid_{i,t} - Bid_{i,t-1}))| / N
    
    Interpretation:
        - DA = 1: all investors moving same direction (strong herding)
        - DA ≈ 0.5: random/divergent behavior
        - DA > 0.8: significant behavioral alignment
    
    Returns:
        {round: agreement_value}
    """
    # Get all rounds sorted
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    rounds = sorted(all_rounds)
    
    if len(rounds) < 2:
        return {}
    
    agreement_series = {}
    for i in range(1, len(rounds)):
        r_curr, r_prev = rounds[i], rounds[i - 1]
        
        directions = []
        for inv_id, bids in investor_bids.items():
            if r_curr in bids and r_prev in bids:
                delta = bids[r_curr] - bids[r_prev]
                if delta > 0:
                    directions.append(1)
                elif delta < 0:
                    directions.append(-1)
                else:
                    directions.append(0)
        
        if len(directions) > 0:
            # Agreement = |sum of directions| / N
            # 1 = all same direction, 0 = balanced
            agreement = abs(sum(directions)) / len(directions)
            agreement_series[r_curr] = agreement
    
    return agreement_series


def calculate_cascade_measure(investor_bids: dict, market_prices: dict, 
                              fundamental: float = FUNDAMENTAL_VALUE) -> dict:
    """
    Calculate Information Cascade Measure.
    
    Based on Bikhchandani et al. (1992): when investors ignore their private
    signals and follow the market trend, a cascade is forming.
    
    Logic:
        - If price > fundamental, rational signal = SELL
        - If investor bids ABOVE market price, they're ignoring signal = CASCADE
        - Cascade ratio = proportion of investors ignoring private signals
    
    Returns:
        {round: cascade_ratio}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    
    cascade_series = {}
    for r in sorted(all_rounds):
        if r not in market_prices:
            continue
        
        price = market_prices[r]
        
        # Count investors ignoring private signal
        contrarian_count = 0
        total_count = 0
        
        for inv_id, bids in investor_bids.items():
            if r not in bids:
                continue
            
            bid = bids[r]
            total_count += 1
            
            # Private signal based on fundamental
            private_signal = 'buy' if price < fundamental else 'sell'
            
            # Actual behavior based on bid vs market
            actual = 'buy' if bid > price else 'sell'
            
            # If actual != private signal, investor is following cascade
            if private_signal != actual:
                contrarian_count += 1
        
        if total_count > 0:
            cascade_series[r] = contrarian_count / total_count
    
    return cascade_series


def calculate_cross_sectional_std(investor_bids: dict) -> dict:
    """
    Calculate cross-sectional standard deviation of investor bids.
    
    Inspired by LSV (1992) and CSAD (Chang et al. 2000) measures.
    Lower std = higher herding (investors bid similarly).
    
    Formula: CSSD_t = std(Bid_1,t, Bid_2,t, ..., Bid_N,t)
    
    Returns:
        {round: std_value}
    """
    # Collect all rounds
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    
    cross_std = {}
    for r in sorted(all_rounds):
        bids_at_r = [bids[r] for bids in investor_bids.values() if r in bids]
        if len(bids_at_r) >= 2:
            cross_std[r] = np.std(bids_at_r)
    return cross_std


def calculate_rolling_volatility(market_prices: dict, window: int = 10) -> dict:
    """
    Calculate rolling price volatility.
    
    Formula: volatility_t = std(P_t-window:t)
    
    Returns:
        {round: volatility}
    """
    rounds = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds]
    
    volatility = {}
    for i, r in enumerate(rounds):
        if i >= window - 1:
            window_prices = prices[i - window + 1 : i + 1]
            volatility[r] = np.std(window_prices)
    return volatility


def calculate_autocorrelation(market_prices: dict, lag: int = 1) -> dict:
    """
    Calculate rolling price return autocorrelation (momentum persistence).
    
    Higher autocorrelation = stronger momentum = potential herding.
    
    Returns:
        {round: autocorr}
    """
    rounds = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds]
    
    # Calculate returns
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i - 1]) / prices[i - 1]
        returns.append(ret)
    
    if len(returns) < lag + 10:
        return {}
    
    # Rolling autocorrelation (window=20)
    window = 20
    autocorr = {}
    for i in range(window - 1, len(returns)):
        r = rounds[i + 1]  # Offset by 1 due to returns calculation
        window_returns = returns[i - window + 1 : i + 1]
        if len(window_returns) >= lag + 2:
            # Compute autocorrelation at given lag
            series = np.array(window_returns)
            if len(series) > lag:
                corr = np.corrcoef(series[:-lag], series[lag:])[0, 1]
                if not np.isnan(corr):
                    autocorr[r] = corr
    return autocorr


def calculate_investor_correlation_matrix(investor_bids: dict) -> dict:
    """
    Calculate pairwise correlation matrix between all investors.
    
    In emergent herding model, we look for increasing correlation
    between Momentum and Aggressive investors (the feedback amplifiers).
    
    Returns:
        {(inv1, inv2): correlation}
    """
    investor_ids = sorted(investor_bids.keys())
    correlations = {}
    
    for i, inv1 in enumerate(investor_ids):
        for inv2 in investor_ids[i+1:]:
            bids1 = investor_bids[inv1]
            bids2 = investor_bids[inv2]
            
            common_rounds = sorted(set(bids1.keys()) & set(bids2.keys()))
            if len(common_rounds) < 10:
                continue
            
            vals1 = [bids1[r] for r in common_rounds]
            vals2 = [bids2[r] for r in common_rounds]
            
            corr, _ = stats.pearsonr(vals1, vals2)
            correlations[(inv1, inv2)] = corr
    
    return correlations


def calculate_rolling_cv(investor_bids: dict, window: int = 20) -> dict:
    """
    Calculate rolling bid convergence (CV) over time.
    
    Shows the dynamics of herd formation/dissolution.
    
    Returns:
        {round: cv}
    """
    all_rounds = set()
    for bids in investor_bids.values():
        all_rounds.update(bids.keys())
    rounds = sorted(all_rounds)
    
    if len(rounds) < window:
        return {}
    
    rolling_cv = {}
    for i in range(window - 1, len(rounds)):
        r = rounds[i]
        window_rounds = rounds[i - window + 1 : i + 1]
        
        # Calculate mean CV over window
        cvs = []
        for wr in window_rounds:
            bids_at_r = [bids[wr] for bids in investor_bids.values() if wr in bids]
            if len(bids_at_r) >= 2:
                mean_bid = np.mean(bids_at_r)
                if mean_bid > 0:
                    cvs.append(np.std(bids_at_r) / mean_bid)
        
        if cvs:
            rolling_cv[r] = np.mean(cvs)
    
    return rolling_cv


def calculate_bubble_magnitude(market_prices: dict, fundamental: float = FUNDAMENTAL_VALUE) -> dict:
    """
    Calculate cumulative bubble magnitude.
    
    Formula: bubble_t = Σ(P_s - F) for s=1 to t
    
    Returns:
        {round: cumulative_bubble}
    """
    rounds = sorted(market_prices.keys())
    cumsum = 0
    bubble = {}
    for r in rounds:
        cumsum += market_prices[r] - fundamental
        bubble[r] = cumsum
    return bubble


def calculate_volume_metrics(investor_quantities: dict) -> dict:
    """
    Calculate volume metrics per round for emergent herding analysis.
    
    In emergent model, we track:
    - Total volume (market activity)
    - Buy/Sell ratio (directional bias)
    - Feedback investor share (Momentum + Aggressive combined)
    
    Returns:
        {
            'total_volume': {round: vol},
            'buy_ratio': {round: ratio},
            'feedback_share': {round: share_pct}  # Momentum + Aggressive
        }
    """
    all_rounds = set()
    for qtys in investor_quantities.values():
        all_rounds.update(qtys.keys())
    
    # Find feedback investors (Momentum + Aggressive = emergent herding drivers)
    feedback_ids = []
    for inv_id in investor_quantities.keys():
        if "momentum" in inv_id.lower() or "aggressive" in inv_id.lower():
            feedback_ids.append(inv_id)
    
    total_volume = {}
    buy_ratio = {}
    feedback_share = {}
    
    for r in sorted(all_rounds):
        quantities = {inv_id: qtys[r] for inv_id, qtys in investor_quantities.items() if r in qtys}
        
        total_vol = sum(abs(q) for q in quantities.values())
        total_volume[r] = total_vol
        
        # Calculate feedback investor share
        if feedback_ids and total_vol > 0:
            feedback_vol = sum(abs(quantities.get(fid, 0)) for fid in feedback_ids)
            feedback_share[r] = feedback_vol / total_vol * 100
        
        buy_qty = sum(q for q in quantities.values() if q > 0)
        sell_qty = sum(abs(q) for q in quantities.values() if q < 0)
        if buy_qty + sell_qty > 0:
            buy_ratio[r] = buy_qty / (buy_qty + sell_qty) * 100
    
    return {
        'total_volume': total_volume,
        'buy_ratio': buy_ratio,
        'feedback_share': feedback_share,
    }


# =============================================================================
# Visualization Functions
# =============================================================================


def plot_prices(data: dict, output_path: str = None):
    """Plot market price and investor bids over rounds."""
    plt.figure(figsize=(14, 8))

    # Extract data
    market_price = data["market_price"]
    investor_bids = data["investor_bids"]

    # Sort rounds
    rounds = sorted(market_price.keys())

    # Plot market price (black solid line)
    prices = [market_price[r] for r in rounds]
    plt.plot(
        rounds,
        prices,
        "k-",
        linewidth=2.5,
        label="Market Price",
        marker="o",
        markersize=4,
    )

    # Auto-generate styles for investors
    investor_ids = sorted(investor_bids.keys())
    styles = get_style_generator(len(investor_ids))

    # Plot investor bids
    for i, investor_id in enumerate(investor_ids):
        bids = investor_bids[investor_id]
        rounds_inv = sorted(bids.keys())
        bid_prices = [bids[r] for r in rounds_inv]

        label = investor_id.replace("investor_", "").replace("_", " ").title()
        color, linestyle, marker = styles[i]

        plt.plot(
            rounds_inv,
            bid_prices,
            linestyle=linestyle,
            linewidth=1.5,
            label=label,
            color=color,
            alpha=0.8,
            marker=marker,
            markersize=3,
            markevery=max(1, len(rounds_inv) // 10),
        )

    plt.xlabel("Round", fontsize=12)
    plt.ylabel("Price / Bid", fontsize=12)
    plt.title("Herd Effect Simulation: Market Price & Investor Bids", fontsize=14)
    plt.legend(loc="best", fontsize=9, ncol=min(3, (len(investor_ids) + 1) // 2 + 1))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()

    plt.close()


def plot_quantities(data: dict, output_path: str = None):
    """Plot investor quantities (buy/sell) over rounds."""
    plt.figure(figsize=(14, 6))

    investor_quantities = data["investor_quantities"]

    # Auto-generate styles for investors
    investor_ids = sorted(investor_quantities.keys())
    styles = get_style_generator(len(investor_ids))

    for i, investor_id in enumerate(investor_ids):
        quantities = investor_quantities[investor_id]
        rounds_inv = sorted(quantities.keys())
        qtys = [quantities[r] for r in rounds_inv]

        label = investor_id.replace("investor_", "").replace("_", " ").title()
        color, linestyle, marker = styles[i]

        plt.plot(
            rounds_inv,
            qtys,
            linestyle=linestyle,
            linewidth=1.5,
            label=label,
            color=color,
            alpha=0.8,
            marker=marker,
            markersize=3,
            markevery=max(1, len(rounds_inv) // 10),
        )

    plt.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    plt.xlabel("Round", fontsize=12)
    plt.ylabel("Quantity (+ buy, - sell)", fontsize=12)
    plt.title("Herd Effect Simulation: Investor Trading Quantities", fontsize=14)
    plt.legend(loc="best", fontsize=9, ncol=min(3, len(investor_ids) // 2 + 1))
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()

    plt.close()


def plot_price_deviation(data: dict, output_path: str = None):
    """
    Plot 1: Price deviation from fundamental value.
    
    Shows: Market price, fundamental line, and deviation percentage.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    market_price = data["market_price"]
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Price vs Fundamental
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', linewidth=2, label=f'Fundamental Value (${FUNDAMENTAL_VALUE})')
    ax1.fill_between(rounds, prices, FUNDAMENTAL_VALUE, alpha=0.3, 
                     color='red' if prices[-1] > FUNDAMENTAL_VALUE else 'green',
                     label='Deviation Area')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Price Deviation from Fundamental Value', fontsize=14)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Deviation percentage
    deviation = calculate_price_deviation(market_price)
    dev_values = [deviation[r] for r in rounds]
    ax2.fill_between(rounds, 0, dev_values, alpha=0.5, color='steelblue')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Deviation (%)', fontsize=12)
    ax2.set_title('Price Deviation Percentage', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Add statistics annotation
    avg_dev = np.mean(dev_values)
    max_dev = max(dev_values)
    final_dev = dev_values[-1]
    stats_text = f'Avg: {avg_dev:.2f}%\nMax: {max_dev:.2f}%\nFinal: {final_dev:.2f}%'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                 fontsize=10, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_bid_convergence(data: dict, output_path: str = None):
    """
    Plot Bid Convergence Index (CV) - core emergent herding indicator.
    
    CV decreasing = bids converging = herding forming.
    """
    investor_bids = data["investor_bids"]
    market_price = data["market_price"]
    
    cv_series = calculate_bid_convergence_cv(investor_bids)
    
    if not cv_series:
        print("Not enough data for CV calculation")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Market price
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Bid Convergence Index (CV) - Emergent Herding Detection', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: CV (lower = more herding)
    cv_rounds = sorted(cv_series.keys())
    cv_values = [cv_series[r] for r in cv_rounds]
    
    ax2.fill_between(cv_rounds, 0, cv_values, alpha=0.4, color='coral')
    ax2.plot(cv_rounds, cv_values, 'coral', linewidth=1.5, label='Bid CV')
    
    # Rolling average
    if len(cv_values) >= 20:
        window = 20
        rolling_avg = np.convolve(cv_values, np.ones(window)/window, mode='valid')
        rolling_rounds = cv_rounds[window-1:]
        ax2.plot(rolling_rounds, rolling_avg, 'darkred', linewidth=2, label=f'{window}-Round MA')
    
    # Herding threshold
    ax2.axhline(y=0.05, color='green', linestyle=':', linewidth=2, 
                label='Strong Herding Threshold (CV < 0.05)')
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Coefficient of Variation (CV)', fontsize=12)
    ax2.set_title('Bid CV: Lower = Behavioral Convergence = Emergent Herding', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Statistics
    avg_cv = np.mean(cv_values)
    min_cv = min(cv_values)
    stats_text = f'Avg CV: {avg_cv:.3f}\nMin CV: {min_cv:.3f}\n(< 0.05 = Strong Herding)'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_group_consensus(data: dict, output_path: str = None):
    """
    Plot 2: Group consensus (Cross-sectional std of bids).
    
    Lower std = higher herding (investors bidding similarly).
    Inspired by LSV (1992) herding measure.
    """
    investor_bids = data["investor_bids"]
    market_price = data["market_price"]
    
    cross_std = calculate_cross_sectional_std(investor_bids)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Market price
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Market Price vs Bid Dispersion (LSV-Inspired Measure)', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Cross-sectional std (inverse herding indicator)
    std_rounds = sorted(cross_std.keys())
    std_values = [cross_std[r] for r in std_rounds]
    
    ax2.fill_between(std_rounds, 0, std_values, alpha=0.4, color='purple')
    ax2.plot(std_rounds, std_values, 'purple', linewidth=1.5, label='Bid Std Dev')
    
    # Rolling average for smoothing
    if len(std_values) >= 20:
        window = 20
        rolling_std = np.convolve(std_values, np.ones(window)/window, mode='valid')
        rolling_rounds = std_rounds[window-1:]
        ax2.plot(rolling_rounds, rolling_std, 'darkviolet', linewidth=2, label=f'{window}-Round Moving Avg')
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Bid Std Dev ($)', fontsize=12)
    ax2.set_title('Cross-Sectional Bid Dispersion (Low = High Herding)', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Add interpretation
    avg_std = np.mean(std_values)
    ax2.annotate(f'Avg Dispersion: ${avg_std:.2f}\n(Lower = More Herding)', 
                 xy=(0.98, 0.95), xycoords='axes fraction',
                 fontsize=10, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_volatility_analysis(data: dict, output_path: str = None):
    """
    Plot 3: Rolling volatility analysis.
    
    Shows if herding is associated with increased price volatility.
    """
    market_price = data["market_price"]
    
    volatility = calculate_rolling_volatility(market_price, window=10)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Price
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Price Volatility Analysis', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Volatility
    vol_rounds = sorted(volatility.keys())
    vol_values = [volatility[r] for r in vol_rounds]
    
    ax2.fill_between(vol_rounds, 0, vol_values, alpha=0.4, color='orange')
    ax2.plot(vol_rounds, vol_values, 'darkorange', linewidth=1.5, label='10-Round Rolling Volatility')
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Volatility (sigma)', fontsize=12)
    ax2.set_title('Rolling Price Volatility', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Statistics
    avg_vol = np.mean(vol_values)
    max_vol = max(vol_values)
    stats_text = f'Avg Vol: {avg_vol:.3f}\nMax Vol: {max_vol:.3f}'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                 fontsize=10, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_contagion_heatmap(data: dict, output_path: str = None):
    """
    Plot 4: Contagion effect heatmap.
    
    Shows bid deviations from market price for each investor over time.
    Red = overbidding, Blue = underbidding.
    """
    market_price = data["market_price"]
    investor_bids = data["investor_bids"]
    
    rounds = sorted(market_price.keys())
    investor_ids = sorted(investor_bids.keys())
    
    # Build heatmap matrix: deviation from market price
    n_investors = len(investor_ids)
    n_rounds = len(rounds)
    
    heatmap_data = np.zeros((n_investors, n_rounds))
    
    for i, inv_id in enumerate(investor_ids):
        bids = investor_bids[inv_id]
        for j, r in enumerate(rounds):
            if r in bids and r in market_price:
                deviation = (bids[r] - market_price[r]) / market_price[r] * 100
                heatmap_data[i, j] = deviation
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(16, 6))
    
    # Center colormap at 0
    vmax = np.abs(heatmap_data).max()
    im = ax.imshow(heatmap_data, aspect='auto', cmap='RdBu_r', vmin=-vmax, vmax=vmax)
    
    # Labels
    labels = [inv_id.replace('investor_', '').replace('_', ' ').title() for inv_id in investor_ids]
    ax.set_yticks(range(n_investors))
    ax.set_yticklabels(labels)
    
    # X-axis: show every Nth round
    step = max(1, n_rounds // 20)
    ax.set_xticks(range(0, n_rounds, step))
    ax.set_xticklabels([rounds[i] for i in range(0, n_rounds, step)])
    
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Investor', fontsize=12)
    ax.set_title('Contagion Heatmap: Bid Deviation from Market Price (Red=Overbid, Blue=Underbid)', fontsize=14)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Bid Deviation (%)', fontsize=11)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_directional_agreement(data: dict, output_path: str = None):
    """
    Plot Directional Agreement - measures behavioral alignment over time.
    
    DA > 0.8 = strong herding (all investors moving same direction).
    """
    investor_bids = data["investor_bids"]
    market_price = data["market_price"]
    
    agreement = calculate_directional_agreement(investor_bids)
    
    if not agreement:
        print("Not enough data for directional agreement")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Price
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Directional Agreement - Behavioral Alignment Detection', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Agreement
    agree_rounds = sorted(agreement.keys())
    agree_values = [agreement[r] for r in agree_rounds]
    
    ax2.fill_between(agree_rounds, 0, agree_values, alpha=0.4, color='purple')
    ax2.plot(agree_rounds, agree_values, 'purple', linewidth=1.5, label='Directional Agreement')
    
    # Herding threshold
    ax2.axhline(y=0.8, color='red', linestyle=':', linewidth=2, 
                label='Strong Herding Threshold (DA > 0.8)')
    ax2.axhline(y=0.5, color='gray', linestyle=':', linewidth=1, 
                label='Random Behavior (DA = 0.5)')
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Agreement (0-1)', fontsize=12)
    ax2.set_title('Directional Agreement: 1 = All Same Direction, 0.5 = Random', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.1)
    
    # Statistics
    avg_agree = np.mean(agree_values)
    max_agree = max(agree_values)
    pct_herding = sum(1 for v in agree_values if v > 0.8) / len(agree_values) * 100
    stats_text = f'Avg: {avg_agree:.3f}\nMax: {max_agree:.3f}\nRounds DA>0.8: {pct_herding:.1f}%'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_cascade_measure(data: dict, output_path: str = None):
    """
    Plot Information Cascade Measure - investors ignoring private signals.
    
    High cascade ratio = investors following market trend over fundamentals.
    """
    investor_bids = data["investor_bids"]
    market_price = data["market_price"]
    
    cascade = calculate_cascade_measure(investor_bids, market_price)
    
    if not cascade:
        print("Not enough data for cascade measure")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Price with fundamental deviation
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.fill_between(rounds, prices, FUNDAMENTAL_VALUE, alpha=0.3, 
                     color='red', label='Deviation')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Information Cascade Measure (Bikhchandani et al. 1992)', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Cascade ratio
    cascade_rounds = sorted(cascade.keys())
    cascade_values = [cascade[r] for r in cascade_rounds]
    
    ax2.fill_between(cascade_rounds, 0, cascade_values, alpha=0.4, color='orange')
    ax2.plot(cascade_rounds, cascade_values, 'darkorange', linewidth=1.5, 
             label='Cascade Ratio')
    
    # Cascade threshold
    ax2.axhline(y=0.6, color='red', linestyle=':', linewidth=2, 
                label='Strong Cascade (> 60%)')
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Cascade Ratio', fontsize=12)
    ax2.set_title('Cascade: Proportion of Investors Ignoring Private Signals', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.1)
    
    # Statistics
    avg_cascade = np.mean(cascade_values)
    max_cascade = max(cascade_values)
    stats_text = f'Avg: {avg_cascade:.3f}\nMax: {max_cascade:.3f}'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                fontsize=10, ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_bubble_magnitude(data: dict, output_path: str = None):
    """
    Plot: Cumulative bubble magnitude.
    
    Shows accumulated deviation from fundamental value over time.
    """
    market_price = data["market_price"]
    
    bubble = calculate_bubble_magnitude(market_price)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    bubble_vals = [bubble[r] for r in rounds]
    
    # Top: Price
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Bubble Magnitude Analysis', fontsize=14)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Cumulative bubble
    ax2.fill_between(rounds, 0, bubble_vals, alpha=0.4, 
                     color='red' if bubble_vals[-1] > 0 else 'green')
    ax2.plot(rounds, bubble_vals, 'darkred' if bubble_vals[-1] > 0 else 'darkgreen', linewidth=1.5)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Cumulative Bubble ($)', fontsize=12)
    ax2.set_title('Cumulative Price Deviation from Fundamental (Bubble Magnitude)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Statistics
    final_bubble = bubble_vals[-1]
    peak_bubble = max(bubble_vals)
    stats_text = f'Final: ${final_bubble:.1f}\nPeak: ${peak_bubble:.1f}'
    ax2.annotate(stats_text, xy=(0.98, 0.95), xycoords='axes fraction',
                 fontsize=10, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_volume_analysis(data: dict, output_path: str = None):
    """
    Plot: Volume analysis - total volume and herding volume share.
    """
    market_price = data["market_price"]
    investor_quantities = data["investor_quantities"]
    
    volume_metrics = calculate_volume_metrics(investor_quantities)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # Top: Price with volume bars
    ax1.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax1.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Volume bars on secondary axis
    ax1_vol = ax1.twinx()
    vol_rounds = sorted(volume_metrics['total_volume'].keys())
    volumes = [volume_metrics['total_volume'][r] for r in vol_rounds]
    ax1_vol.bar(vol_rounds, volumes, alpha=0.3, color='gray', label='Volume')
    ax1_vol.set_ylabel('Volume', fontsize=12, color='gray')
    ax1_vol.tick_params(axis='y', labelcolor='gray')
    ax1.set_title('Price & Volume Analysis', fontsize=14)
    
    # Bottom: Feedback investor volume share (Momentum + Aggressive)
    if volume_metrics['feedback_share']:
        share_rounds = sorted(volume_metrics['feedback_share'].keys())
        shares = [volume_metrics['feedback_share'][r] for r in share_rounds]
        
        ax2.fill_between(share_rounds, 0, shares, alpha=0.4, color='coral')
        ax2.plot(share_rounds, shares, 'coral', linewidth=1.5, label='Feedback Investors Share')
        
        ax2.set_xlabel('Round', fontsize=12)
        ax2.set_ylabel('Feedback Volume Share (%)', fontsize=12)
        ax2.set_title('Feedback Investors (Momentum + Aggressive) Volume Contribution', fontsize=12)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        # Statistics
        avg_share = np.mean(shares)
        ax2.annotate(f'Avg Share: {avg_share:.1f}%', 
                     xy=(0.98, 0.95), xycoords='axes fraction',
                     fontsize=10, ha='right', va='top',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax2.text(0.5, 0.5, 'No feedback investor data', 
                 ha='center', va='center', transform=ax2.transAxes)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_autocorrelation(data: dict, output_path: str = None):
    """
    Plot: Price return autocorrelation (momentum persistence).
    
    Higher autocorrelation = stronger momentum = herding amplification.
    """
    market_price = data["market_price"]
    
    autocorr_lag1 = calculate_autocorrelation(market_price, lag=1)
    autocorr_lag5 = calculate_autocorrelation(market_price, lag=5)
    
    if not autocorr_lag1:
        print("Not enough data for autocorrelation")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    rounds_1 = sorted(autocorr_lag1.keys())
    ac_vals_1 = [autocorr_lag1[r] for r in rounds_1]
    
    ax.plot(rounds_1, ac_vals_1, 'b-', linewidth=1.5, label='Lag-1 Autocorr')
    
    if autocorr_lag5:
        rounds_5 = sorted(autocorr_lag5.keys())
        ac_vals_5 = [autocorr_lag5[r] for r in rounds_5]
        ax.plot(rounds_5, ac_vals_5, 'r--', linewidth=1.5, label='Lag-5 Autocorr')
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.axhline(y=0.3, color='orange', linestyle=':', linewidth=1, alpha=0.7, label='Significance Threshold')
    ax.axhline(y=-0.3, color='orange', linestyle=':', linewidth=1, alpha=0.7)
    
    ax.fill_between(rounds_1, 0, ac_vals_1, alpha=0.2, color='blue')
    
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Autocorrelation', fontsize=12)
    ax.set_title('Price Return Autocorrelation (Momentum Persistence)', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1, 1)
    
    # Statistics
    avg_ac = np.mean(ac_vals_1)
    ax.annotate(f'Avg Lag-1 AC: {avg_ac:.3f}\n(>0: Momentum, <0: Mean-Reversion)', 
                xy=(0.98, 0.05), xycoords='axes fraction',
                fontsize=10, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_comprehensive_summary(data: dict, output_path: str = None):
    """
    Generate a comprehensive 2x3 summary panel of emergent herding indicators.
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    market_price = data["market_price"]
    investor_bids = data["investor_bids"]
    
    rounds = sorted(market_price.keys())
    prices = [market_price[r] for r in rounds]
    
    # 1. Price vs Fundamental (top-left)
    ax = axes[0, 0]
    ax.plot(rounds, prices, 'b-', linewidth=2, label='Market Price')
    ax.axhline(y=FUNDAMENTAL_VALUE, color='gray', linestyle='--', label='Fundamental')
    ax.fill_between(rounds, prices, FUNDAMENTAL_VALUE, alpha=0.3, color='red')
    ax.set_xlabel('Round')
    ax.set_ylabel('Price ($)')
    ax.set_title('1. Price vs Fundamental Value')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # 2. Bid Convergence CV (top-middle) - KEY EMERGENT INDICATOR
    ax = axes[0, 1]
    cv_series = calculate_bid_convergence_cv(investor_bids)
    if cv_series:
        cv_rounds = sorted(cv_series.keys())
        cv_values = [cv_series[r] for r in cv_rounds]
        ax.fill_between(cv_rounds, 0, cv_values, alpha=0.5, color='coral')
        ax.axhline(y=0.05, color='green', linestyle=':', linewidth=2)
        ax.set_title(f'2. Bid CV (Avg: {np.mean(cv_values):.3f}, Low=Herding)')
    else:
        ax.set_title('2. Bid CV (No Data)')
    ax.set_xlabel('Round')
    ax.set_ylabel('CV')
    ax.grid(True, alpha=0.3)
    
    # 3. Directional Agreement (top-right) - KEY EMERGENT INDICATOR
    ax = axes[0, 2]
    agreement = calculate_directional_agreement(investor_bids)
    if agreement:
        agree_rounds = sorted(agreement.keys())
        agree_values = [agreement[r] for r in agree_rounds]
        ax.fill_between(agree_rounds, 0, agree_values, alpha=0.5, color='purple')
        ax.axhline(y=0.8, color='red', linestyle=':', linewidth=2)
        ax.set_title(f'3. Dir. Agreement (Avg: {np.mean(agree_values):.3f})')
    else:
        ax.set_title('3. Dir. Agreement (No Data)')
    ax.set_xlabel('Round')
    ax.set_ylabel('Agreement')
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)
    
    # 4. Cross-Sectional Std (bottom-left)
    ax = axes[1, 0]
    cross_std = calculate_cross_sectional_std(investor_bids)
    std_rounds = sorted(cross_std.keys())
    std_vals = [cross_std[r] for r in std_rounds]
    ax.fill_between(std_rounds, 0, std_vals, alpha=0.5, color='steelblue')
    ax.set_xlabel('Round')
    ax.set_ylabel('Bid Std Dev ($)')
    ax.set_title(f'4. Bid Dispersion (Low=Consensus)')
    ax.grid(True, alpha=0.3)
    
    # 5. Information Cascade (bottom-middle)
    ax = axes[1, 1]
    cascade = calculate_cascade_measure(investor_bids, market_price)
    if cascade:
        cascade_rounds = sorted(cascade.keys())
        cascade_vals = [cascade[r] for r in cascade_rounds]
        ax.fill_between(cascade_rounds, 0, cascade_vals, alpha=0.5, color='orange')
        ax.axhline(y=0.6, color='red', linestyle=':', linewidth=2)
        ax.set_title(f'5. Cascade Measure (Avg: {np.mean(cascade_vals):.3f})')
    else:
        ax.set_title('5. Cascade Measure (No Data)')
    ax.set_xlabel('Round')
    ax.set_ylabel('Cascade Ratio')
    ax.set_ylim(0, 1.1)
    ax.grid(True, alpha=0.3)
    
    # 6. Bubble Magnitude (bottom-right)
    ax = axes[1, 2]
    bubble = calculate_bubble_magnitude(market_price)
    bubble_vals = [bubble[r] for r in rounds]
    color = 'red' if bubble_vals[-1] > 0 else 'green'
    ax.fill_between(rounds, 0, bubble_vals, alpha=0.5, color=color)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_xlabel('Round')
    ax.set_ylabel('Cumulative Bubble ($)')
    ax.set_title(f'6. Bubble Magnitude (Final: ${bubble_vals[-1]:.1f})')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle('Emergent Herding Analysis - No Explicit Imitator', fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def print_summary(data: dict):
    """Print comprehensive summary statistics for emergent herding analysis."""
    market_price = data["market_price"]
    investor_bids = data["investor_bids"]
    investor_quantities = data["investor_quantities"]
    rounds = sorted(market_price.keys())

    print("\n" + "=" * 70)
    print("  EMERGENT HERDING ANALYSIS - COMPREHENSIVE SUMMARY")
    print("  (No Explicit Imitator - Herding Emerges from Positive Feedback)")
    print("=" * 70)

    # Basic Market Statistics
    prices = list(market_price.values())
    print(f"\n[1] MARKET PRICE STATISTICS")
    print(f"    Initial:     ${prices[0]:.2f}")
    print(f"    Final:       ${prices[-1]:.2f}")
    print(f"    Min:         ${min(prices):.2f}")
    print(f"    Max:         ${max(prices):.2f}")
    print(f"    Mean:        ${np.mean(prices):.2f}")
    print(f"    Std Dev:     ${np.std(prices):.3f}")
    print(f"    Rounds:      {len(rounds)}")

    # Price Deviation from Fundamental
    deviation = calculate_price_deviation(market_price)
    dev_values = list(deviation.values())
    print(f"\n[2] PRICE DEVIATION (from Fundamental ${FUNDAMENTAL_VALUE})")
    print(f"    Avg Deviation:    {np.mean(dev_values):+.2f}%")
    print(f"    Max Deviation:    {max(dev_values):+.2f}%")
    print(f"    Final Deviation:  {dev_values[-1]:+.2f}%")

    # Bubble Magnitude
    bubble = calculate_bubble_magnitude(market_price)
    bubble_vals = list(bubble.values())
    print(f"\n[3] BUBBLE MAGNITUDE (Cumulative Deviation)")
    print(f"    Final Cumulative: ${bubble_vals[-1]:.1f}")
    print(f"    Peak Cumulative:  ${max(bubble_vals):.1f}")

    # Bid Convergence CV - KEY EMERGENT METRIC
    cv_series = calculate_bid_convergence_cv(investor_bids)
    if cv_series:
        cv_values = list(cv_series.values())
        print(f"\n[4] BID CONVERGENCE INDEX (CV) - Emergent Herding Indicator")
        print(f"    Avg CV:           {np.mean(cv_values):.4f}")
        print(f"    Min CV:           {min(cv_values):.4f} (max convergence)")
        print(f"    Max CV:           {max(cv_values):.4f}")
        print(f"    Interpretation:   CV < 0.05 = Strong Herding")

    # Directional Agreement - KEY EMERGENT METRIC
    agreement = calculate_directional_agreement(investor_bids)
    if agreement:
        agree_values = list(agreement.values())
        pct_herding = sum(1 for v in agree_values if v > 0.8) / len(agree_values) * 100
        print(f"\n[5] DIRECTIONAL AGREEMENT - Behavioral Alignment")
        print(f"    Avg Agreement:    {np.mean(agree_values):.4f}")
        print(f"    Max Agreement:    {max(agree_values):.4f}")
        print(f"    Rounds DA > 0.8:  {pct_herding:.1f}% (strong herding)")
        print(f"    Interpretation:   DA > 0.8 = Strong Herding")

    # Information Cascade - KEY EMERGENT METRIC
    cascade = calculate_cascade_measure(investor_bids, market_price)
    if cascade:
        cascade_values = list(cascade.values())
        print(f"\n[6] INFORMATION CASCADE MEASURE")
        print(f"    Avg Cascade:      {np.mean(cascade_values):.4f}")
        print(f"    Max Cascade:      {max(cascade_values):.4f}")
        print(f"    Interpretation:   > 0.6 = Strong Information Cascade")

    # Cross-sectional Dispersion (LSV-inspired)
    cross_std = calculate_cross_sectional_std(investor_bids)
    std_values = list(cross_std.values())
    print(f"\n[7] BID DISPERSION (LSV-Inspired Measure)")
    print(f"    Avg Dispersion:   ${np.mean(std_values):.2f}")
    print(f"    Min Dispersion:   ${min(std_values):.2f} (max consensus)")
    print(f"    Max Dispersion:   ${max(std_values):.2f}")

    # Volatility
    volatility = calculate_rolling_volatility(market_price)
    if volatility:
        vol_values = list(volatility.values())
        print(f"\n[8] PRICE VOLATILITY (10-Round Rolling)")
        print(f"    Avg Volatility:   {np.mean(vol_values):.4f}")
        print(f"    Max Volatility:   {max(vol_values):.4f}")

    # Investor Correlations
    correlations = calculate_investor_correlation_matrix(investor_bids)
    if correlations:
        print(f"\n[9] INVESTOR CORRELATIONS (Pairwise)")
        for (inv1, inv2), corr in sorted(correlations.items(), key=lambda x: -x[1])[:5]:
            label1 = inv1.replace('investor_', '').title()
            label2 = inv2.replace('investor_', '').title()
            print(f"    {label1:12s} <-> {label2:12s}: {corr:+.3f}")

    # Volume Metrics
    volume_metrics = calculate_volume_metrics(investor_quantities)
    if volume_metrics['feedback_share']:
        share_values = list(volume_metrics['feedback_share'].values())
        print(f"\n[10] FEEDBACK INVESTORS VOLUME SHARE (Momentum + Aggressive)")
        print(f"    Avg Share:        {np.mean(share_values):.1f}%")
        print(f"    Max Share:        {max(share_values):.1f}%")

    # Investor Details
    print(f"\n[11] INVESTOR SUMMARY ({len(investor_bids)} investors)")
    print(f"    {'Investor':<15s} {'Avg Bid':>10s} {'Total Qty':>12s} {'Role'}")
    print(f"    {'-'*15} {'-'*10} {'-'*12} {'-'*20}")
    for inv_id in sorted(investor_bids.keys()):
        bids = investor_bids[inv_id]
        qtys = investor_quantities[inv_id]
        avg_bid = sum(bids.values()) / len(bids)
        total_qty = sum(qtys.values())
        # Determine role in emergent model
        if "momentum" in inv_id.lower():
            role = "FEEDBACK (Primary)"
        elif "aggressive" in inv_id.lower():
            role = "FEEDBACK (Amplifier)"
        elif "contrarian" in inv_id.lower():
            role = "STABILIZER"
        elif "risk" in inv_id.lower():
            role = "EARLY EXIT"
        elif "noise" in inv_id.lower():
            role = "TRIGGER"
        else:
            role = "OTHER"
        label = inv_id.replace('investor_', '')
        print(f"    {label:<15s} ${avg_bid:>9.2f} {total_qty:>+12.2f} {role}")

    print("\n" + "=" * 70)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze HerdEffect simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to simulation config file (e.g., configs/HerdEffect/simulation.yml)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    config = load_config(args.config)
    data_dir, output_dir = get_paths_from_config(config)

    # Check if data exists
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        print("Run the simulation first:")
        print(f"  python examples/HerdEffect/run_herd.py -c {args.config}")
        return

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load and process data
    print(f"Loading messages from: {data_dir}")
    messages = load_messages(data_dir)
    print(f"Loaded {len(messages)} messages")

    data = extract_price_data(messages)

    # Print comprehensive summary
    print_summary(data)

    # Generate all charts for Emergent Herding Model
    print("\nGenerating emergent herding analysis charts...")
    
    # 1. Basic price chart
    plot_prices(data, os.path.join(output_dir, "01_price_chart.png"))
    
    # 2. Quantity chart
    plot_quantities(data, os.path.join(output_dir, "02_quantity_chart.png"))
    
    # 3. Price deviation from fundamental
    plot_price_deviation(data, os.path.join(output_dir, "03_price_deviation.png"))
    
    # 4. Bid Convergence (CV) - KEY EMERGENT INDICATOR
    plot_bid_convergence(data, os.path.join(output_dir, "04_bid_convergence.png"))
    
    # 5. Group consensus (LSV-inspired)
    plot_group_consensus(data, os.path.join(output_dir, "05_group_consensus.png"))
    
    # 6. Volatility analysis
    plot_volatility_analysis(data, os.path.join(output_dir, "06_volatility.png"))
    
    # 7. Contagion heatmap
    plot_contagion_heatmap(data, os.path.join(output_dir, "07_contagion_heatmap.png"))
    
    # 8. Directional Agreement - KEY EMERGENT INDICATOR
    plot_directional_agreement(data, os.path.join(output_dir, "08_directional_agreement.png"))
    
    # 9. Information Cascade Measure - KEY EMERGENT INDICATOR
    plot_cascade_measure(data, os.path.join(output_dir, "09_cascade_measure.png"))
    
    # 10. Bubble magnitude
    plot_bubble_magnitude(data, os.path.join(output_dir, "10_bubble_magnitude.png"))
    
    # 11. Volume analysis
    plot_volume_analysis(data, os.path.join(output_dir, "11_volume_analysis.png"))
    
    # 12. Autocorrelation (momentum persistence)
    plot_autocorrelation(data, os.path.join(output_dir, "12_autocorrelation.png"))
    
    # 13. Comprehensive summary panel
    plot_comprehensive_summary(data, os.path.join(output_dir, "00_summary_panel.png"))

    print(f"\n" + "=" * 60)
    print(f"Emergent Herding Analysis Complete!")
    print(f"All charts saved to: {output_dir}")
    print(f"=" * 60)
    print("\nGenerated charts:")
    print("  00_summary_panel.png        - Comprehensive 6-panel summary")
    print("  01_price_chart.png          - Price & investor bids")
    print("  02_quantity_chart.png       - Trading quantities")
    print("  03_price_deviation.png      - Deviation from fundamental")
    print("  04_bid_convergence.png      - Bid CV (KEY: Low = Herding)")
    print("  05_group_consensus.png      - LSV-inspired bid dispersion")
    print("  06_volatility.png           - Rolling price volatility")
    print("  07_contagion_heatmap.png    - Investor deviation heatmap")
    print("  08_directional_agreement.png- Behavioral alignment (KEY)")
    print("  09_cascade_measure.png      - Information cascade (KEY)")
    print("  10_bubble_magnitude.png     - Cumulative bubble measure")
    print("  11_volume_analysis.png      - Volume & feedback share")
    print("  12_autocorrelation.png      - Momentum persistence")


if __name__ == "__main__":
    main()
