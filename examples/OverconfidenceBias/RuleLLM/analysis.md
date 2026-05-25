# OverconfidenceBias RuleLLM — Analysis Specification

## §1 Overview

The RuleLLM analysis evaluates explicit rule adherence, reasoning quality, and standard market/portfolio outcomes.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Excess Turnover (ET) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Excess Turnover` |
| Signal Overreaction (SO) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Signal Overreaction` |
| Confidence Reinforcement Activity (CRA) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Confidence Reinforcement Activity` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Return Volatility (RV) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Return Volatility` |
| Portfolio Performance Gap (PPG) | `calculate_metrics(data)` | `analysis-bases.md §2 Metric: Portfolio Performance Gap` |

## §3 Analysis Dimensions

Analysis compares rule consistency, reasoning text, canonical orders, turnover, deviation, volatility, and portfolio outcomes.

## §4 Phase Analysis

RuleLLM phases are initialization, rule-conditioned reasoning, market feedback, and stabilization or amplification.

## §5 Cross-Variant Comparison

RuleLLM should stay closer to Rule than LLM while adding model-generated explanations.

## §6 Expected Results

### §6.1 Stylised Facts

Valid runs should show overconfidence-consistent order flow, explicit reasoning, and complete market histories.

### §6.2 Calibration Targets

Targets follow `analysis-bases.md §6.2`; rule adherence should keep outcomes close to Rule baseline.

### §6.3 Cross-Variant Predictions

RuleLLM should reduce persona-only variance while retaining richer explanations.

### §6.4 Validation Failure Signs

Invalid decision JSON, missing canonical fields, or rule-inconsistent sustained behavior indicates failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_overconfidencebias_dynamics.png`, `02_overconfidencebias_analysis.png`, and `03_summary.png`.
