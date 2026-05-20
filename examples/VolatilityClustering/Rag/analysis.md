# VolatilityClustering Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved volatility-context changes regime persistence,
trend amplification, or volatility-trader responses.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Rolling Volatility | `compute_rolling_volatility()` | `analysis-bases.md §2.1` | Knowledge-informed regimes |
| Volatility Autocorrelation | `compute_volatility_autocorrelation()` | `analysis-bases.md §2.2` | Clustering under RAG |
| High-Volatility Duration | `compute_high_vol_duration()` | `analysis-bases.md §2.3` | Compare with RuleLLM |
| Trend-Follower Contribution | `compute_trend_follower_contribution()` | `analysis-bases.md §2.4` | Retrieved trend context |
| Slow-Adapter Lag | `compute_slow_adapter_lag()` | `analysis-bases.md §2.5` | Persistence from lagged beliefs |
| Volatility-Trader Regime Response | `compute_volatility_trader_response()` | `analysis-bases.md §2.6` | Dynamic liquidity contract relevance |
| Fundamental Stabilization | `compute_fundamental_stabilization()` | `analysis-bases.md §2.7` | Valuation context |

## §3 Dimension-by-Dimension Analysis

Compare Rag against RuleLLM and inspect whether retrieved context changes
high-volatility duration or threshold response.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Knowledge-informed volatility response | VolatilityTrader decisions reflect retrieved volatility context |
| Persistence change | High-volatility duration differs from RuleLLM |
| Retrieval quality | Low retrieval or fallback is marked in Level-2 review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag mechanism derives from
`../simulation-bases.md §9`.
