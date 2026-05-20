# SunkCostFallacy RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether formula-anchored LLM decisions preserve sunk-cost holding,
commitment escalation, rational cutting, and opportunity-cost behavior.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Prompt-guided hold behavior |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Prompt-guided escalation |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Rational benchmark |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost behavior |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Bias cost |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Loss timing |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM with Rule and LLM to isolate whether explicit rule instructions
reduce prompt drift while preserving the behavioral bias.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions should respect prompt thresholds |
| Explanation richness | Reasons should cite sunk cost, commitment, or opportunity cost |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM design derives from
`../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit parse failures, retry counts, and fallback behavior before acceptance.
- Compare action direction and quantity scale with prompt-embedded rules.

## §7 Reporting Notes

Report RuleLLM as a formula-anchored language condition. Parser failures after
all retries should be treated as failed rows, not substituted hold actions.
