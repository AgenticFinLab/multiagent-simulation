# VolatilityClustering RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether RuleLLM preserves volatility-clustering rules and how LLM
reasoning changes persistence.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Rolling Volatility | `compute_rolling_volatility()` | `analysis-bases.md §2.1` | Compare with Rule |
| Volatility Autocorrelation | `compute_volatility_autocorrelation()` | `analysis-bases.md §2.2` | Rule fidelity |
| High-Volatility Duration | `compute_high_vol_duration()` | `analysis-bases.md §2.3` | Persistence under LLM |
| Trend-Follower Contribution | `compute_trend_follower_contribution()` | `analysis-bases.md §2.4` | Prompt-rule contribution |
| Slow-Adapter Lag | `compute_slow_adapter_lag()` | `analysis-bases.md §2.5` | Gradual update adherence |
| Volatility-Trader Regime Response | `compute_volatility_trader_response()` | `analysis-bases.md §2.6` | Threshold behavior |
| Fundamental Stabilization | `compute_fundamental_stabilization()` | `analysis-bases.md §2.7` | Value anchor |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM to Rule for volatility persistence and regime-triggered order
flow. Inspect LLM decisions if persistence disappears.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | VolatilityTrader responds to high/low-vol thresholds |
| Trend amplification | TrendFollower contributes during clustered volatility |
| Clean output | Low parse/fallback counts |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
