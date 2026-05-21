# SunkCostFallacy LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents reproduce sunk-cost holding,
commitment escalation, rational cutting, and opportunity-cost reasoning.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Persona-driven refusal to realize losses. |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Averaging-down pressure. |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Forward-looking persona behavior. |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost persona behavior. |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Biased-vs-rational outcome gap. |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Start of loss-state evaluation. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed pressure by class. |

## §3 Dimension-By-Dimension Analysis

Compare LLM with Rule on escalation volume, rational counterpressure, price
path, and explanation quality.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Sunk-cost rationalization | Reasoning cites prior commitment or reluctance to realize losses. |
| Escalation narrative | Commitment agents justify averaging down. |
| Output quality | Invalid canonical decision fields fail after bounded retries. |

## §5 References

Metrics derive from `../analysis-bases.md §2`; persona targets derive from
`../simulation-bases.md §4` and `../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Review LLM logs for parse failures, retries, and provider errors.
- Confirm deterministic contract failures do not enter silent fallback.

## §7 Reporting Notes

Report LLM as the persona-reasoning condition. Include parse-warning counts and
accepted-decision quality in final sample review.
