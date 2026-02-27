"""
Volume and Market Impact Metrics

Functions to analyze trading volume and market impact patterns.
Used to measure agent influence and detect bubble/crash dynamics.

References:
    - Kyle (1985): Market impact model
    - Grossman & Stiglitz (1980): Informed trading
    - Shiller (2000): Bubble dynamics
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import numpy as np


def calculate_volume_metrics(
    investor_quantities: Dict[str, Dict[int, float]],
) -> Dict[str, Dict[int, float]]:
    """
    Calculate volume metrics per round.

    Tracks:
    - Total volume (market activity level)
    - Buy/Sell ratio (directional bias)
    - Feedback investor share (for emergent herding analysis)

    Args:
        investor_quantities: {investor_id: {round: quantity}}

    Returns:
        {
            'total_volume': {round: vol},
            'buy_ratio': {round: ratio},
            'sell_ratio': {round: ratio},
            'net_flow': {round: net}
        }
    """
    all_rounds = set()
    for qtys in investor_quantities.values():
        all_rounds.update(qtys.keys())

    total_volume = {}
    buy_ratio = {}
    sell_ratio = {}
    net_flow = {}

    for r in sorted(all_rounds):
        buy_vol = 0.0
        sell_vol = 0.0
        net = 0.0

        for _, qtys in investor_quantities.items():
            if r in qtys:
                qty = qtys[r]
                net += qty
                if qty > 0:
                    buy_vol += qty
                elif qty < 0:
                    sell_vol += abs(qty)

        total = buy_vol + sell_vol
        total_volume[r] = total
        buy_ratio[r] = buy_vol / total if total > 0 else 0.5
        sell_ratio[r] = sell_vol / total if total > 0 else 0.5
        net_flow[r] = net

    return {
        "total_volume": total_volume,
        "buy_ratio": buy_ratio,
        "sell_ratio": sell_ratio,
        "net_flow": net_flow,
    }


def calculate_agent_impact(
    round_orders: Dict[int, List[Dict]],
    market_returns: Optional[Dict[int, float]] = None,
    investor_strategy: Optional[Dict[str, str]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Analyze trading impact by strategy type.

    Measures the market footprint of different investor strategies.

    Args:
        round_orders: {round: [{investor, quantity, strategy, ...}, ...]}
        market_returns: {round: return} (optional, for correlation analysis)
        investor_strategy: {investor_id: strategy} (optional)

    Returns:
        {
            strategy_name: {
                'total_volume': float,
                'net_direction': float,
                'avg_trade_size': float,
                'trade_count': int
            }
        }
    """
    strategy_volume = defaultdict(float)
    strategy_directional = defaultdict(float)
    strategy_count = defaultdict(int)

    for _, orders in round_orders.items():
        for order in orders:
            strategy = order["strategy"]
            qty = order["quantity"]
            strategy_volume[strategy] += abs(qty)
            strategy_directional[strategy] += qty
            strategy_count[strategy] += 1

    impact = {}
    for strategy in strategy_volume.keys():
        impact[strategy] = {
            "total_volume": float(strategy_volume[strategy]),
            "net_direction": float(strategy_directional[strategy]),
            "avg_trade_size": float(
                strategy_volume[strategy] / max(strategy_count[strategy], 1)
            ),
            "trade_count": int(strategy_count[strategy]),
        }

    return impact


def calculate_bubble_magnitude(
    market_prices: Dict[int, float], fundamental: float
) -> Dict[int, float]:
    """
    Calculate cumulative bubble magnitude.

    Tracks the accumulated deviation from fundamental value.
    Positive values indicate bubble buildup, negative indicates crash.

    Formula: bubble_t = Σ(P_s - F) for s=1 to t

    Args:
        market_prices: {round: price}
        fundamental: Fundamental value

    Returns:
        {round: cumulative_bubble}
    """
    rounds = sorted(market_prices.keys())
    cumsum = 0.0
    bubble = {}

    for r in rounds:
        cumsum += market_prices[r] - fundamental
        bubble[r] = cumsum

    return bubble


def calculate_net_demand(
    investor_quantities: Dict[str, Dict[int, float]],
) -> Dict[int, float]:
    """
    Calculate net demand per round.

    Positive = excess demand (upward price pressure)
    Negative = excess supply (downward price pressure)

    Args:
        investor_quantities: {investor_id: {round: quantity}}

    Returns:
        {round: net_demand}
    """
    all_rounds = set()
    for qtys in investor_quantities.values():
        all_rounds.update(qtys.keys())

    net_demand = {}
    for r in sorted(all_rounds):
        total = 0.0
        for qtys in investor_quantities.values():
            if r in qtys:
                total += qtys[r]
        net_demand[r] = total

    return net_demand


def calculate_strategy_contribution(
    round_orders: Dict[int, List[Dict]], market_prices: Dict[int, float]
) -> Dict[str, Dict[str, float]]:
    """
    Calculate each strategy's contribution to price movement.

    Measures how much each strategy type contributes to:
    - Bubble formation (buying during price rises)
    - Crash acceleration (selling during price falls)
    - Stabilization (contrarian behavior)

    Args:
        round_orders: {round: [{investor, quantity, strategy, ...}, ...]}
        market_prices: {round: price}

    Returns:
        {
            strategy: {
                'pro_bubble': float,  # Buy when price rising
                'pro_crash': float,   # Sell when price falling
                'stabilizing': float  # Contrarian trades
            }
        }
    """
    rounds = sorted(market_prices.keys())

    # Calculate returns
    returns = {}
    for i in range(1, len(rounds)):
        r_curr, r_prev = rounds[i], rounds[i - 1]
        if market_prices[r_prev] > 0:
            returns[r_curr] = (
                market_prices[r_curr] - market_prices[r_prev]
            ) / market_prices[r_prev]

    strategy_pro_bubble = defaultdict(float)
    strategy_pro_crash = defaultdict(float)
    strategy_stabilizing = defaultdict(float)

    for r, orders in round_orders.items():
        if r not in returns:
            continue

        ret = returns[r]

        for order in orders:
            strategy = order["strategy"]
            qty = order["quantity"]

            if ret > 0.01:  # Rising market
                if qty > 0:  # Buying in rising market → pro-bubble
                    strategy_pro_bubble[strategy] += abs(qty)
                else:  # Selling in rising market → stabilizing
                    strategy_stabilizing[strategy] += abs(qty)
            elif ret < -0.01:  # Falling market
                if qty < 0:  # Selling in falling market → pro-crash
                    strategy_pro_crash[strategy] += abs(qty)
                else:  # Buying in falling market → stabilizing
                    strategy_stabilizing[strategy] += abs(qty)

    # Compile results
    all_strategies = (
        set(strategy_pro_bubble.keys())
        | set(strategy_pro_crash.keys())
        | set(strategy_stabilizing.keys())
    )

    contribution = {}
    for strategy in all_strategies:
        total = (
            strategy_pro_bubble[strategy]
            + strategy_pro_crash[strategy]
            + strategy_stabilizing[strategy]
        )

        if total > 0:
            contribution[strategy] = {
                "pro_bubble": float(strategy_pro_bubble[strategy] / total),
                "pro_crash": float(strategy_pro_crash[strategy] / total),
                "stabilizing": float(strategy_stabilizing[strategy] / total),
            }
        else:
            contribution[strategy] = {
                "pro_bubble": 0.0,
                "pro_crash": 0.0,
                "stabilizing": 0.0,
            }

    return contribution


def calculate_liquidity_metrics(
    round_orders: Dict[int, List[Dict]], market_prices: Dict[int, float]
) -> Dict[str, Dict[int, float]]:
    """
    Calculate liquidity-related metrics.

    Tracks market liquidity proxies:
    - Order depth (number of active orders)
    - Spread proxy (bid-ask spread approximation)
    - Price impact (return per unit volume)

    Args:
        round_orders: {round: [{investor, quantity, price, ...}, ...]}
        market_prices: {round: price}

    Returns:
        {
            'order_depth': {round: count},
            'avg_order_size': {round: avg_size},
            'price_impact': {round: impact}
        }
    """
    rounds = sorted(market_prices.keys())

    order_depth = {}
    avg_order_size = {}
    price_impact = {}

    # Calculate returns for price impact
    returns = {}
    for i in range(1, len(rounds)):
        r_curr, r_prev = rounds[i], rounds[i - 1]
        if market_prices[r_prev] > 0:
            returns[r_curr] = (
                market_prices[r_curr] - market_prices[r_prev]
            ) / market_prices[r_prev]

    for r in rounds:
        orders = round_orders[r]
        active_orders = [o for o in orders if o["quantity"] != 0]

        order_depth[r] = len(active_orders)

        if active_orders:
            sizes = [abs(o["quantity"]) for o in active_orders]
            avg_order_size[r] = float(np.mean(sizes))

            # Price impact = return / volume
            total_vol = sum(sizes)
            if r in returns and total_vol > 0:
                price_impact[r] = abs(returns[r]) / total_vol * 100
            else:
                price_impact[r] = 0.0
        else:
            avg_order_size[r] = 0.0
            price_impact[r] = 0.0

    return {
        "order_depth": order_depth,
        "avg_order_size": avg_order_size,
        "price_impact": price_impact,
    }
