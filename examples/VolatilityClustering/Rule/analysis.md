# Volatility Clustering Rule Analysis Plan

## §1 Objectives

This analysis checks whether the deterministic GARCH baseline produces complete
volatility clustering: finite price path, persistent volatility, nonzero order
flow, and interpretable calm and turbulent phases.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Rolling volatility | `def compute_rolling_volatility(returns: list[float], window: int) -> list[float]` | `analysis-bases.md §2.1` |
| Absolute-return autocorrelation | `def compute_abs_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.2` |
| High-volatility duration | `def compute_high_vol_duration(volatility: list[float], threshold: float) -> int` | `analysis-bases.md §2.3` |
| Trend amplification share | `def compute_trend_amplification_share(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Stabilization pressure | `def compute_stabilization_pressure(orders: list[dict], prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.6` |

## §3 Analysis Dimensions

Review price, returns, rolling volatility, absolute-return persistence, and
order flow by deterministic role.

## §4 Phase Analysis

Segment the run into calm baseline, shock onset, clustered high volatility,
adaptive response, and return toward calmer volatility.

## §5 Cross-Variant Comparison

Rule is the benchmark for comparing LLM, RuleLLM, and Rag on volatility
persistence, order-flow composition, and structural quality.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, nonzero volume, bounded
volatility, and observable return variation.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volatilityclustering_dynamics.png`, `02_volatilityclustering_analysis.png`,
and `03_summary.png`.
