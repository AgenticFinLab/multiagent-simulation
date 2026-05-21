# MentalAccounting Rag — Analysis Specification

## §1 Overview

The Rag analysis extends the standard MentalAccounting metric pipeline with retrieval coverage diagnostics. It measures the same market and behavior metrics as RuleLLM and writes `rag_stats.json` from recorded `rag_context` payloads.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Account-Level Turnover (ALT) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Account-Level Turnover` |
| House-Money Risk Shift (HMRS) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: House-Money Risk Shift` |
| Sunk-Cost Holding Ratio (SCHR) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Sunk-Cost Holding Ratio` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Behavioral Price Impact (BPI) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Behavioral Price Impact` |
| Return Volatility (RV) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Return Volatility` |
| Realization Frequency Ratio (RFR) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Realization Frequency Ratio` |
| Retrieval Coverage | `analyze_rag_knowledge_effect(investor_payloads)` | `analysis-bases.md §5 Cross-Variant Comparison` |

## §3 Analysis Dimensions

Rag analysis compares market behavior, investor actions, reasoning text, retrieval coverage, and whether retrieved context appears in accepted orders.

## §4 Phase Analysis

The run is read as initialization, index availability, retrieved-context decision cycles, and stabilization. Retrieval coverage is interpreted alongside ALT, HMRS, SCHR, RFR, and RBD.

## §5 Cross-Variant Comparison

Rag should preserve RuleLLM's decision schema while adding knowledge traces. Cross-variant review checks whether retrieved context changes decision timing or improves explanation coherence.

## §6 Expected Results

### §6.1 Stylised Facts

Valid Rag runs should show non-empty retrieval traces, parseable decisions, mental-accounting trading patterns, and standard market histories.

### §6.2 Calibration Targets

Core market and behavioral targets follow `analysis-bases.md §6.2`; retrieval statistics should show visible coverage for agents that query the shared knowledge index.

### §6.3 Cross-Variant Predictions

Rag may produce more historically grounded reasoning than RuleLLM while keeping the same action schema and bounded order behavior.

### §6.4 Validation Failure Signs

Missing `rag_context`, absent `rag_stats.json`, unavailable processed documents, invalid decision JSON, or broken price/fundamental histories indicate failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_mentalaccounting_dynamics.png`, `02_mentalaccounting_analysis.png`, `03_summary.png`, and `rag_stats.json`.
