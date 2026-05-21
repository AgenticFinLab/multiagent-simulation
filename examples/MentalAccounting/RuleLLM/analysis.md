# MentalAccounting RuleLLM — Analysis Specification

## §1 Overview

The RuleLLM analysis evaluates whether explicit decision rules plus LLM reasoning preserve the deterministic mental-accounting mechanisms while providing parseable calculation narratives.

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

## §3 Analysis Dimensions

Analysis compares rule adherence, decision-contract validity, reasoning content, price/fundamental deviation, and portfolio outcomes.

## §4 Phase Analysis

RuleLLM phases are initialization, rule-conditioned reasoning, market feedback, and stabilization. ALT, HMRS, SCHR, RFR, RBD, BPI, and RV are interpreted in each phase.

## §5 Cross-Variant Comparison

RuleLLM should sit between Rule and LLM: more structured than persona-only LLM, but with richer reasoning than deterministic Rule.

## §6 Expected Results

### §6.1 Stylised Facts

Expected outputs include valid JSON decisions, explicit reasoning, account-framing effects, house-money sensitivity, and bounded market deviation.

### §6.2 Calibration Targets

Targets follow `analysis-bases.md §6.2`; comparisons emphasize whether explicit rules keep metrics near the Rule baseline.

### §6.3 Cross-Variant Predictions

RuleLLM should reduce persona-only variance relative to LLM while retaining API-generated analysis text.

### §6.4 Validation Failure Signs

Invalid JSON contracts, absent analysis text, missing canonical order fields, or zero trading activity indicate failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_mentalaccounting_dynamics.png`, `02_mentalaccounting_analysis.png`, and `03_summary.png`.
