# Momentum Effect Rule Analysis Plan

## §1 Objectives

Verify that the deterministic baseline produces return continuation through
momentum and technical order flow, then shows offset from contrarian, passive,
market-making, and fundamental-value roles.

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

Analyze price continuation, signal-driven order flow, role-level volume share,
and fundamental anchoring.

## §4 Phase Analysis

Signal formation, momentum activation, crowded continuation, offset, and
stabilization or reversal.

## §5 Cross-Variant Comparison

Use Rule as the deterministic reference for all API variants.

## §6 Expected Results And Validation Criteria

A valid Rule sample should complete 200 rounds, show non-trivial order flow,
and include at least one phase with positive continuation pressure.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`.
