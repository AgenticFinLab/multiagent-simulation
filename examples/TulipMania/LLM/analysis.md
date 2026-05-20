# TulipMania LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents produce mania inflation, crowd demand,
valuation resistance, early exits, and collapse.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Bubble Premium | `compute_bubble_premium()` | `analysis-bases.md §2.1` | LLM-driven overpricing |
| Trend-Chasing Volume | `compute_trend_chasing_volume()` | `analysis-bases.md §2.2` | Trend persona demand |
| Social-Proof Demand | `compute_social_proof_demand()` | `analysis-bases.md §2.3` | Crowd persona demand |
| Fundamental Resistance | `compute_fundamental_resistance()` | `analysis-bases.md §2.4` | Value persona selling |
| Early Exit Timing | `compute_early_exit_timing()` | `analysis-bases.md §2.5` | Exit timing |
| Crash Magnitude | `compute_crash_magnitude()` | `analysis-bases.md §2.6` | Collapse size |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule to evaluate whether natural-language mania reasoning
changes bubble size or crash timing.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Mania rationalization | LLM explanations cite trend or crowd demand |
| Fundamental skepticism | Intrinsic-value persona resists extreme prices |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

