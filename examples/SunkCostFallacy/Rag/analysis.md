# SunkCostFallacy Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved behavioral-finance context changes sunk-cost
holding, escalation, rational cutting, and opportunity-cost reallocation.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Context-informed holding |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Context-informed escalation |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Forward-looking correction |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Reallocation context |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Bias cost |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Loss timing |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag with LLM to isolate whether retrieved domain evidence changes
holding losers or escalation behavior.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | Retrieved context should discuss sunk costs or escalation |
| Domain-grounded reasoning | Explanations may cite behavioral decision evidence |
| Output quality | RAG retrieval and parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag design derives from
`../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit retrieval context availability, parse failures, and retry counts.
- Confirm `rag_context` appears in accepted output artifacts for Level-2 review.

## §7 Reporting Notes

Report RAG outcomes with retrieval diagnostics. Missing or fallback retrieval
context should be explicitly noted even if simulator execution succeeds.
