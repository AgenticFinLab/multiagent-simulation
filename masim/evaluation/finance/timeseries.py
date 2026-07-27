"""
Core Financial Time Series Metrics

Time series analysis functions commonly used across financial simulations.
This module serves TWO roles:

  1. **Computation primitives** — pure functions (calculate_returns, calculate_sharpe_ratio,
     etc.) that accept raw arrays/dicts and return computed values.
  2. **Registry-compatible metric functions** — ``m_*`` functions with signature
     ``fn(data, config) -> dict`` that raise :class:`MetricUnavailable` on missing
     inputs. These live here because they belong to the *timeseries analytical
     method family* and share internal primitives with the computation functions.

Registry-compatible metrics in this file (23 total):
  - price_dynamics (12): price_deviation_ts, mad_pct, half_life_threshold,
    half_life_fitted, rolling_volatility_ts, mean_volatility_pct, max_drawdown_pct,
    return_skewness, return_kurtosis, return_autocorr_lag1, return_autocorr_profile,
    variance_ratio_lo_mackinlay
  - information_efficiency (5): under_revision_ratio, regime_transition_lag,
    price_efficiency_ratio, forecast_error_persistence, deviation_decay_slope
  - statistical_inference (4): mad_block_bootstrap_ci_95, half_life_block_bootstrap_ci_95,
    ljung_box_returns_pvalue, adf_unit_root_pvalue
  - tail_risk (2): value_at_risk_95, conditional_var_95

References:
    - Jegadeesh & Titman (1993): Momentum returns
    - Shiller (1981): Excess volatility
    - Sharpe (1966): Risk-adjusted returns
    - Lo & MacKinlay (1988): Variance ratios
    - Campbell & Sharpe (2009): Anchoring in financial forecasts
    - Fama & French (1988): Permanent and temporary components
    - Cont (2001): Empirical properties of asset returns
    - Politis & Romano (1994): Moving-block bootstrap
    - Ljung & Box (1978): Portmanteau test
    - Dickey & Fuller (1979): Unit root test
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np

from masim.evaluation.registry import Metric, MetricUnavailable
from masim.evaluation.data_loader import aligned_prices_and_fundamentals


# ===========================================================================
# Part I: Computation Primitives
# ===========================================================================


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
    market_prices: Dict[int, float] | np.ndarray | list, window: int = 10
) -> Dict[int, float] | np.ndarray:
    """
    Calculate rolling price volatility (standard deviation).

    Higher volatility indicates market stress or uncertainty.
    Used in volatility clustering analysis.

    Formula: σ_t = std(P_{t-window+1}, ..., P_t)

    Args:
        market_prices: {round: price} or array/list of prices
        window: Rolling window size

    Returns:
        {round: volatility} or array of volatility values
    """
    # Handle array/list input
    if isinstance(market_prices, (np.ndarray, list)):
        prices = np.array(market_prices)
        result = np.zeros(len(prices))
        for i in range(window - 1, len(prices)):
            result[i] = np.std(prices[i - window + 1 : i + 1])
        return result

    # Handle dict input
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
    market_prices: Dict[int, float] | np.ndarray | list, log_returns: bool = False
) -> Dict[int, float] | np.ndarray:
    """
    Calculate price returns (simple or log returns).

    Args:
        market_prices: {round: price} or array/list of prices
        log_returns: If True, compute log returns

    Returns:
        {round: return} (starting from round 2) or array of returns
    """
    # Handle array/list input
    if isinstance(market_prices, (np.ndarray, list)):
        prices = np.array(market_prices)
        if len(prices) < 2:
            return np.array([])
        if log_returns:
            return np.log(prices[1:] / prices[:-1])
        else:
            return np.diff(prices) / prices[:-1]

    # Handle dict input
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
        # NaN, not 0.0: a Sharpe of 0 is a valid measurement (zero excess
        # return), so it must not be reused as an "insufficient data"
        # sentinel.
        return float("nan")

    arr = np.array(returns)
    excess_return = np.mean(arr) - risk_free_rate
    std_return = np.std(arr, ddof=1)

    if std_return == 0:
        # Zero-variance returns produce a mathematically undefined Sharpe
        # (division by zero). Return NaN — using 0.0 here would falsely
        # signal "no risk-adjusted alpha" for what is actually
        # "risk-adjusted alpha is undefined".
        return float("nan")

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
        # NaN with sentinel indices: 0.0 is a valid "no drawdown observed"
        # measurement, so it must not be reused for "insufficient data".
        return float("nan"), -1, -1

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


# ===========================================================================
# Part II: Internal Helpers for Registry Metrics
# ===========================================================================


def _returns(prices: np.ndarray) -> np.ndarray:
    """Arithmetic per-round returns; raises MetricUnavailable if fewer than two prices."""
    if prices.size < 2:
        raise MetricUnavailable("need at least two prices to compute returns")
    return calculate_returns(prices)


def _log_returns(prices: np.ndarray) -> np.ndarray:
    """Log returns; raises MetricUnavailable if fewer than two prices."""
    if prices.size < 2:
        raise MetricUnavailable("need at least two prices to compute log returns")
    return calculate_returns(prices, log_returns=True)


def _half_life_threshold_impl(prices: np.ndarray, fundamental: float) -> float:
    """First round at which |deviation| <= 0.5 * |deviation_0|."""
    devs = np.abs((prices - fundamental) / fundamental)
    if devs[0] == 0:
        # Initial price already equals fundamental — half-life is undefined
        # (no deviation to decay). Returning 0.0 previously falsely reported
        # "reached half-life at round 0" and dragged the scenario mean-
        # reversion metric downward.
        raise MetricUnavailable("initial deviation is zero — half-life undefined")
    target = devs[0] / 2.0
    for idx, dev in enumerate(devs):
        if dev <= target:
            return float(idx)
    return float(prices.size)


def _block_bootstrap_indices(n: int, block: int, num: int) -> np.ndarray:
    """Generate (num, n) array of moving-block-bootstrap indices."""
    rng = np.random.default_rng(42)
    indices = np.empty((num, n), dtype=int)
    for sim in range(num):
        out = []
        while len(out) < n:
            start = rng.integers(0, n - block + 1)
            out.extend(range(start, start + block))
        indices[sim] = out[:n]
    return indices


def _chi2_sf(x: float, df: int) -> float:
    """Survival function of chi-square via regularized upper gamma."""
    if x <= 0:
        return 1.0
    return float(_gammaincc(df / 2.0, x / 2.0))


def _gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x)."""
    import math
    if x < 0 or a <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap = a
        summand = 1.0 / a
        delta = summand
        for _ in range(200):
            ap += 1.0
            delta *= x / ap
            summand += delta
            if abs(delta) < abs(summand) * 1e-12:
                break
        gamser = summand * math.exp(-x + a * math.log(x) - gln)
        return 1.0 - gamser
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 201):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def _erf(x: float) -> float:
    """Abramowitz-Stegun 7.1.26 approximation; |error| < 1.5e-7."""
    import math
    sign = 1.0 if x >= 0 else -1.0
    x_abs = abs(x)
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    t = 1.0 / (1.0 + p * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x_abs * x_abs)
    return sign * y


# ===========================================================================
# Part III: Registry-Compatible Metric Functions (m_* prefix)
# ===========================================================================

# ---------------------------------------------------------------------------
# Category: price_dynamics (12 metrics)
# ---------------------------------------------------------------------------


def m_price_deviation_ts(data, config):
    """Signed (P-F)/F deviation per round."""
    rounds, prices, funds = aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    return {
        "rounds": rounds,
        "deviation_pct": (deviations * 100).tolist(),
        "max_abs_deviation_pct": float(np.max(np.abs(deviations)) * 100),
        "final_deviation_pct": float(deviations[-1] * 100),
    }


def m_mad_pct(data, config):
    """Mean absolute deviation of price from fundamental (%)."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    return {"value_pct": float(np.mean(np.abs(deviations)) * 100)}


def m_half_life_threshold(data, config):
    """First round at which |deviation| falls below half its initial value."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    return {
        "value_rounds": _half_life_threshold_impl(prices, float(funds.mean())),
        "method": "first round at which |deviation| <= 0.5 * |deviation_0|",
    }


def m_half_life_fitted(data, config):
    """Half-life from OLS exponential decay fit on log|deviation|."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    if prices.size < 5:
        raise MetricUnavailable("need >=5 rounds for exponential fit")
    devs = np.abs((prices - funds) / funds)
    floor = max(1e-6, float(np.max(devs)) * 1e-4)
    log_devs = np.log(np.maximum(devs, floor))
    rounds_idx = np.arange(prices.size, dtype=float)
    slope, intercept = np.polyfit(rounds_idx, log_devs, 1)
    if slope >= 0 or not np.isfinite(slope):
        return {
            "value_rounds": float("nan"),
            "tau": float("nan"),
            "intercept_log_d0": float(intercept),
            "slope_per_round": float(slope),
            "method": "OLS log|deviation| vs. round; half_life = ln(2) * tau",
        }
    tau = -1.0 / float(slope)
    return {
        "value_rounds": float(np.log(2.0) * tau),
        "tau": float(tau),
        "intercept_log_d0": float(intercept),
        "slope_per_round": float(slope),
        "method": "OLS log|deviation| vs. round; half_life = ln(2) * tau",
    }


def m_rolling_volatility_ts(data, config):
    """10-round rolling std of percent returns."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    if prices.size < 2:
        raise MetricUnavailable("need >=2 prices for volatility")
    returns_pct = (np.diff(prices) / prices[:-1]) * 100
    window = 10
    vols = []
    for i in range(returns_pct.size):
        start = max(0, i - window + 1)
        vols.append(float(np.std(returns_pct[start : i + 1])))
    return {"window": window, "rolling_vol_pct": vols}


def m_mean_volatility_pct(data, config):
    """Std of full-sample percent returns."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    return {"value_pct": float(np.std(returns) * 100)}


def m_max_drawdown_pct(data, config):
    """Worst peak-to-trough percent decline."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    if prices.size < 2:
        raise MetricUnavailable("need >=2 prices for drawdown")
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        if peak > 0:
            dd = (peak - price) / peak
            if dd > worst:
                worst = dd
    return {"value_pct": float(-worst * 100)}


def m_return_skewness(data, config):
    """Sample skewness of percent returns."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 3:
        raise MetricUnavailable("need >=3 returns for skewness")
    mean = float(np.mean(returns))
    std = float(np.std(returns))
    if std < 1e-12:
        raise MetricUnavailable("zero return variance")
    skew = float(np.mean(((returns - mean) / std) ** 3))
    return {"value": skew}


def m_return_kurtosis(data, config):
    """Excess kurtosis of percent returns (0 = Gaussian)."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 4:
        raise MetricUnavailable("need >=4 returns for kurtosis")
    mean = float(np.mean(returns))
    std = float(np.std(returns))
    if std < 1e-12:
        raise MetricUnavailable("zero return variance")
    excess = float(np.mean(((returns - mean) / std) ** 4) - 3.0)
    return {"value_excess": excess}


def m_return_autocorr_lag1(data, config):
    """Lag-1 autocorrelation of percent returns."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 3:
        raise MetricUnavailable("need >=3 returns for autocorrelation")
    centered = returns - float(np.mean(returns))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    autocov = float(np.mean(centered[:-1] * centered[1:]))
    return {"value": autocov / var}


def m_return_autocorr_profile(data, config):
    """Autocorrelation at lags 1..10."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    max_lag = min(10, returns.size - 1)
    if max_lag < 1:
        raise MetricUnavailable("need >1 returns for autocorr profile")
    centered = returns - float(np.mean(returns))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    profile = []
    for lag in range(1, max_lag + 1):
        autocov = float(np.mean(centered[:-lag] * centered[lag:]))
        profile.append(autocov / var)
    return {"lags": list(range(1, max_lag + 1)), "ac_values": profile}


def m_variance_ratio_lo_mackinlay(data, config):
    """Lo & MacKinlay (1988) variance ratio test at periods 2, 4, 8."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    log_rets = _log_returns(prices)
    n = log_rets.size
    if n < 16:
        raise MetricUnavailable("need >=16 returns for variance-ratio test")
    var_1 = float(np.var(log_rets, ddof=0))
    if var_1 < 1e-18:
        raise MetricUnavailable("zero return variance")
    ratios = {}
    for q in (2, 4, 8):
        if n < q * 2:
            continue
        trimmed = log_rets[: (n // q) * q]
        agg = trimmed.reshape(-1, q).sum(axis=1)
        var_q = float(np.var(agg, ddof=0)) / q
        ratios[f"vr_q{q}"] = var_q / var_1
    if not ratios:
        raise MetricUnavailable("not enough rounds for any q")
    return {"interpretation": "1.0 = random walk; >1 momentum; <1 mean-reversion", **ratios}


# ---------------------------------------------------------------------------
# Category: information_efficiency (5 metrics)
# ---------------------------------------------------------------------------


def m_under_revision_ratio(data, config):
    """Fraction of rounds where sign(P-F) matches initial sign (sign persistence)."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    deviations = prices - funds
    initial_sign = np.sign(deviations[0])
    if initial_sign == 0:
        raise MetricUnavailable("initial deviation has zero sign")
    same_sign = float(np.mean(np.sign(deviations) == initial_sign))
    return {
        "value": same_sign,
        "interpretation": (
            "1.0 = price never crosses fundamental; <0.7 means corrective force is meaningful"
        ),
    }


def m_regime_transition_lag(data, config):
    """First round where |deviation| falls below 1% (convergence detection)."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    deviations_pct = np.abs((prices - funds) / funds) * 100
    for idx, dev in enumerate(deviations_pct):
        if dev < 1.0:
            return {"value_rounds": idx, "threshold_pct": 1.0, "reached": True}
    return {"value_rounds": int(prices.size), "threshold_pct": 1.0, "reached": False}


def m_price_efficiency_ratio(data, config):
    """Var(price_change)/Var(mispricing); 1.0 = efficient market."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    if prices.size < 10:
        raise MetricUnavailable("need >=10 rounds for efficiency ratio")
    price_changes = np.diff(prices)
    mispricing = funds[:-1] - prices[:-1]
    var_change = float(np.var(price_changes))
    var_misprice = float(np.var(mispricing))
    if var_misprice < 1e-12:
        raise MetricUnavailable("zero mispricing variance")
    return {"value": var_change / var_misprice}


def m_forecast_error_persistence(data, config):
    """Lag-1 autocorrelation of the deviation series (not returns)."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    if deviations.size < 10:
        raise MetricUnavailable("need >=10 rounds for deviation persistence")
    centered = deviations - float(np.mean(deviations))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero deviation variance")
    autocov = float(np.mean(centered[:-1] * centered[1:]))
    return {"value": autocov / var}


def m_deviation_decay_slope(data, config):
    """OLS slope of |deviation| on round number; negative = converging."""
    rounds, prices, funds = aligned_prices_and_fundamentals(data)
    if prices.size < 10:
        raise MetricUnavailable("need >=10 rounds for decay slope")
    abs_dev = np.abs((prices - funds) / funds)
    x = np.arange(abs_dev.size, dtype=float)
    slope, intercept = np.polyfit(x, abs_dev, 1)
    return {"slope_per_round": float(slope), "intercept": float(intercept)}


# ---------------------------------------------------------------------------
# Category: statistical_inference (4 metrics)
# ---------------------------------------------------------------------------


def m_mad_block_bootstrap_ci_95(data, config):
    """Moving-block bootstrap 95% CI for MAD."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for bootstrap")
    devs = np.abs((prices - funds) / funds)
    block = max(5, int(round(prices.size ** (1 / 3))))
    indices = _block_bootstrap_indices(prices.size, block, num=500)
    mad_samples = np.mean(devs[indices], axis=1) * 100
    return {
        "mean_pct": float(np.mean(mad_samples)),
        "ci95_low_pct": float(np.percentile(mad_samples, 2.5)),
        "ci95_high_pct": float(np.percentile(mad_samples, 97.5)),
        "block_length": block,
        "num_replicates": 500,
    }


def m_half_life_block_bootstrap_ci_95(data, config):
    """Moving-block bootstrap 95% CI for fitted half-life."""
    _, prices, funds = aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for bootstrap")
    devs = np.abs((prices - funds) / funds)
    floor = max(1e-6, float(np.max(devs)) * 1e-4)
    log_devs = np.log(np.maximum(devs, floor))
    rounds_idx = np.arange(prices.size, dtype=float)
    block = max(5, int(round(prices.size ** (1 / 3))))
    indices = _block_bootstrap_indices(prices.size, block, num=500)
    halves = []
    for sample_idx in indices:
        slope, _ = np.polyfit(rounds_idx, log_devs[sample_idx], 1)
        if slope >= 0 or not np.isfinite(slope):
            continue
        halves.append(float(np.log(2.0) / -slope))
    if len(halves) < 50:
        raise MetricUnavailable("insufficient bootstrap samples produced finite half-life")
    halves_arr = np.asarray(halves)
    return {
        "mean_rounds": float(np.mean(halves_arr)),
        "ci95_low_rounds": float(np.percentile(halves_arr, 2.5)),
        "ci95_high_rounds": float(np.percentile(halves_arr, 97.5)),
        "valid_replicates": len(halves),
        "block_length": block,
    }


def m_ljung_box_returns_pvalue(data, config):
    """Ljung-Box Q-statistic at lag 10; null = no autocorrelation."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    n = returns.size
    if n < 20:
        raise MetricUnavailable("need >=20 returns for Ljung-Box")
    mean = float(np.mean(returns))
    centered = returns - mean
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    max_lag = 10
    q_stat = 0.0
    for lag in range(1, max_lag + 1):
        autocov = float(np.mean(centered[:-lag] * centered[lag:]))
        rho = autocov / var
        q_stat += rho * rho / (n - lag)
    q_stat *= n * (n + 2)
    p_value = _chi2_sf(q_stat, df=max_lag)
    return {
        "q_statistic": q_stat,
        "max_lag": max_lag,
        "p_value": float(p_value),
    }


def m_adf_unit_root_pvalue(data, config):
    """ADF(0) unit-root statistic on price series."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for ADF")
    delta_p = np.diff(prices)
    p_lag = prices[:-1]
    x = np.column_stack([np.ones_like(p_lag), p_lag])
    beta, _residuals, _rank, _sv = np.linalg.lstsq(x, delta_p, rcond=None)
    fitted = x @ beta
    resid = delta_p - fitted
    n = delta_p.size
    sigma2 = float(np.sum(resid * resid)) / max(n - 2, 1)
    xtx_inv = np.linalg.inv(x.T @ x)
    se_beta1 = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
    if se_beta1 < 1e-12:
        raise MetricUnavailable("ADF standard error degenerate")
    t_stat = float(beta[1] / se_beta1)
    p_value = 0.5 * (1.0 + _erf(t_stat / np.sqrt(2.0)))
    return {"t_statistic": t_stat, "approx_p_value": float(p_value)}


# ---------------------------------------------------------------------------
# Category: tail_risk (2 metrics)
# ---------------------------------------------------------------------------


def m_value_at_risk_95(data, config):
    """5th percentile of per-round returns (left tail risk)."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 20:
        raise MetricUnavailable("need >=20 returns for VaR")
    var_95 = float(np.percentile(returns * 100, 5.0))
    return {"value_pct": var_95}


def m_conditional_var_95(data, config):
    """Mean of returns below VaR-95 (expected shortfall)."""
    _, prices, _ = aligned_prices_and_fundamentals(data)
    returns = _returns(prices) * 100
    if returns.size < 20:
        raise MetricUnavailable("need >=20 returns for CVaR")
    threshold = float(np.percentile(returns, 5.0))
    tail = returns[returns <= threshold]
    if tail.size == 0:
        raise MetricUnavailable("no returns below VaR threshold")
    return {"value_pct": float(np.mean(tail)), "var_95_pct": threshold, "n_tail_obs": int(tail.size)}


# ===========================================================================
# Part IV: Metric Definitions for Registry Registration
# ===========================================================================


TIMESERIES_METRICS: List[Metric] = [
    # price_dynamics (12)
    Metric(name="price_deviation_ts", category="price_dynamics", fn=m_price_deviation_ts,
           output_keys=("rounds", "deviation_pct", "max_abs_deviation_pct", "final_deviation_pct"),
           references=("Campbell & Sharpe (2009)",), description="Signed (P-F)/F deviation per round."),
    Metric(name="mad_pct", category="price_dynamics", fn=m_mad_pct,
           output_keys=("value_pct",), references=("Campbell & Sharpe (2009)",),
           description="Time-averaged |deviation|; primary mispricing magnitude."),
    Metric(name="half_life_threshold", category="price_dynamics", fn=m_half_life_threshold,
           output_keys=("value_rounds", "method"), references=("Campbell & Sharpe (2009)",),
           description="First round at which |deviation| falls below half its initial value."),
    Metric(name="half_life_fitted", category="price_dynamics", fn=m_half_life_fitted,
           output_keys=("value_rounds", "tau", "intercept_log_d0", "slope_per_round", "method"),
           references=("Fama & French (1988)", "Campbell & Sharpe (2009)"),
           description="Half-life from OLS exponential decay fit on log|deviation|."),
    Metric(name="rolling_volatility_ts", category="price_dynamics", fn=m_rolling_volatility_ts,
           output_keys=("window", "rolling_vol_pct"), references=("Andersen et al. (2003)",),
           description="10-round rolling std of percent returns."),
    Metric(name="mean_volatility_pct", category="price_dynamics", fn=m_mean_volatility_pct,
           output_keys=("value_pct",), references=("Black (1986)",),
           description="Std of full-sample percent returns."),
    Metric(name="max_drawdown_pct", category="price_dynamics", fn=m_max_drawdown_pct,
           output_keys=("value_pct",), references=("Northcraft & Neale (1987)",),
           description="Worst peak-to-trough percent decline."),
    Metric(name="return_skewness", category="price_dynamics", fn=m_return_skewness,
           output_keys=("value",), references=("Cont (2001)",),
           description="Sample skewness of percent returns."),
    Metric(name="return_kurtosis", category="price_dynamics", fn=m_return_kurtosis,
           output_keys=("value_excess",), references=("Cont (2001)",),
           description="Excess kurtosis of percent returns (0 = Gaussian)."),
    Metric(name="return_autocorr_lag1", category="price_dynamics", fn=m_return_autocorr_lag1,
           output_keys=("value",), references=("Lo & MacKinlay (1988)",),
           description="Lag-1 autocorrelation of percent returns."),
    Metric(name="return_autocorr_profile", category="price_dynamics", fn=m_return_autocorr_profile,
           output_keys=("lags", "ac_values"), references=("Lo & MacKinlay (1988)",),
           description="Autocorrelation at lags 1..10."),
    Metric(name="variance_ratio_lo_mackinlay", category="price_dynamics", fn=m_variance_ratio_lo_mackinlay,
           output_keys=("interpretation",), references=("Lo & MacKinlay (1988)",),
           description="Variance ratios at periods 2/4/8 — random walk test."),
    # information_efficiency (5)
    Metric(name="under_revision_ratio", category="information_efficiency", fn=m_under_revision_ratio,
           output_keys=("value", "interpretation"), references=("Campbell & Sharpe (2009)",),
           description="Sign persistence of (P-F); fraction of rounds matching initial sign."),
    Metric(name="regime_transition_lag", category="information_efficiency", fn=m_regime_transition_lag,
           output_keys=("value_rounds", "threshold_pct", "reached"), references=("Campbell & Sharpe (2009)",),
           description="First round where |deviation| < 1%."),
    Metric(name="price_efficiency_ratio", category="information_efficiency", fn=m_price_efficiency_ratio,
           output_keys=("value",), references=("Fama (1970)",),
           description="Var(price_change)/Var(mispricing); 1.0 = efficient."),
    Metric(name="forecast_error_persistence", category="information_efficiency", fn=m_forecast_error_persistence,
           output_keys=("value",), references=("Campbell & Sharpe (2009)",),
           description="Lag-1 autocorrelation of deviation series."),
    Metric(name="deviation_decay_slope", category="information_efficiency", fn=m_deviation_decay_slope,
           output_keys=("slope_per_round", "intercept"), references=("Fama & French (1988)",),
           description="OLS slope of |deviation| on round number; negative = converging."),
    # statistical_inference (4)
    Metric(name="mad_block_bootstrap_ci_95", category="statistical_inference", fn=m_mad_block_bootstrap_ci_95,
           output_keys=("mean_pct", "ci95_low_pct", "ci95_high_pct", "block_length", "num_replicates"),
           references=("Politis & Romano (1994)",), description="Moving-block bootstrap 95% CI for MAD."),
    Metric(name="half_life_block_bootstrap_ci_95", category="statistical_inference", fn=m_half_life_block_bootstrap_ci_95,
           output_keys=("mean_rounds", "ci95_low_rounds", "ci95_high_rounds", "valid_replicates", "block_length"),
           references=("Politis & Romano (1994)",), description="Moving-block bootstrap 95% CI for half-life."),
    Metric(name="ljung_box_returns_pvalue", category="statistical_inference", fn=m_ljung_box_returns_pvalue,
           output_keys=("q_statistic", "max_lag", "p_value"), references=("Ljung & Box (1978)",),
           description="Q-statistic for return autocorrelation up to lag 10."),
    Metric(name="adf_unit_root_pvalue", category="statistical_inference", fn=m_adf_unit_root_pvalue,
           output_keys=("t_statistic", "approx_p_value"), references=("Dickey & Fuller (1979)",),
           description="ADF(0) unit-root statistic on price series."),
    # tail_risk (2)
    Metric(name="value_at_risk_95", category="tail_risk", fn=m_value_at_risk_95,
           output_keys=("value_pct",), references=("Jorion (2006)",),
           description="5th percentile of per-round returns (left tail)."),
    Metric(name="conditional_var_95", category="tail_risk", fn=m_conditional_var_95,
           output_keys=("value_pct", "var_95_pct", "n_tail_obs"), references=("Artzner et al. (1999)",),
           description="Mean of returns below VaR-95 (expected shortfall)."),
]
