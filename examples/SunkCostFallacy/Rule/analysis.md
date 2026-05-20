# SunkCostFallacy Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic sunk-cost holding, commitment escalation,
rational cutting, opportunity-cost reallocation, and noise rules produce sticky
losing positions and escalation.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | SunkCostHolder hold behavior |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | CommitmentEscalator buys |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | RationalCutter sells |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost exit |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Bias cost |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | First loss state |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare holding losers, escalation, rational cutting, opportunity reallocation,
and performance drag.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Sunk-cost holding | SunkCostHolder avoids realizing losses |
| Escalation | CommitmentEscalator adds after losses |
| Rational benchmark | RationalCutter exits based on forward-looking value |

## §5 References

Metrics derive from `../analysis-bases.md §2`; deterministic behavior derives
from `../simulation-bases.md §4` and `§9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Confirm investor orders contain valid action, quantity, and agent type fields.
- Confirm escalation, rational cutting, and opportunity-cost activity can be
  attributed by agent.

## §7 Reporting Notes

Report this variant as the deterministic baseline for sunk-cost persistence.
Compare API variants only after parser and output-quality checks pass.
