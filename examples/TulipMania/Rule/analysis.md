# Tulip Mania Rule Analysis Plan

## §1 Objectives

The Rule analysis checks whether deterministic positive-feedback and correction
rules produce a complete TulipMania trajectory suitable for cross-variant
comparison.

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

Analyze price premium, order imbalance, agent-type demand, volume, finite-value
integrity, and market phase transitions.

## §4 Phase Analysis

Use the phases in `analysis-bases.md §4`: initialization, bubble ignition,
mania acceleration, overvaluation peak, correction pressure, and terminal state.

## §5 Cross-Variant Comparison

The Rule output is the reference for comparing LLM stochasticity, RuleLLM
formula adherence, and Rag retrieval influence.

## §6 Expected Results and Validation Criteria

A full Rule sample should complete 200 rounds, record finite positive prices,
produce non-trivial order flow, and show interpretable positive-feedback and
correction pressure.

## §7 Visualization Catalogue

The analysis output contract is `summary.json`, `00_investor_bids.png`,
`01_tulipmania_dynamics.png`, `02_tulipmania_analysis.png`, and
`03_summary.png`.
