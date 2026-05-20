# StatusQuoBias LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents produce status quo underreaction,
default adherence, active rebalancing, and momentum offset.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Inertial persona hold rate |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Default-following strength |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Active persona response |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Delayed adjustment |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend pressure |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule to evaluate whether natural-language inertia changes
underreaction magnitude or timing.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Inaction rationalization | LLM explanations justify holding current allocation |
| Active benchmark | Active persona should be less inertial |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit parse failures, retry counts, and fallback behavior before acceptance.
- Confirm output reasoning explains inaction, default adherence, or active
  rebalancing without invalid JSON.

## §7 Reporting Notes

Report LLM outcomes together with output-quality diagnostics. Parse failure
after retries should fail the sample rather than entering a silent hold.
