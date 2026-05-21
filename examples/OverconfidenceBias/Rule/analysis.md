# OverconfidenceBias Rule — Analysis Specification

## §1 Overview

The Rule analysis evaluates whether deterministic overconfidence produces excess turnover, signal overreaction, self-attribution reinforcement, bounded price deviation, volatility, and portfolio performance gaps.

## §2 Metric Implementation

| Metric | Function / Source | Root Reference |
|---|---|---|
| Excess Turnover (ET) | `calculate_metrics(data)` from order payloads | `analysis-bases.md §2 Metric: Excess Turnover` |
| Signal Overreaction (SO) | `calculate_metrics(data)` from quantity and deviation | `analysis-bases.md §2 Metric: Signal Overreaction` |
| Confidence Reinforcement Activity (CRA) | `calculate_metrics(data)` from SelfAttributor payloads | `analysis-bases.md §2 Metric: Confidence Reinforcement Activity` |
| Rational Benchmark Deviation (RBD) | `calculate_metrics(data)` from price/fundamental histories | `analysis-bases.md §2 Metric: Rational Benchmark Deviation` |
| Return Volatility (RV) | `calculate_metrics(data)` from price returns | `analysis-bases.md §2 Metric: Return Volatility` |
| Portfolio Performance Gap (PPG) | `calculate_metrics(data)` from portfolio values | `analysis-bases.md §2 Metric: Portfolio Performance Gap` |

## §3 Analysis Dimensions

Analysis compares agent types, turnover, order sizes, price deviation, volume, portfolio values, and canonical order completeness.

## §4 Phase Analysis

Runs are read as initialization, biased-order activation, market-feedback amplification, and stabilization or persistence phases.

## §5 Cross-Variant Comparison

Rule is the deterministic baseline used to interpret LLM, RuleLLM, and Rag variability.

## §6 Expected Results

### §6.1 Stylised Facts

Biased agents should trade more than calibrated agents, contrarian flow should oppose large deviations, and price paths should remain bounded.

### §6.2 Calibration Targets

Targets follow `analysis-bases.md §6.2`: ET above 1, nonzero biased activity, bounded RBD, and nonzero volume.

### §6.3 Cross-Variant Predictions

Rule should be the most mechanically stable variant and should show the cleanest interpretation of config-driven overconfidence.

### §6.4 Validation Failure Signs

Zero volume, absent canonical order fields, missing fundamental history, or unbounded price divergence indicate invalid output.

## §7 Visualization Catalogue

The analysis writes `summary.json`, `00_investor_bids.png`, `01_overconfidencebias_dynamics.png`, `02_overconfidencebias_analysis.png`, and `03_summary.png`.
