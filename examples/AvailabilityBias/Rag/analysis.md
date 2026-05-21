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

## §3 Analysis Dimensions

Rag analysis first applies the shared market metrics, then evaluates retrieval coverage and whether `rag_context` is present in investor payloads.

## §4 Phase Analysis

RAG should not change the market phases directly; it changes the knowledge available to each investor during the same phase structure.

## §5 Cross-Variant Comparison

Compare Rag primarily against RuleLLM because both use explicit decision rules; differences should be attributed to retrieved context and API stochasticity.

## §6 Expected Results

### §6.1 Stylised Facts

Rag should preserve the same order schema and produce a usable retrieval-quality audit.

### §6.2 Calibration Targets

Same market targets as `analysis-bases.md §6.2`; retrieval failure rate should be low enough to justify knowledge-effect interpretation.

### §6.3 Cross-Variant Predictions

Rag may reduce or sharpen availability bias depending on retrieved evidence, but high retrieval failure makes the sample closer to RuleLLM.

### §6.4 Validation Failure Signs

Missing `rag_context`, absent `rag_stats.json`, embedding-key failures, or parser failures require quality investigation.

## §7 Visualization Catalogue

The imported analysis writes `summary.json`, `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, and `03_summary.png`. The Rag wrapper also writes `rag_stats.json`.
