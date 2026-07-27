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

## §4 Variant-Specific Observable Phenomena

RuleLLM injects the Rule formulas (recency weight, media response, systematic
correction gain, value anchor) into the LLM prompt. The model uses the given
formulas to derive its order size while providing narrative characterization.

| Phenomenon                     | Description                                                                                          | How to Observe                                                                        | Contrast with Rule Baseline                                     |
|--------------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| Formula-grounded reasoning     | `<analysis>` sections reproduce the Rule computation with occasional persona commentary              | Reasoning traces at bias onset and correction                                         | Rule provides no verbal trace                                   |
| Bounded persona modulation     | Order sizes stay within ±20% of the Rule quantity even when persona voice varies                     | Bid-cloud dispersion in `00_investor_bids.png` around Rule bids                       | LLM can shift sizes by 100% or more                             |
| Rule-preserving timing         | Bias onset, `BPS`, and `SR` cluster tightly around Rule                                              | `summary.json` metric distributions over 10 trials                                    | LLM shows wide distributions                                    |
| Explicit calculation traces    | Recency weight and media response applied in prompt-embedded formulas                                | `<analysis>` fields reference config parameters                                       | Rule executes silently                                          |
| Narrative-consistent correction | SystematicAnalyst and ValueTrader personas cite anchoring rules; `SR` remains in [0.4, 0.8]         | Reasoning traces plus `summary.json → metrics.stabilization_ratio`                    | Rule stays there by construction                                |

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                       | Phenomenon Clarity | Recommended Use   |
|--------------|---------------------------------------------------------------------------|--------------------|-------------------|
| 100          | Bias episode visible; metric means close to Rule                          | High               | Standard runs     |
| 200          | Full cycle plus stability audit; tight variance around Rule               | Very High          | Publication runs  |
| 500          | Multi-cycle robustness; verify rule anchor holds long-term                | High               | Robustness checks |

### Agent Count Scaling

| Agent Count      | Expected Observable                                                       | Environment Dynamics                                       |
|------------------|---------------------------------------------------------------------------|------------------------------------------------------------|
| 10 (min viable)  | Bias episode forms; rule-clamped sizes limit runaway effects              | Rule anchor dominates when few agents contribute            |
| 20 (recommended) | Standard channel separation; hybrid effects clearly visible               | Reference configuration                                    |
| 40+              | LLM variance averages out; metrics converge tightly around Rule            | RuleLLM approaches pure Rule in aggregate                   |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                | Change | Expected Effect on This Variant's Analysis                                                                             |
|------------------------------------------|--------|-----------------------------------------------------------------------------------------------------------------------|
| `temperature` (LLM)                      | +50%   | Wider narrative variety; sizing spread widens toward ±20% clamp; metric variance grows toward pure LLM                |
| `temperature` (LLM)                      | −50%   | Metric distributions collapse toward Rule                                                                             |
| Removing rule text from prompt           | Any    | RuleLLM degrades toward pure LLM behavior; a canary for prompt correctness                                            |
| `RecentEventOverweighter.recency_weight` | +50%   | Rule's amplitude rises; RuleLLM tracks it closely                                                                     |
| `SystematicAnalyst.correction_gain`      | +50%   | `SR` rises; LLM commentary should acknowledge the stronger correction                                                 |

## §6 Output Files Reference

`RuleLLM/analysis.py` imports the Rule analysis pipeline. Outputs are in
`EXPERIMENT/AvailabilityBias/RuleLLM/analysis/`.

| Output File                             | Generated By          | Contents                                                                                                             | How to Interpret                                                                                                    |
|-----------------------------------------|-----------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `summary.json`                          | shared Rule analysis  | All Rule metrics: `peak_deviation`, `bias_persistence`, `bias_magnitude`, `return_autocorr_lag1`, `stabilization_ratio` | Distribution should be tighter than LLM and centered near Rule; validation score comparable to Rule                 |
| `00_investor_bids.png`                  | shared Rule analysis  | Market price + individual bids                                                                                       | RuleLLM bid cloud should hug the Rule deterministic path more tightly than LLM's                                    |
| `01_availability_bias_dynamics.png`     | shared Rule analysis  | Price + deviation                                                                                                    | Onset round within 1–2 rounds of Rule                                                                               |
| `02_availability_bias_analysis.png`     | shared Rule analysis  | Volume decomposition + rolling AC1                                                                                   | AC1 distribution tight; SR stays in [0.4, 0.8]                                                                      |
| `03_summary.png`                        | shared Rule analysis  | Fit summary                                                                                                          | Overall validation score comparable to Rule                                                                         |

## §7 Cross-Variant Comparison Notes

RuleLLM tests the hypothesis that explicit rule text embedded in the prompt
suffices to keep a stochastic model close to the deterministic baseline
(`analysis-bases.md §5`, `§6.3`).

| Comparison Axis           | RuleLLM's Expected Position                                    | Reason                                                                             |
|---------------------------|----------------------------------------------------------------|------------------------------------------------------------------------------------|
| Onset speed               | Very close to Rule                                             | Rule branches given verbatim in prompt                                             |
| Peak `PDF`                | Distribution centered near Rule; std smaller than LLM          | Rule-clamped sizing bounds behavior                                                |
| Persistence `BPS`         | Between Rule and LLM; usually near Rule                        | Formula anchoring survives most persona variation                                  |
| Stabilization `SR`        | Within [0.4, 0.8] with high probability                        | Systematic/value formulas are in the prompt                                        |
| Behavioral realism        | Higher than Rule; lower than LLM                               | Narrative present but constrained                                                  |
| Reproducibility           | Higher than LLM; lower than Rule                               | Sampling variance survives even under rule anchor                                  |
