# Momentum Effect RuleLLM Analysis Plan

## §1 Objectives

Verify that explicit momentum, contrarian, technical, trend-following, and
fundamental rules keep API decisions aligned with the intended mechanism.

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

Analyze continuation pressure, `provides_liquidity` quality, parser quality,
and role-level trade direction.

## §4 Phase Analysis

Signal formation, rule-guided continuation, crowded trend following, offset,
and stabilization or reversal.

## §5 Cross-Variant Comparison

RuleLLM should be closer to Rule than LLM in directional consistency while
retaining API-level variation.

## §6 Expected Results And Validation Criteria

A valid RuleLLM sample should complete 200 rounds, preserve the
`provides_liquidity` contract, and avoid hidden parser/schema failures.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`.
