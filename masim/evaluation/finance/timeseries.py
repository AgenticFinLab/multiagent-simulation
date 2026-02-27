"""
Core Financial Time Series Metrics

Time series analysis functions commonly used across financial simulations.
Based on standard quantitative finance literature.

References:
    - Jegadeesh & Titman (1993): Momentum returns
    - Shiller (1981): Excess volatility
    - Sharpe (1966): Risk-adjusted returns
"""

from typing import Dict, List, Tuple
import numpy as np


def calculate_autocorrelation(
    series: List[float], max_lag: int = 20, as_dict: bool = False
) -> List[float]:
    """
    Calculate autocorrelation function (ACF) for a time series.

    Used to detect:
        - Momentum persistence (positive ACF at short lags)
        - Mean reversion (negative ACF)
        - Random walk (ACF ≈ 0)

    Args:
        series: Time series data
        max_lag: Maximum lag to compute
        as_dict: If True, return {lag: acf_value}

    Returns:
        List of autocorrelation coefficients for lags 1 to max_lag
    """
    if len(series) < max_lag + 1:
        return [] if not as_dict else {}

    arr = np.array(series)
    mean = np.mean(arr)
    var = np.var(arr)

    if var == 0:
        return (
            [0.0] * max_lag if not as_dict else {i: 0.0 for i in range(1, max_lag + 1)}
        )

    acf = []
    for lag in range(1, max_lag + 1):
        if len(arr) - lag < 1:
            break
        cov = np.mean((arr[lag:] - mean) * (arr[:-lag] - mean))
        acf.append(cov / var)

    if as_dict:
        return {i + 1: v for i, v in enumerate(acf)}
    return acf


def calculate_rolling_volatility(
    market_prices: Dict[int, float], window: int = 10
) -> Dict[int, float]:
    """
    Calculate rolling price volatility (standard deviation).

    Higher volatility indicates market stress or uncertainty.
    Used in volatility clustering analysis.

    Formula: σ_t = std(P_{t-window+1}, ..., P_t)

    Args:
        market_prices: {round: price}
        window: Rolling window size

    Returns:
        {round: volatility}
    """
    rounds = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds]

    volatility = {}
    for i, r in enumerate(rounds):
        if i >= window - 1:
            window_prices = prices[i - window + 1 : i + 1]
            volatility[r] = float(np.std(window_prices))
    return volatility


def calculate_price_deviation(
    market_prices: Dict[int, float], fundamental: float
) -> Dict[int, float]:
    """
    Calculate price deviation from fundamental value.

    Positive deviation = overvaluation (potential bubble)
    Negative deviation = undervaluation (potential opportunity)

    Formula: deviation_t = (P_t - F) / F × 100%

    Args:
        market_prices: {round: price}
        fundamental: Fundamental/intrinsic value

    Returns:
        {round: deviation_percentage}
    """
    deviation = {}
    for r, price in market_prices.items():
        deviation[r] = (price - fundamental) / fundamental * 100
    return deviation


def calculate_returns(
    market_prices: Dict[int, float], log_returns: bool = False
) -> Dict[int, float]:
    """
    Calculate price returns (simple or log returns).

    Args:
        market_prices: {round: price}
        log_returns: If True, compute log returns

    Returns:
        {round: return} (starting from round 2)
    """
    rounds = sorted(market_prices.keys())
    returns = {}

    for i in range(1, len(rounds)):
        r_curr, r_prev = rounds[i], rounds[i - 1]
        p_curr, p_prev = market_prices[r_curr], market_prices[r_prev]

        if p_prev > 0:
            if log_returns:
                returns[r_curr] = float(np.log(p_curr / p_prev))
            else:
                returns[r_curr] = (p_curr - p_prev) / p_prev

    return returns


def calculate_sharpe_ratio(
    returns: List[float], risk_free_rate: float = 0.0, annualization_factor: float = 252
) -> float:
    """
    Calculate Sharpe Ratio for risk-adjusted performance.

    Formula: SR = (μ_r - r_f) / σ_r × √T

    Args:
        returns: List of period returns
        risk_free_rate: Risk-free rate (per period)
        annualization_factor: Periods per year (252 for daily)

    Returns:
        Annualized Sharpe Ratio
    """
    if len(returns) < 2:
        return 0.0

    arr = np.array(returns)
    excess_return = np.mean(arr) - risk_free_rate
    std_return = np.std(arr, ddof=1)

    if std_return == 0:
        return 0.0

    return float(excess_return / std_return * np.sqrt(annualization_factor))


def calculate_max_drawdown(prices: List[float]) -> Tuple[float, int, int]:
    """
    Calculate maximum drawdown and its timing.

    Drawdown = peak-to-trough decline during the period.

    Args:
        prices: List of prices in chronological order

    Returns:
        (max_drawdown_pct, peak_idx, trough_idx)
    """
    if len(prices) < 2:
        return 0.0, 0, 0

    arr = np.array(prices)
    running_max = np.maximum.accumulate(arr)
    drawdowns = (arr - running_max) / running_max * 100

    trough_idx = int(np.argmin(drawdowns))
    peak_idx = int(np.argmax(arr[: trough_idx + 1])) if trough_idx > 0 else 0
    max_drawdown = float(drawdowns[trough_idx])

    return max_drawdown, peak_idx, trough_idx


def calculate_rolling_autocorrelation(
    market_prices: Dict[int, float], lag: int = 1, window: int = 20
) -> Dict[int, float]:
    """
    Calculate rolling return autocorrelation (momentum persistence).

    Higher autocorrelation = stronger momentum = potential herding.

    Args:
        market_prices: {round: price}
        lag: Autocorrelation lag
        window: Rolling window size

    Returns:
        {round: autocorrelation}
    """
    rounds = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds]

    # Calculate returns
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i - 1]) / prices[i - 1] if prices[i - 1] > 0 else 0
        returns.append(ret)

    if len(returns) < lag + window:
        return {}

    autocorr = {}
    for i in range(window - 1, len(returns)):
        r = rounds[i + 1]  # Offset due to returns calculation
        window_returns = returns[i - window + 1 : i + 1]

        if len(window_returns) >= lag + 2:
            series = np.array(window_returns)
            if len(series) > lag:
                corr = np.corrcoef(series[:-lag], series[lag:])[0, 1]
                if not np.isnan(corr):
                    autocorr[r] = float(corr)

    return autocorr
