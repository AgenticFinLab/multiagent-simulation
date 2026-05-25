# AvailabilityBias LLM — Analysis Documentation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Analysis Script | `examples/AvailabilityBias/LLM/analysis.py` imports the Rule analysis implementation |
| Basis | `../analysis-bases.md` |
| Outputs | Same fixed output set as Rule |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md Ref | LLM-Specific Notes |
|---|---|---|---|
| Price Deviation from Fundamental | `_compute_peak_deviation(...)` | `§2 Metric: Price Deviation from Fundamental` | Captures persona-driven mispricing depth. |
| Bias Persistence Score | `_compute_bias_persistence(...)` | `§2 Metric: Bias Persistence Score` | Detects whether narratives persist. |
| Availability Bias Magnitude | investor payload decomposition | `§2 Metric: Availability Bias Magnitude` | Requires reasoning-quality audit for agent contamination. |
| Return Autocorrelation | `_compute_rolling_ac1(...)` | `§2 Metric: Return Autocorrelation` | Shows overreaction and correction timing. |
| Agent-Type Volume Share | `_load_data(...)` | `§2 Metric: Agent-Type Volume Share` | Reveals which LLM persona drives order flow. |
| Stabilization Ratio | `_compute_stabilization_ratio(...)` | `§2 Metric: Stabilization Ratio` | Tests SystematicAnalyst/ValueTrader discipline. |
| RAG Retrieval Failure Rate | not applicable | `§2 Metric: RAG Retrieval Failure Rate` | LLM variant has no retrieval. |

## §3 Analysis Dimensions

LLM analysis uses the same metrics as Rule, then interprets differences as stochastic persona effects. Reasoning fields should be inspected for invalid JSON, formula leakage, or SystematicAnalyst contamination.

## §4 Phase Analysis

Bias phases may be less smooth than Rule because persona outputs can change direction across rounds. Valid phases still require finite price paths and parse-valid actions.

## §5 Cross-Variant Comparison

Compare LLM against Rule for bias depth and against RuleLLM for the value of explicit formula anchoring.

## §6 Expected Results

### §6.1 Stylised Facts

LLM may show higher variance in peak deviation and persistence than Rule.

### §6.2 Calibration Targets

Same metric targets as `analysis-bases.md §6.2`; LLM-specific quality requires no silent fallback holds in successful runs.

### §6.3 Cross-Variant Predictions

LLM is expected to be more variable than Rule and less formula-disciplined than RuleLLM.

### §6.4 Validation Failure Signs

Repeated parser errors, invalid `bid_price`, missing `reasoning`, or SystematicAnalyst overreliance on recent salience require quality investigation.

## §7 Visualization Catalogue

The imported analysis writes `summary.json`, `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, and `03_summary.png`.
