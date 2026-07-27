# AvailabilityBias Rule — Analysis Documentation

## §1 Overview

| Item            | Description                                                                                                                        |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------|
| Variant         | Rule                                                                                                                               |
| Analysis Script | `examples/AvailabilityBias/Rule/analysis.py`                                                                                       |
| Basis           | `../analysis-bases.md`                                                                                                             |
| Outputs         | `summary.json`, `00_investor_bids.png`, `01_availability_bias_dynamics.png`, `02_availability_bias_analysis.png`, `03_summary.png` |

## §2 Metric Implementation

| Metric                           | Function                                                    | analysis-bases.md Ref                         | Rule-Specific Notes                                     |
|----------------------------------|-------------------------------------------------------------|-----------------------------------------------|---------------------------------------------------------|
| Price Deviation from Fundamental | `_compute_peak_deviation(...)`                              | `§2 Metric: Price Deviation from Fundamental` | Primary bias-depth statistic.                           |
| Bias Persistence Score           | `_compute_bias_persistence(...)`                            | `§2 Metric: Bias Persistence Score`           | Detects sustained availability episodes.                |
| Availability Bias Magnitude      | volume decomposition in `_compute_stabilization_ratio(...)` | `§2 Metric: Availability Bias Magnitude`      | Interpreted through biased/rational volume.             |
| Return Autocorrelation           | `_compute_rolling_ac1(...)`                                 | `§2 Metric: Return Autocorrelation`           | Detects momentum and reversal.                          |
| Agent-Type Volume Share          | `_load_data(...)` investor payloads                         | `§2 Metric: Agent-Type Volume Share`          | Separates recency, media, rational, and noise channels. |
| Stabilization Ratio              | `_compute_stabilization_ratio(...)`                         | `§2 Metric: Stabilization Ratio`              | Measures rational correction during bias episodes.      |
| RAG Retrieval Failure Rate       | not applicable                                              | `§2 Metric: RAG Retrieval Failure Rate`       | Rule variant has no retrieval.                          |

## §3 Analysis Dimensions

| Dimension                   | Rule Interpretation                                                      |
|-----------------------------|--------------------------------------------------------------------------|
| Bias-Induced Price Dynamics | Rule provides the deterministic formula baseline.                        |
| Channel Attribution         | Recency and media channels are directly traceable to config parameters.  |
| Stabilization Effectiveness | SystematicAnalyst and ValueTrader correction is exact and interpretable. |
| Cross-Variant Comparison    | Rule is the reference for LLM, RuleLLM, and Rag deviations.              |

## §4 Variant-Specific Observable Phenomena

The Rule variant realizes availability bias through deterministic weighting of
recent events and media volume against systematic and value channels. Behavior
is fully reproducible under a fixed seed; only NoiseTrader introduces stochasticity.

| Phenomenon                    | Description                                                                                                | How to Observe                                                                          | Contrast with Baseline |
|-------------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|------------------------|
| Deterministic bias onset      | `|PDF|` crosses 5% at the round when accumulated recency/media pressure first exceeds ValueTrader anchor    | `01_availability_bias_dynamics.png` deviation curve crossing the 5% guideline           | This is the baseline   |
| Threshold-locked persistence  | `BPS` reflects an exact count of rounds in which all 5 lagged deviations exceed 5%                          | `summary.json → metrics.bias_persistence`                                               | This is the baseline   |
| Analytic magnitude            | `ABM` reproduces the config-driven ratio of biased to rational order sizes                                  | `02_availability_bias_analysis.png` volume panel                                        | This is the baseline   |
| Reversal-consistent AC1       | Positive rolling AC1 during bias episode, near zero or negative during correction                          | `summary.json → metrics.return_autocorr_lag1` (via `_compute_rolling_ac1`)              | This is the baseline   |
| Partial-correction stabilization | `SR` sits within 0.4–0.8 by construction of `SystematicAnalyst.max_size` and `ValueTrader.max_size`      | `summary.json → metrics.stabilization_ratio`                                            | This is the baseline   |

Rule is deterministic given the seed. Any drift in these metrics across
repeated runs indicates a non-seeded RNG or investor state bug.

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                              | Phenomenon Clarity | Recommended Use   |
|--------------|----------------------------------------------------------------------------------|--------------------|-------------------|
| 100          | Bias onset visible; persistence estimate noisy                                   | Low                | Smoke test        |
| 200          | Full episode plus correction; matches `analysis-bases.md §6.2` targets           | High               | Standard runs     |
| 500          | Multiple bias/reversal cycles; robust `BPS` estimate                              | Very High          | Sensitivity grid  |

### Agent Count Scaling

| Agent Count       | Expected Observable                                                          | Environment Dynamics                                     |
|-------------------|------------------------------------------------------------------------------|----------------------------------------------------------|
| 10 (min viable)   | Bias episode still forms; volume shares noisy                                | Individual agents drive channel share                    |
| 20 (recommended)  | Clean recency vs. media vs. rational split; `ATV` stable                     | Standard configuration                                   |
| 40+               | Volume shares near design targets; deterministic behaviour dominates          | Bias phenomenon fully expressed                          |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                             | Change | Expected Effect on This Variant's Analysis                                                                        |
|-------------------------------------------------------|--------|-------------------------------------------------------------------------------------------------------------------|
| `RecentEventOverweighter.recency_weight`              | +50%   | Larger `ABM`; higher peak `PDF`; longer `BPS`                                                                     |
| `RecentEventOverweighter.recency_weight`              | −50%   | Bias may fail to form (peak `PDF < 3%`)                                                                           |
| `MediaInfluencedTrader.media_response`                | +50%   | Positive AC1 wider; peak `PDF` deeper; risk of `SR < 0.3`                                                         |
| `SystematicAnalyst.correction_gain` / `ValueTrader.anchor_weight` | +50% | `SR` rises; `BPS` shortens; `PDF` peak lower                                                                     |
| Mean reversion (`γ`)                                  | +50%   | Faster convergence toward fundamental; shorter correction phase                                                   |

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/AvailabilityBias/Rule/analysis/`.

| Output File                                | Generated By                                          | Contents                                                                                             | How to Interpret                                                                                                            |
|--------------------------------------------|-------------------------------------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `summary.json`                             | inline block in `Rule/analysis.py`                    | `metrics.peak_deviation`, `metrics.bias_persistence`, `metrics.bias_magnitude`, `metrics.return_autocorr_lag1`, `metrics.stabilization_ratio`, `metrics.agent_type_volume`, `validation.*` | Compare each metric to §6 targets: peak 5–15%, persistence ≥ 0.10, AC1 in [0.20, 0.40], SR in [0.4, 0.8]                    |
| `00_investor_bids.png`                     | inline block in `Rule/analysis.py`                    | Market-price curve plus every investor bid                                                           | Recency/media bidders should overshoot fundamental during bias episodes; systematic/value bidders anchor near fundamental    |
| `01_availability_bias_dynamics.png`        | inline block in `Rule/analysis.py`                    | Price + deviation path with 5% guideline                                                             | Bias episodes visible as `|PDF|` above 5%; correction visible as deviation returning inside band                             |
| `02_availability_bias_analysis.png`        | inline block in `Rule/analysis.py`                    | Volume decomposition by channel plus rolling AC1                                                     | Biased channels should carry 30–60% of volume during episodes; AC1 positive during bias, near zero during correction        |
| `03_summary.png`                           | inline block in `Rule/analysis.py`                    | Fit summary: score bars, return distribution                                                         | Overall validation score reflects match to §6 targets                                                                       |

## §7 Cross-Variant Comparison Notes

Rule is the reference for LLM, RuleLLM, and Rag runs of AvailabilityBias
(`analysis-bases.md §5` and `§6.3`).

| Comparison Axis           | Rule's Expected Position                                     | Reason                                                                                     |
|---------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Bias episode onset speed  | Fastest and reproducible                                     | Thresholds and weights are constants                                                        |
| Peak deviation `PDF`      | Consistent (tight distribution)                              | No sampling variance                                                                        |
| Persistence `BPS`         | Predictable from `γ`, `recency_weight`, `media_response`     | Deterministic transitions                                                                   |
| Stabilization `SR`        | Within [0.4, 0.8] by construction                            | Systematic/value volumes set by config                                                      |
| Behavioral realism        | Mechanistic; no persona reasoning                            | No LLM reasoning traces                                                                     |
| Reproducibility           | Highest                                                      | Only NoiseTrader is stochastic                                                              |
