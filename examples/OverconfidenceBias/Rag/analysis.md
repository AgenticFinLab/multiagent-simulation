# OverconfidenceBias Rag — Analysis Specification

## §1 Overview

The Rag analysis extends the standard OverconfidenceBias metric pipeline with retrieval coverage diagnostics from recorded `rag_context` payloads.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Excess Turnover (ET) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Excess Turnover` |
| Signal Overreaction (SO) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Signal Overreaction` |
| Confidence Reinforcement Activity (CRA) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Confidence Reinforcement Activity` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Return Volatility (RV) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Return Volatility` |
| Portfolio Performance Gap (PPG) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Portfolio Performance Gap` |
| Retrieval Coverage | `analyze_rag_knowledge_effect(investor_payloads)` | `analysis-bases.md §5 Cross-Variant Comparison` |

## §3 Analysis Dimensions

Rag analysis compares market metrics, role-level order flow, reasoning text, retrieval coverage, and canonical order validity.

## §4 Phase Analysis

The run is read as initialization, index availability, retrieved-context decisions, and market feedback.

## §5 Cross-Variant Comparison

Rag should preserve RuleLLM action schema while adding auditable knowledge traces.

## §6 Expected Results

### §6.1 Stylised Facts

Valid Rag runs should show non-empty retrieval traces, parseable decisions, and standard overconfidence market metrics.

### §6.2 Calibration Targets

Core targets follow `analysis-bases.md §6.2`; retrieval coverage should be visible in `rag_stats.json`.

### §6.3 Cross-Variant Predictions

Rag may produce more historically grounded reasoning than RuleLLM while keeping comparable action schemas.

### §6.4 Validation Failure Signs

Missing `rag_context`, absent `rag_stats.json`, invalid decisions, unavailable documents, or broken market histories indicate failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_overconfidencebias_dynamics.png`, `02_overconfidencebias_analysis.png`, `03_summary.png`, and `rag_stats.json`.
