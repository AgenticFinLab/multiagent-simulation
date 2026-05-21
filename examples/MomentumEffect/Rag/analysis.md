# Momentum Effect Rag Analysis Plan

## §1 Objectives

Verify that the retrieval-augmented API variant preserves the RuleLLM momentum
contract and records usable retrieval evidence.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Return autocorrelation | `compute_return_autocorrelation(returns, lag=1)` | `analysis-bases.md §2.1` |
| Momentum order imbalance | `compute_momentum_order_imbalance(orders)` | `analysis-bases.md §2.2` |
| Contrarian offset | `compute_contrarian_offset(orders)` | `analysis-bases.md §2.3` |
| Trend duration | `compute_trend_duration(prices)` | `analysis-bases.md §2.4` |
| Fundamental deviation | `compute_fundamental_deviation(prices, fundamentals)` | `analysis-bases.md §2.5` |
| Agent volume share | `compute_agent_volume_share(orders)` | `analysis-bases.md §2.6` |
| Retrieval coverage | `compute_rag_retrieval_coverage(rag_payloads)` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze market continuation, role-level order flow, liquidity fields, parser
quality, and retrieval coverage.

## §4 Phase Analysis

Signal formation, retrieval-informed continuation, crowded trend following,
offset, and stabilization or reversal.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to isolate the effect of retrieved domain knowledge
on momentum conviction and timing.

## §6 Expected Results And Validation Criteria

A valid Rag sample should complete 200 rounds, preserve `provides_liquidity`,
record `rag_context`, and produce `rag_stats.json`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
