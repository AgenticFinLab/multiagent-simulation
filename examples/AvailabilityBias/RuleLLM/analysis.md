# AvailabilityBias RuleLLM — Analysis Documentation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Analysis Script | `examples/AvailabilityBias/RuleLLM/analysis.py` imports the Rule analysis implementation |
| Basis | `../analysis-bases.md` |
| Outputs | Same fixed output set as Rule |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md Ref | RuleLLM-Specific Notes |
|---|---|---|---|
| Price Deviation from Fundamental | `_compute_peak_deviation(...)` | `§2 Metric: Price Deviation from Fundamental` | Should remain near Rule baseline. |
| Bias Persistence Score | `_compute_bias_persistence(...)` | `§2 Metric: Bias Persistence Score` | Formula anchoring should reduce narrative persistence. |
| Availability Bias Magnitude | investor payload decomposition | `§2 Metric: Availability Bias Magnitude` | Confirm calculations in reasoning. |
| Return Autocorrelation | `_compute_rolling_ac1(...)` | `§2 Metric: Return Autocorrelation` | Expected between Rule and LLM variance. |
| Agent-Type Volume Share | `_load_data(...)` | `§2 Metric: Agent-Type Volume Share` | Checks formula-driven channel attribution. |
| Stabilization Ratio | `_compute_stabilization_ratio(...)` | `§2 Metric: Stabilization Ratio` | Tests whether rational rules remain effective. |
| RAG Retrieval Failure Rate | not applicable | `§2 Metric: RAG Retrieval Failure Rate` | RuleLLM variant has no retrieval. |

## §3 Analysis Dimensions

RuleLLM analysis focuses on whether explicit formulas constrain persona variability while preserving the same market mechanism.

## §4 Phase Analysis

Bias onset should follow the Rule thresholds with stochastic wording and minor quantity variation from LLM decisions.

## §5 Cross-Variant Comparison

RuleLLM should be compared against Rule for formula adherence and against LLM for reduction of persona drift.

## §6 Expected Results

### §6.1 Stylised Facts

RuleLLM should produce bounded availability-bias episodes and explicit calculation traces in reasoning.

### §6.2 Calibration Targets

Same targets as `analysis-bases.md §6.2`; successful samples must have parse-valid decisions without fallback-hold substitution.

### §6.3 Cross-Variant Predictions

RuleLLM is expected to be more disciplined than LLM and more stochastic than Rule.

### §6.4 Validation Failure Signs

Reasoning that omits formulas, invalid action JSON, or SystematicAnalyst use of recency salience indicates a contract or quality issue.

## §7 Visualization Catalogue

The imported analysis writes `summary.json`, `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, and `03_summary.png`.
