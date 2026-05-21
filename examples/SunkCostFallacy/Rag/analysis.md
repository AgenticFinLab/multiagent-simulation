# SunkCostFallacy Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved behavioral-finance context changes sunk-cost
holding, commitment escalation, rational cutting, and opportunity-cost
reallocation.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Context-informed refusal to realize losses. |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Context-informed averaging down. |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Forward-looking benchmark. |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost benchmark. |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Biased-vs-rational outcome gap. |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | Start of loss-state evaluation. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed pressure by class. |
| RAG Knowledge Effect | `analyze_rag_knowledge_effect()` | `analysis-bases.md §6` | Retrieval success and fallback context rates. |

## §3 Dimension-By-Dimension Analysis

Compare Rag with LLM and RuleLLM to isolate whether retrieved evidence changes
escalation or rational cutting.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | `rag_context` discusses sunk costs, escalation, or opportunity cost. |
| Domain-grounded reasoning | Reasoning may cite retrieved behavioral evidence. |
| Retrieval fallback | Explicit fallback context is counted in `rag_stats.json`. |
| Output quality | Invalid decision JSON fails after bounded retries. |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RAG diagnostics derive from
`../analysis-bases.md §6` and historical cases in `../simulation-bases.md §8`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Confirm `rag_context` is recorded in accepted investor outputs.
- Confirm `rag_stats.json` reports total RAG rounds, retrieval success rounds,
  and fallback rounds.

## §7 Reporting Notes

Report Rag as the domain-knowledge condition. Retrieval fallback context is a
quality diagnostic, not hidden simulation fallback.
