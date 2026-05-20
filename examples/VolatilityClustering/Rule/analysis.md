# VolatilityClustering Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic volatility persistence, trend amplification, slow
adaptation, volatility-regime trading, and fundamental stabilization.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Rolling Volatility | `compute_rolling_volatility()` | `analysis-bases.md §2.1` | Time-varying volatility |
| Volatility Autocorrelation | `compute_volatility_autocorrelation()` | `analysis-bases.md §2.2` | Clustering indicator |
| High-Volatility Duration | `compute_high_vol_duration()` | `analysis-bases.md §2.3` | Regime persistence |
| Trend-Follower Contribution | `compute_trend_follower_contribution()` | `analysis-bases.md §2.4` | Trend amplification |
| Slow-Adapter Lag | `compute_slow_adapter_lag()` | `analysis-bases.md §2.5` | Adaptive persistence |
| Volatility-Trader Regime Response | `compute_volatility_trader_response()` | `analysis-bases.md §2.6` | Threshold behavior |
| Fundamental Stabilization | `compute_fundamental_stabilization()` | `analysis-bases.md §2.7` | Value anchor |

## §3 Dimension-by-Dimension Analysis

Rule output should show autocorrelated absolute returns and persistent
high-volatility regimes after shocks.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Volatility clustering | Absolute returns remain elevated after shocks |
| Trend amplification | TrendFollower contributes during high-vol periods |
| Slow adaptation | SlowAdapter extends the shock response |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
