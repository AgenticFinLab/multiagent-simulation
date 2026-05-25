# LUNACollapse RuleLLM — Analysis Guide

## §1 Objectives

This guide traces RuleLLM analysis to `../analysis-bases.md`. RuleLLM tests
whether LLM reasoning can preserve the configured death-spiral rules while still
producing natural-language reasoning and bounded variation.

## §2 Metric Mapping

| analysis-bases.md Metric | Implementation |
|---|---|
| §2.1 Price Deviation | `analysis.py` reuses Rule `calculate_metrics()` on the RuleLLM record path |
| §2.2 Maximum Drawdown | `calculate_metrics()` records the largest one-round return drop |
| §2.3 Crash Velocity | Interpreted from the most negative one-round return |
| §2.4 Sell Pressure Share | Post-run order aggregation attributes sell volume by RuleLLM agent identity |
| §2.5 Stabilization Ratio | Post-run aggregation compares ValueBuyer buy volume with panic sell volume |
| §2.6 Collapse Onset Round | Derived from the first material negative-deviation breach |
| §2.7 Volume Acceleration | Post-run checks volume acceleration during collapse phases |

## §3 Analysis Dimensions

Compare rule adherence, parse quality, threshold timing, sell-pressure share,
and stabilization behavior against the deterministic Rule baseline.

## §4 Phase Analysis

RuleLLM should follow the same phase order as Rule. Differences should be
limited to reasoning phrasing or bounded order-size variation rather than
opposite trading signs.

## §5 Cross-Variant Comparison

RuleLLM sits between Rule and LLM: it should be closer to Rule on action timing
while still exposing LLM reasoning quality for audit.

## §6 Expected Results

Valid outputs must complete full rounds, show low malformed-output retry
rates, preserve canonical JSON fields, and keep thresholds aligned with
`configs/LUNACollapse/RuleLLM/players.yml`.

## §7 Visualization Catalogue

Plot price/fundamental, deviation, rule-adherence timing, malformed-output
counts, sell-pressure shares, stabilization ratio, and cross-variant drawdown.
