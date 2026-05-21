# Volatility Clustering LLM Analysis Plan

## §1 Objectives

This analysis checks whether persona-driven API investors preserve volatility
clustering while producing complete structured order records.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Rolling volatility | `def compute_rolling_volatility(returns: list[float], window: int) -> list[float]` | `analysis-bases.md §2.1` |
| Absolute-return autocorrelation | `def compute_abs_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.2` |
| High-volatility duration | `def compute_high_vol_duration(volatility: list[float], threshold: float) -> int` | `analysis-bases.md §2.3` |
| Trend amplification share | `def compute_trend_amplification_share(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| API and retrieval quality | `def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review volatility persistence, role-level order flow, parser retries, fallback
events, and portfolio constraints.

## §4 Phase Analysis

Use the same phase framework as Rule and inspect whether LLM investors interpret
volatility regimes earlier or later than deterministic thresholds.

## §5 Cross-Variant Comparison

Compare LLM with Rule to isolate prompt-driven stochasticity and with RuleLLM to
measure whether explicit rules reduce dispersion.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, structured order fields, and
low API parse/fallback rates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volatilityclustering_dynamics.png`, `02_volatilityclustering_analysis.png`,
and `03_summary.png`.
