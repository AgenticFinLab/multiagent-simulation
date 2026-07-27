"""
GARCH/Volatility Clustering Metrics

Functions to detect and measure volatility clustering patterns.
Based on GARCH econometric theory and stylized facts of financial returns.

References:
    - Bollerslev (1986): GARCH model
    - Engle (1982): ARCH model
    - Cont (2001): Stylized facts of asset returns

Key Stylized Fact (GARCH Signature):
    - Returns are approximately uncorrelated
    - Squared returns show significant positive autocorrelation
    - This indicates volatility clustering: high vol → high vol, low vol → low vol

GARCH(1,1) Model:
    σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}

    Stationarity condition: α + β < 1
    Persistence: α + β (higher = slower mean reversion)
"""

from typing import Dict, List, Any
import numpy as np


def calculate_volatility_persistence(
    volatility: Dict[int, float], max_lag: int = 10
) -> Dict[str, float]:
    """
    Calculate volatility persistence metrics.

    High persistence indicates GARCH-like behavior where
    volatility shocks decay slowly over time.

    Args:
        volatility: {round: volatility_value}
        max_lag: Maximum lag for autocorrelation

    Returns:
        {
            'vol_autocorr_1': First-order autocorrelation of volatility,
            'vol_autocorr_5': 5th-order autocorrelation,
            'half_life': Estimated half-life of volatility shocks (in rounds)
        }
    """
    if len(volatility) < max_lag + 1:
        # Insufficient data: return NaN rather than 0.0 to avoid confusing
        # "not enough samples" with "measured zero autocorrelation".
        nan = float("nan")
        return {"vol_autocorr_1": nan, "vol_autocorr_5": nan, "half_life": nan}

    vol_series = [volatility[r] for r in sorted(volatility.keys())]
    acf = _calculate_acf(vol_series, max_lag=max_lag)

    vol_autocorr_1 = acf[0] if len(acf) > 0 else 0.0
    vol_autocorr_5 = acf[4] if len(acf) > 4 else 0.0

    # Estimate half-life: t_half = -ln(2) / ln(ρ)
    if 0 < vol_autocorr_1 < 1:
        half_life = -np.log(2) / np.log(vol_autocorr_1)
    else:
        half_life = float("inf")

    return {
        "vol_autocorr_1": float(vol_autocorr_1),
        "vol_autocorr_5": float(vol_autocorr_5),
        "half_life": float(half_life),
    }


def calculate_return_clustering(
    returns: Dict[int, float], max_lag: int = 5
) -> Dict[str, float]:
    """
    Test for volatility clustering via squared returns.

    GARCH Signature:
        - Returns are uncorrelated (efficient market)
        - Squared returns are correlated (volatility clustering)

    Args:
        returns: {round: return_value}
        max_lag: Maximum lag for autocorrelation

    Returns:
        {
            'return_autocorr_1': First-order autocorrelation of returns,
            'sq_return_autocorr_1': First-order autocorr of squared returns,
            'clustering_ratio': sq_return_autocorr / |return_autocorr| + 0.01
        }
    """
    if len(returns) < max_lag + 5:
        nan = float("nan")
        return {
            "return_autocorr_1": nan,
            "sq_return_autocorr_1": nan,
            "clustering_ratio": nan,
        }

    return_series = [returns[r] for r in sorted(returns.keys())]
    sq_return_series = [r**2 for r in return_series]

    return_acf = _calculate_acf(return_series, max_lag=max_lag)
    sq_return_acf = _calculate_acf(sq_return_series, max_lag=max_lag)

    return_autocorr_1 = return_acf[0] if len(return_acf) > 0 else 0.0
    sq_return_autocorr_1 = sq_return_acf[0] if len(sq_return_acf) > 0 else 0.0

    # Clustering ratio: sq_return_autocorr should be much higher than return_autocorr
    clustering_ratio = sq_return_autocorr_1 / (abs(return_autocorr_1) + 0.01)

    return {
        "return_autocorr_1": float(return_autocorr_1),
        "sq_return_autocorr_1": float(sq_return_autocorr_1),
        "clustering_ratio": float(clustering_ratio),
    }


def detect_volatility_regimes(
    volatility: Dict[int, float], threshold_multiplier: float = 1.5
) -> Dict[str, Any]:
    """
    Detect high/low volatility regimes.

    Identifies periods of sustained high or low volatility,
    which is characteristic of volatility clustering.

    Args:
        volatility: {round: volatility_value}
        threshold_multiplier: Multiplier for regime thresholds

    Returns:
        {
            'avg_vol': Average volatility,
            'high_vol_episodes': [(start, end), ...] for high vol periods,
            'low_vol_episodes': [(start, end), ...] for low vol periods,
            'regime_persistence': Average length of regimes
        }
    """
    if len(volatility) < 5:
        return {
            "avg_vol": float("nan"),
            "high_vol_episodes": [],
            "low_vol_episodes": [],
            "regime_persistence": float("nan"),
        }

    rounds = sorted(volatility.keys())
    vol_series = [volatility[r] for r in rounds]
    avg_vol = float(np.mean(vol_series))

    high_threshold = avg_vol * threshold_multiplier
    low_threshold = avg_vol / threshold_multiplier

    high_episodes = []
    low_episodes = []

    current_regime = "normal"
    regime_start = rounds[0]

    for i, (r, v) in enumerate(zip(rounds, vol_series)):
        if v > high_threshold and current_regime != "high":
            if current_regime == "low" and i > 0:
                low_episodes.append((regime_start, rounds[i - 1]))
            current_regime = "high"
            regime_start = r
        elif v < low_threshold and current_regime != "low":
            if current_regime == "high" and i > 0:
                high_episodes.append((regime_start, rounds[i - 1]))
            current_regime = "low"
            regime_start = r
        elif low_threshold <= v <= high_threshold and current_regime != "normal":
            if current_regime == "high" and i > 0:
                high_episodes.append((regime_start, rounds[i - 1]))
            elif current_regime == "low" and i > 0:
                low_episodes.append((regime_start, rounds[i - 1]))
            current_regime = "normal"
            regime_start = r

    # Handle final regime
    if current_regime == "high":
        high_episodes.append((regime_start, rounds[-1]))
    elif current_regime == "low":
        low_episodes.append((regime_start, rounds[-1]))

    # Calculate average regime length
    all_episodes = high_episodes + low_episodes
    if all_episodes:
        regime_lengths = [e[1] - e[0] + 1 for e in all_episodes]
        regime_persistence = float(np.mean(regime_lengths))
    else:
        regime_persistence = 0.0

    return {
        "avg_vol": avg_vol,
        "high_vol_episodes": high_episodes,
        "low_vol_episodes": low_episodes,
        "regime_persistence": regime_persistence,
    }


def calculate_garch_signature(market_prices: Dict[int, float]) -> Dict[str, Any]:
    """
    Comprehensive GARCH signature test.

    Tests whether the price series exhibits GARCH-like behavior:
    1. Returns approximately uncorrelated
    2. Squared returns positively autocorrelated
    3. Volatility shows persistence

    Args:
        market_prices: {round: price}

    Returns:
        {
            'has_garch_signature': bool,
            'return_acf': [...],
            'sq_return_acf': [...],
            'interpretation': str
        }
    """
    rounds = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds]

    if len(prices) < 20:
        return {
            "has_garch_signature": False,
            "return_acf": [],
            "sq_return_acf": [],
            "interpretation": "Insufficient data",
        }

    # Calculate returns
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])

    sq_returns = [r**2 for r in returns]

    return_acf = _calculate_acf(returns, max_lag=10)
    sq_return_acf = _calculate_acf(sq_returns, max_lag=10)

    # GARCH signature test
    # Returns should be near zero autocorrelation
    return_near_zero = abs(return_acf[0]) < 0.15 if return_acf else True
    # Squared returns should have positive autocorrelation
    sq_return_positive = sq_return_acf[0] > 0.1 if sq_return_acf else False

    has_signature = return_near_zero and sq_return_positive

    # Generate interpretation
    if has_signature:
        interpretation = (
            "STRONG volatility clustering detected! "
            "Returns uncorrelated but squared returns correlated → GARCH effect"
        )
    elif sq_return_positive:
        interpretation = "MODERATE volatility clustering"
    else:
        interpretation = "Weak or no volatility clustering"

    return {
        "has_garch_signature": has_signature,
        "return_acf": [float(x) for x in return_acf],
        "sq_return_acf": [float(x) for x in sq_return_acf],
        "interpretation": interpretation,
    }


def _calculate_acf(series: List[float], max_lag: int = 20) -> List[float]:
    """Calculate autocorrelation function for a time series."""
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
