# Tulip Mania RuleLLM Analysis Plan

## §1 Objectives

The RuleLLM analysis checks whether LLM reasoning follows explicit TulipMania
rules while preserving complete market and order records.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Bubble premium | `def compute_bubble_premium(prices, fundamental) -> float` | `analysis-bases.md §2.1` |
| Trend-chasing demand | `def compute_trend_chasing_demand(orders) -> float` | `analysis-bases.md §2.2` |
| Social-proof demand | `def compute_social_proof_demand(orders) -> float` | `analysis-bases.md §2.3` |
| Fundamental resistance | `def compute_fundamental_resistance(orders) -> float` | `analysis-bases.md §2.4` |
| Early exit timing | `def compute_early_exit_timing(orders, prices) -> int` | `analysis-bases.md §2.5` |
| Crash magnitude | `def compute_crash_magnitude(prices) -> float` | `analysis-bases.md §2.6` |
| Agent attribution | `def compute_agent_attribution(orders) -> dict` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Evaluate formula adherence, market path, order imbalance, fallback rate, and
agent-type attribution.

## §4 Phase Analysis

Analyze the same phases as Rule and test whether explicit rules keep phase
timing close to the deterministic baseline.

## §5 Cross-Variant Comparison

RuleLLM should sit between Rule and LLM: closer to Rule formulas but with model
reasoning and possible stochastic variation.

## §6 Expected Results and Validation Criteria

A full RuleLLM sample should complete 200 rounds, keep valid quantity orders,
and preserve fallback counts within the accepted quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_tulipmania_dynamics.png`, `02_tulipmania_analysis.png`, and
`03_summary.png`.
