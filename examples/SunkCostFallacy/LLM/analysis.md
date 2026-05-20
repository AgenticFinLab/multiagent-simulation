# SunkCostFallacy LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents produce sunk-cost holding, commitment
escalation, rational cutting, and opportunity-cost reallocation.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Sunk-cost persona holds |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Escalation persona buys |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Rational persona exits |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost shifts |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Bias performance cost |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Timing of loss state |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule to evaluate whether natural-language rationalizations
increase or reduce sunk-cost persistence.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Sunk-cost rationalization | Explanations justify holding losers |
| Escalation narrative | Commitment persona justifies averaging down |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

