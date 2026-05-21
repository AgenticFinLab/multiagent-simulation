# Volatility Clustering Rag Analysis Plan

## §1 Objectives

This analysis checks whether retrieved volatility-domain knowledge changes
regime interpretation, liquidity provision, or high-volatility duration while
preserving the RuleLLM market contract.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Rolling volatility | `def compute_rolling_volatility(returns: list[float], window: int) -> list[float]` | `analysis-bases.md §2.1` |
| Absolute-return autocorrelation | `def compute_abs_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.2` |
| High-volatility duration | `def compute_high_vol_duration(volatility: list[float], threshold: float) -> int` | `analysis-bases.md §2.3` |
| Volatility-regime response | `def compute_volatility_regime_response(orders: list[dict], volatility: list[float]) -> float` | `analysis-bases.md §2.5` |
| API and retrieval quality | `def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review volatility persistence, liquidity provision, parser quality,
conservative liquidity defaults, and retrieval coverage.

## §4 Phase Analysis

Analyze whether retrieved context affects shock onset, high-volatility
persistence, or reversion toward calmer volatility.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to isolate retrieval effects, and against Rule/LLM
for broader mechanism preservation.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, order-level liquidity
values, `rag_context` fields, and a `rag_stats.json` retrieval audit.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volatilityclustering_dynamics.png`, `02_volatilityclustering_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
