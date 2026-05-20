# TulipMania Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved mania/bubble context changes bubble premium,
trend-chasing demand, social-proof demand, valuation resistance, and crash
dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Bubble Premium | `compute_bubble_premium()` | `analysis-bases.md §2.1` | Context-informed overpricing |
| Trend-Chasing Volume | `compute_trend_chasing_volume()` | `analysis-bases.md §2.2` | Retrieved trend context |
| Social-Proof Demand | `compute_social_proof_demand()` | `analysis-bases.md §2.3` | Retrieved crowd context |
| Fundamental Resistance | `compute_fundamental_resistance()` | `analysis-bases.md §2.4` | Valuation context |
| Early Exit Timing | `compute_early_exit_timing()` | `analysis-bases.md §2.5` | Exit timing |
| Crash Magnitude | `compute_crash_magnitude()` | `analysis-bases.md §2.6` | Collapse size |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag with LLM to isolate whether retrieved domain evidence changes
mania amplification or correction timing.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | Retrieved context should discuss manias, bubbles, or valuation |
| Domain-grounded reasoning | Explanations may cite historical mania behavior |
| Output quality | RAG retrieval and parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag design derives from
`../simulation-bases.md §9`.

