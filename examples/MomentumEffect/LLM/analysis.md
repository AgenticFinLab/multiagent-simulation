# Momentum Effect LLM Analysis Plan

## §1 Objectives

Verify that persona-driven API decisions preserve a coherent momentum effect
with the five-role API population.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Return autocorrelation | `compute_return_autocorrelation(returns, lag=1)` | `analysis-bases.md §2.1` |
| Momentum order imbalance | `compute_momentum_order_imbalance(orders)` | `analysis-bases.md §2.2` |
| Contrarian offset | `compute_contrarian_offset(orders)` | `analysis-bases.md §2.3` |
| Trend duration | `compute_trend_duration(prices)` | `analysis-bases.md §2.4` |
| Fundamental deviation | `compute_fundamental_deviation(prices, fundamentals)` | `analysis-bases.md §2.5` |
| Agent volume share | `compute_agent_volume_share(orders)` | `analysis-bases.md §2.6` |

## §3 Analysis Dimensions

Analyze market path, role-level order flow, parser quality, fallback rate, and
whether TrendFollower amplifies continuation.

## §4 Phase Analysis

Signal formation, API trend conviction, crowded continuation, offset, and
stabilization or reversal.

## §5 Cross-Variant Comparison

Compare against Rule for mechanism shape and against RuleLLM for the value of
explicit rules.

## §6 Expected Results And Validation Criteria

A valid LLM sample should complete 200 rounds, retain finite market state, and
avoid excessive fallback holds under the project fallback policy.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`.
