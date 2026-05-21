# OverconfidenceBias LLM — Analysis Specification

## §1 Overview

The LLM analysis uses the standard OverconfidenceBias metric pipeline while checking model reasoning and decision-contract validity.

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

Analysis compares persona consistency, parse quality, canonical order fields, turnover, price deviation, volatility, and portfolio outcomes.

## §4 Phase Analysis

LLM phases include initialization, persona-conditioned decisions, repeated market feedback, and stabilization or amplification.

## §5 Cross-Variant Comparison

LLM is compared with Rule to determine whether persona-only reasoning preserves overconfidence without hidden fallback behavior.

## §6 Expected Results

### §6.1 Stylised Facts

Valid runs should show parseable reasoning, nonzero biased activity, and bounded market histories.

### §6.2 Calibration Targets

Targets follow `analysis-bases.md §6.2` with additional review of parse failures and decision quality.

### §6.3 Cross-Variant Predictions

LLM should show more variable order timing than Rule while preserving role-level direction.

### §6.4 Validation Failure Signs

Invalid JSON, missing `bid_price`, absent reasoning, zero volume, or broken price histories indicate failure.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_overconfidencebias_dynamics.png`, `02_overconfidencebias_analysis.png`, and `03_summary.png`.
