# AvailabilityBias Rag — Analysis Documentation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Analysis Script | `examples/AvailabilityBias/Rag/analysis.py` imports Rule analysis and adds RAG statistics |
| Basis | `../analysis-bases.md` |
| Outputs | Standard fixed output set plus `rag_stats.json` |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md Ref | Rag-Specific Notes |
|---|---|---|---|
| Price Deviation from Fundamental | `_compute_peak_deviation(...)` | `§2 Metric: Price Deviation from Fundamental` | Tests knowledge-altered bias depth. |
| Bias Persistence Score | `_compute_bias_persistence(...)` | `§2 Metric: Bias Persistence Score` | Compares knowledge-guided persistence to LLM/RuleLLM. |
| Availability Bias Magnitude | investor payload decomposition | `§2 Metric: Availability Bias Magnitude` | Must be interpreted with RAG context quality. |
| Return Autocorrelation | `_compute_rolling_ac1(...)` | `§2 Metric: Return Autocorrelation` | Detects knowledge-modified overreaction/reversal. |
| Agent-Type Volume Share | `_load_data(...)` | `§2 Metric: Agent-Type Volume Share` | Shows whether retrieved context changes channel volume. |
| Stabilization Ratio | `_compute_stabilization_ratio(...)` | `§2 Metric: Stabilization Ratio` | Tests whether debiasing context strengthens rational correction. |
| RAG Retrieval Failure Rate | `analyze_rag_knowledge_effect(...)` | `§2 Metric: RAG Retrieval Failure Rate` | Written to `rag_stats.json`. |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §3 Analysis Dimensions

Rag analysis first applies the shared market metrics, then evaluates retrieval coverage and whether `rag_context` is present in investor payloads.

## §4 Variant-Specific Observable Phenomena

Rag adds a knowledge-store retrieval on top of RuleLLM. Each decision prompt
includes a `{rag_context}` slot filled either by retrieved passages or by
`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` when
`KnowledgeStore.query()` finds no relevant documents. Availability-bias
dynamics may be dampened when retrieved narratives about salience bias reach
the personas.

| Phenomenon                    | Description                                                                                                | How to Observe                                                                                              | Contrast with Rule Baseline                                    |
|-------------------------------|------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| Retrieval-informed debiasing  | ValueTrader and SystematicAnalyst cite retrieved arbitrage-limits literature; peak `PDF` lowered            | `<analysis>` fields reference retrieval; `summary.json → metrics.peak_deviation` compared to RuleLLM        | Rule has no context; RuleLLM has no external knowledge         |
| Retrieval failure sentinel    | `_RAG_FALLBACK` injected when knowledge query fails                                                        | Count of rounds where `rag_context == _RAG_FALLBACK`; `retrieval_failure_rate` in `rag_stats.json`         | Not applicable                                                 |
| Media-context-aware bidding   | MediaInfluencedTrader personas may cite retrieved cases of media-driven mispricing                          | Reasoning traces + `01_availability_bias_dynamics.png` deviation curve                                      | Rule executes without narrative                                |
| Earlier correction            | `BPS` slightly shorter than RuleLLM when retrieval succeeds                                                | `summary.json → metrics.bias_persistence` compared to RuleLLM                                              | Rule's `BPS` is deterministic                                  |
| Retrieval-quality audit       | Per-agent `retrieval_success_rate`, `retrieval_failure_rate`, `meets_target` diagnostics                    | `rag_stats.json`                                                                                            | Rule/LLM/RuleLLM have no such file                             |

Cross-variant claims about knowledge effects require `retrieval_failure_rate < 0.30`;
above this the run degrades toward RuleLLM.

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                              | Phenomenon Clarity | Recommended Use            |
|--------------|----------------------------------------------------------------------------------|--------------------|----------------------------|
| 100          | Bias episode plus retrieval audit; warm-up may bias early success rate            | Medium             | Standard runs              |
| 200          | Retrieval statistics converge; full bias/correction cycle                         | High               | Publication runs           |
| 500          | Retrieval-diversity plateau; multi-episode knowledge effects                     | Very High          | Retrieval stress tests     |

### Agent Count Scaling

| Agent Count      | Expected Observable                                                     | Environment Dynamics                                                                    |
|------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 10 (min viable)  | Per-agent retrieval statistics individually diagnosable                  | Small population makes retrieval failures visible in metrics                            |
| 20 (recommended) | Reference configuration; per-agent `rag_stats.json` block                | Standard                                                                                |
| 40+              | Retrieval-quality aggregates smooth; knowledge-store latency dominates    | Persona-level effects average out; useful for knowledge-base regression                |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                | Change | Expected Effect on This Variant's Analysis                                                                                                       |
|------------------------------------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| Knowledge-store size                     | +50%   | `retrieval_success_rate` rises; more diverse anchors in reasoning                                                                                |
| `top_k` in `KnowledgeStore.query`         | +50%   | More context per prompt; fewer `_RAG_FALLBACK` occurrences                                                                                       |
| `top_k`                                   | −50%   | More `_RAG_FALLBACK`; metrics regress toward RuleLLM                                                                                              |
| Similarity threshold                      | Loosen | Fewer sentinel injections; possibly noisier context                                                                                              |
| `temperature` (LLM)                      | +50%   | Wider metric distributions; knowledge advantage narrows                                                                                          |
| `RecentEventOverweighter.recency_weight` | +50%   | Bias amplitude rises but retrieval may still moderate persistence                                                                                |

## §6 Output Files Reference

`Rag/analysis.py` imports the Rule pipeline and additionally writes
`rag_stats.json` from `analyze_rag_knowledge_effect()`. Outputs are in
`EXPERIMENT/AvailabilityBias/Rag/analysis/`.

| Output File                               | Generated By                                             | Contents                                                                                                            | How to Interpret                                                                                                                                    |
|-------------------------------------------|----------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `summary.json`                            | shared Rule analysis                                     | `metrics.peak_deviation`, `bias_persistence`, `bias_magnitude`, `return_autocorr_lag1`, `stabilization_ratio`, `agent_type_volume`, `validation.*` | Compare to RuleLLM; any material improvement in `SR` or reduction in `BPS` must be conditioned on `retrieval_success_rate ≥ 0.70`                    |
| `rag_stats.json`                          | `analyze_rag_knowledge_effect()` in `Rag/analysis.py`    | Per-agent `retrieval_success_rate`, `retrieval_failure_rate`, `meets_target`; aggregate `retrieval_failure_rate`     | `retrieval_failure_rate > 0.30` invalidates cross-variant claims; count `_RAG_FALLBACK` occurrences                                                 |
| `00_investor_bids.png`                    | shared Rule analysis                                     | Market price + individual bids                                                                                      | Value/systematic bidders may cluster tighter around fundamental when retrieval succeeds                                                             |
| `01_availability_bias_dynamics.png`       | shared Rule analysis                                     | Price + deviation                                                                                                   | Peak `PDF` may be lower than Rule/RuleLLM when retrieval is healthy                                                                                  |
| `02_availability_bias_analysis.png`       | shared Rule analysis                                     | Volume decomposition + rolling AC1                                                                                  | `SR` may exceed 0.6; AC1 falls faster during correction                                                                                              |
| `03_summary.png`                          | shared Rule analysis                                     | Fit summary                                                                                                         | Validation score comparable to RuleLLM under successful retrieval                                                                                    |

## §7 Cross-Variant Comparison Notes

Rag is compared primarily against RuleLLM (same rule anchoring; retrieval is
the only added factor). See `analysis-bases.md §5` and `§6.3`.

| Comparison Axis           | Rag's Expected Position                                        | Reason                                                                                                    |
|---------------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Onset speed               | Similar to RuleLLM, sometimes slightly later                   | Retrieved literature can inject caution                                                                   |
| Peak `PDF`                | Median slightly lower than RuleLLM                             | Retrieved bias/arbitrage narratives moderate the episode                                                  |
| Persistence `BPS`         | Sometimes shorter than RuleLLM                                 | ValueTrader/SystematicAnalyst gain evidence-based conviction                                              |
| Stabilization `SR`        | Sometimes higher than RuleLLM                                  | Retrieval reinforces rational corrective personas                                                        |
| Behavioral realism        | Highest of the four variants                                   | Retrieved narratives anchor personas in real cases                                                        |
| Retrieval health          | Only variant with `rag_stats.json`                             | `_RAG_FALLBACK` sentinel classifies each round                                                            |
| Reproducibility           | Between LLM and RuleLLM                                        | Retrieval determinism helps but LLM sampling still adds variance                                          |
