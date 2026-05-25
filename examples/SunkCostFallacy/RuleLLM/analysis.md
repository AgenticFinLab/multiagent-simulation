# SunkCostFallacy RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether explicit rule guidance keeps LLM sunk-cost, escalation,
rational-cutting, and opportunity-cost behavior aligned with the Rule baseline.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Rule-guided hold behavior. |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Rule-guided averaging down. |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Forward-looking rule guidance. |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost rule guidance. |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Biased-vs-rational outcome gap. |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Start of loss-state evaluation. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed pressure by class. |

## §3 Dimension-By-Dimension Analysis

Compare RuleLLM to Rule and LLM to isolate the effect of explicit rule text.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions reference sunk-cost, escalation, or opportunity-cost rules. |
| Schema stability | Parser receives all canonical fields. |
| Behavioral alignment | Action direction and quantity are closer to Rule than persona-only LLM. |

## §5 References

Metrics derive from `../analysis-bases.md §2`; prompt-rule design derives from
`../simulation-bases.md §4` and `../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Audit parse retries and invalid-decision failures.
- Compare action direction and quantity scale with Rule.

## §7 Reporting Notes

Report RuleLLM as the formula-guided language condition. Separate stochastic API
issues from deterministic prompt/parser contract failures.
