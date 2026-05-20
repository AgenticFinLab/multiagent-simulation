# TulipMania RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether formula-anchored LLM decisions preserve mania inflation,
social-proof demand, valuation resistance, and early exits.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Bubble Premium | `compute_bubble_premium()` | `analysis-bases.md §2.1` | Rule-guided bubble size |
| Trend-Chasing Volume | `compute_trend_chasing_volume()` | `analysis-bases.md §2.2` | Prompt-guided trend demand |
| Social-Proof Demand | `compute_social_proof_demand()` | `analysis-bases.md §2.3` | Prompt-guided crowd demand |
| Fundamental Resistance | `compute_fundamental_resistance()` | `analysis-bases.md §2.4` | Value correction |
| Early Exit Timing | `compute_early_exit_timing()` | `analysis-bases.md §2.5` | Exit timing |
| Crash Magnitude | `compute_crash_magnitude()` | `analysis-bases.md §2.6` | Collapse size |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM with Rule and LLM to isolate the effect of explicit rule
instructions on mania and correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions should respect prompt thresholds |
| Explanation richness | Reasons should cite trend, social proof, value, or exit timing |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM design derives from
`../simulation-bases.md §9`.

