# AvailabilityBias Rule — Analysis Documentation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Analysis Script | `examples/AvailabilityBias/Rule/analysis.py` |
| Basis | `../analysis-bases.md` |
| Outputs | `summary.json`, `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, `03_summary.png` |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md Ref | Rule-Specific Notes |
|---|---|---|---|
| Price Deviation from Fundamental | `_compute_peak_deviation(...)` | `§2 Metric: Price Deviation from Fundamental` | Primary bias-depth statistic. |
| Bias Persistence Score | `_compute_bias_persistence(...)` | `§2 Metric: Bias Persistence Score` | Detects sustained availability episodes. |
| Availability Bias Magnitude | volume decomposition in `_compute_stabilization_ratio(...)` | `§2 Metric: Availability Bias Magnitude` | Interpreted through biased/rational volume. |
| Return Autocorrelation | `_compute_rolling_ac1(...)` | `§2 Metric: Return Autocorrelation` | Detects momentum and reversal. |
| Agent-Type Volume Share | `_load_data(...)` investor payloads | `§2 Metric: Agent-Type Volume Share` | Separates recency, media, rational, and noise channels. |
| Stabilization Ratio | `_compute_stabilization_ratio(...)` | `§2 Metric: Stabilization Ratio` | Measures rational correction during bias episodes. |
| RAG Retrieval Failure Rate | not applicable | `§2 Metric: RAG Retrieval Failure Rate` | Rule variant has no retrieval. |

## §3 Analysis Dimensions

| Dimension | Rule Interpretation |
|---|---|
| Bias-Induced Price Dynamics | Rule provides the deterministic formula baseline. |
| Channel Attribution | Recency and media channels are directly traceable to config parameters. |
| Stabilization Effectiveness | SystematicAnalyst and ValueTrader correction is exact and interpretable. |
| Cross-Variant Comparison | Rule is the reference for LLM, RuleLLM, and Rag deviations. |

## §4 Phase Analysis

Rule runs should move from equilibrium into possible bias onset when return or deviation signals cross thresholds, then into correction as stabilizing agents and mean reversion offset biased order flow.

## §5 Cross-Variant Comparison

Use Rule as the calibrated baseline. LLM should be compared for persona drift, RuleLLM for formula adherence, and Rag for knowledge effects.

## §6 Expected Results

### §6.1 Stylised Facts

The Rule variant should show bounded mispricing, nonzero biased-agent volume, and partial correction rather than permanent divergence.

### §6.2 Calibration Targets

Targets come from `analysis-bases.md §6.2`: peak deviation 5%-15%, persistence at least 10% in clear episodes, AC1 0.20-0.40 during active bias, and stabilization ratio 0.4-0.8.

### §6.3 Cross-Variant Predictions

Rule is expected to be less variable than LLM and Rag because only NoiseTrader is stochastic.

### §6.4 Validation Failure Signs

No price data, no fundamental batch store, all-zero quantities, or invalid order fields indicate a contract problem rather than a meaningful market result.

## §7 Visualization Catalogue

The analysis writes the fixed output set required by `docs/create-example-skill/08-step4-implement.md`: `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, `03_summary.png`, and `summary.json`.
