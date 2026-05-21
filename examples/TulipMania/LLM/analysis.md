# Tulip Mania LLM Analysis Plan

## §1 Objectives

The LLM analysis checks whether persona-driven stochastic decisions still
produce a valid TulipMania trajectory under the same market schema.

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

Analyze market path, role-specific order flow, portfolio constraints, parse
fallback count, and whether persona reasoning remains consistent with the role.

## §4 Phase Analysis

Use the same phase framework as the Rule baseline and compare whether LLM
decisions accelerate or delay mania and correction phases.

## §5 Cross-Variant Comparison

LLM is compared against Rule for bubble premium, crash magnitude, agent
attribution, and fallback rate.

## §6 Expected Results and Validation Criteria

A full LLM sample should complete 200 rounds with valid quantity orders and
fallback rate within the project quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_tulipmania_dynamics.png`, `02_tulipmania_analysis.png`, and
`03_summary.png`.
