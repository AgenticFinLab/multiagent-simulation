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

## §4 Variant-Specific Observable Phenomena

LLM replaces deterministic weighting with persona-conditioned reasoning about
recent salience and media coverage. The Rule analysis pipeline is reused;
metric distributions must be interpreted over multiple trials.

| Phenomenon                     | Description                                                                                        | How to Observe                                                                          | Contrast with Rule Baseline                              |
|--------------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------|
| Persona narrative onset        | RecentEventOverweighter/MediaInfluencedTrader reason about salience before submitting biased orders | `<analysis>` field in payloads; onset round of `|PDF| > 5%`                             | Rule crosses threshold at exact deterministic round      |
| Reasoning variability          | Repeat runs with same seed but different LLM sampling produce different `peak_deviation` values     | 10-trial `summary.json` distribution                                                    | Rule reproduces to floating-point precision              |
| Emergent caution               | Some LLM personas may voluntarily reduce sizing when narrative becomes extreme                      | `metrics.bias_magnitude` distribution                                                   | Rule maintains config-driven volume ratios                |
| Threshold inconsistency        | `SR` and `AC1` show wider spread; occasional overshoot into `SR < 0.3` or `> 1.2`                   | 10-trial `summary.json → metrics.stabilization_ratio` distribution                      | Rule always sits in [0.4, 0.8]                            |
| Schema robustness              | Strict parser rejects malformed decisions; hold rate should stay near zero                          | Aggregate hold rate from decision payloads                                              | Rule always produces valid orders                         |

All quantitative comparisons should be based on 10 independent trials
reported as mean ± std with Mann-Whitney U tests, per `analysis-bases.md §5`.

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                        | Phenomenon Clarity | Recommended Use              |
|--------------|----------------------------------------------------------------------------|--------------------|------------------------------|
| 100          | Bias episode visible; persona effects clearest in early rounds             | Medium             | Standard single-trial runs   |
| 200          | Complete bias/correction; stable metric means over trials                  | High               | Publication runs             |
| 500          | LLM cost dominates; use only for load/latency profiling                     | Low per trial      | Rare                         |

### Agent Count Scaling

| Agent Count      | Expected Observable                                                   | Environment Dynamics                                     |
|------------------|-----------------------------------------------------------------------|----------------------------------------------------------|
| 10 (min viable)  | Individual persona differences dominate; volume shares volatile        | Persona parse errors visible                             |
| 20 (recommended) | Standard population; channel shares stabilize                          | Reference configuration                                  |
| 40+              | LLM cost dominates runtime; volume shares smooth                       | Approaches Rule in aggregate                             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                | Change | Expected Effect on This Variant's Analysis                                                                             |
|------------------------------------------|--------|-----------------------------------------------------------------------------------------------------------------------|
| `temperature` (LLM)                      | +50%   | Wider metric distributions; more persona-inconsistent order flow; possible `SR` runaway                                |
| `temperature` (LLM)                      | −50%   | Metrics collapse toward Rule; less narrative variety                                                                   |
| Persona prompt phrasing                  | Any    | Directly shifts channel share; test that recency/media/rational separation remains intact                              |
| `RecentEventOverweighter.recency_weight` | +50%   | Higher `ABM`; LLM personas amplify accordingly but not exactly as Rule                                                 |
| Mean reversion (`γ`)                     | +50%   | Correction faster; LLM personas may adapt or overshoot                                                                 |

## §6 Output Files Reference

`LLM/analysis.py` imports the Rule analysis pipeline. Outputs are in
`EXPERIMENT/AvailabilityBias/LLM/analysis/`.

| Output File                                | Generated By                                    | Contents                                                                                                                    | How to Interpret                                                                                                    |
|--------------------------------------------|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| `summary.json`                             | shared Rule analysis                            | `metrics.peak_deviation`, `bias_persistence`, `bias_magnitude`, `return_autocorr_lag1`, `stabilization_ratio`, `agent_type_volume`, `validation.*` | Compare distributions to Rule's deterministic values; check that median is close and that variance is meaningfully larger |
| `00_investor_bids.png`                     | shared Rule analysis                            | Market price + individual investor bids                                                                                     | Persona differentiation should be visible in bid trajectories; recency/media bidders overshoot                       |
| `01_availability_bias_dynamics.png`        | shared Rule analysis                            | Price + deviation curve                                                                                                     | Peak `PDF` between 5–15% expected; onset may shift ±5 rounds vs. Rule                                                |
| `02_availability_bias_analysis.png`        | shared Rule analysis                            | Volume decomposition + rolling AC1                                                                                          | Wider AC1 rolling profile; SR may deviate from Rule's tight band                                                    |
| `03_summary.png`                           | shared Rule analysis                            | Fit summary                                                                                                                | Overall validation score should still pass §6.2 targets on average                                                  |

## §7 Cross-Variant Comparison Notes

LLM is the persona-only cell; it isolates the effect of LLM reasoning without
rule anchors or knowledge retrieval (`analysis-bases.md §5`).

| Comparison Axis           | LLM's Expected Position                                     | Reason                                                                                     |
|---------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Onset speed               | More variable than Rule/RuleLLM                             | Persona reasoning shifts crossover round                                                    |
| Peak `PDF`                | Higher variance; mean can exceed Rule                        | Narrative momentum sustains bias longer                                                     |
| Persistence `BPS`         | Wider distribution                                          | Persona reactions vary across trials                                                       |
| Stabilization `SR`        | Can drift outside [0.4, 0.8]                                | Systematic/value personas may be "contaminated" by recency narrative                        |
| Behavioral realism        | Richer than Rule; comparable to RuleLLM                     | Persona reasoning traces expose salience heuristics                                        |
| Reproducibility           | Lowest of the four variants                                 | Model sampling + API variance                                                              |
