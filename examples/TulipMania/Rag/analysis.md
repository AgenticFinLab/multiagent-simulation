# Tulip Mania Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both TulipMania market quality and whether retrieval was
available during model decisions.

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

Analyze market path, role-specific demand, fallback rate, retrieval success
rate, and whether retrieved context changes reasoning relative to RuleLLM.

## §4 Phase Analysis

Use the same mania phases as Rule and compare retrieval coverage across phases.

## §5 Cross-Variant Comparison

Rag is compared against RuleLLM to identify the incremental effect of retrieved
historical context.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid quantity orders,
write `rag_context` for decisions, and produce `rag_stats.json` with retrieval
coverage.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_tulipmania_dynamics.png`, `02_tulipmania_analysis.png`, `03_summary.png`,
and `rag_stats.json`.
