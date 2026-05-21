# MentalAccounting LLM — Analysis Specification

## §1 Overview

The LLM analysis uses the same standard MentalAccounting metric pipeline as the Rule variant while adding attention to parsed reasoning and API decision-contract integrity.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Account-Level Turnover (ALT) | `calculate_metrics(data)` from order payloads | `analysis-bases.md §2 Metric: Account-Level Turnover` |
| House-Money Risk Shift (HMRS) | `calculate_metrics(data)` from action patterns | `analysis-bases.md §2 Metric: House-Money Risk Shift` |
| Sunk-Cost Holding Ratio (SCHR) | `calculate_metrics(data)` from losing-position actions | `analysis-bases.md §2 Metric: Sunk-Cost Holding Ratio` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` from prices and fundamentals | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Behavioral Price Impact (BPI) | `calculate_metrics(data)` from net demand and price response | `analysis-bases.md §2 Metric: Behavioral Price Impact` |
| Return Volatility (RV) | `calculate_metrics(data)` from price returns | `analysis-bases.md §2 Metric: Return Volatility` |
| Realization Frequency Ratio (RFR) | `calculate_metrics(data)` from gain/loss realization | `analysis-bases.md §2 Metric: Realization Frequency Ratio` |

## §3 Analysis Dimensions

Analysis compares persona-consistent actions, canonical order validity, reasoning text, market deviation, and portfolio outcomes by investor type.

## §4 Phase Analysis

The run is evaluated across initialization, persona activation, repeated decision cycles, and stabilization. Reasoning traces are interpreted alongside ALT, SCHR, HMRS, and RFR.

## §5 Cross-Variant Comparison

LLM results are compared with Rule to identify whether persona-only reasoning preserves mental-accounting structure while introducing stochastic variation in timing and sizing.

## §6 Expected Results

### §6.1 Stylised Facts

Valid LLM runs should produce parseable analysis text, nonzero trading activity, account-framing behavior, and bounded portfolio evolution.

### §6.2 Calibration Targets

Calibration follows `analysis-bases.md §6.2`; deviations are interpreted against the Rule baseline and expected API variability.

### §6.3 Cross-Variant Predictions

LLM should show richer explanations than Rule, less deterministic trade timing, and similar directional mental-accounting effects when the decision contract is satisfied.

### §6.4 Validation Failure Signs

Repeated invalid decision JSON, missing reasoning, absent bid prices, zero total volume, or broken market histories indicate invalid output.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_mentalaccounting_dynamics.png`, `02_mentalaccounting_analysis.png`, and `03_summary.png`.
