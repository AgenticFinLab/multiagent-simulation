# StatusQuoBias RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether formula-anchored LLM decisions preserve status quo and default
underreaction dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Prompt-guided hold behavior |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Prompt-guided default following |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Active benchmark |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Signal response delay |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend offset |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM with Rule and LLM to isolate the effect of explicit rule
instructions on inertia and default adherence.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions should respect prompt thresholds |
| Explanation richness | Reasons should cite inertia, default, or rebalancing logic |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM design derives from
`../simulation-bases.md §9`.

