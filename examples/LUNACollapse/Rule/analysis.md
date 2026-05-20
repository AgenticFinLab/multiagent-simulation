# LUNACollapse Rule — Analysis Guide

## §1 Objectives

This guide traces the Rule variant analysis back to `../analysis-bases.md`.
The Rule run is the deterministic baseline for measuring whether threshold
redemptions, arbitrage, liquidations, yield exits, and contrarian buying
produce a stablecoin death spiral.

## §2 Metric Mapping

| analysis-bases.md Metric | Implementation |
|---|---|
| §2.1 Price Deviation | `calculate_metrics()` computes `(price - fundamental) / fundamental` from market records |
| §2.2 Maximum Drawdown | `calculate_metrics()` records the largest one-round return drop as `max_drawdown_pct` |
| §2.3 Crash Velocity | Approximated by the most negative one-round return in `price_metrics.max_drawdown_pct` |
| §2.4 Sell Pressure Share | Requires order-level post-run aggregation by agent identity |
| §2.5 Stabilization Ratio | Requires buy/sell order aggregation by destabilizing and stabilizing agent groups |
| §2.6 Collapse Onset Round | Derived from the first deviation below the configured stress threshold |
| §2.7 Volume Acceleration | Market records expose `volume`; use post-run acceleration checks |

## §3 Analysis Dimensions

Compare Rule results across price path, deviation depth, sell-pressure timing,
stabilization attempts, and full-round completion. Rule should be interpreted as
the baseline implementation of `simulation-bases.md §4`.

## §4 Phase Analysis

Early rounds should stay close to fundamental. Peg stress begins when deviation
crosses the configured redemption/yield thresholds. The death-spiral phase is
identified by accelerating sell pressure and drawdown. Late rounds diagnose
whether ValueBuyer demand can slow or stabilize the decline.

## §5 Cross-Variant Comparison

Use this variant as the reference line for LLM, RuleLLM, and Rag. Deviations in
timing or magnitude should be explained by prompt reasoning or retrieved
knowledge, not by inconsistent thresholds.

## §6 Expected Results

Valid outputs should complete the full configured round count, produce
finite prices and fundamentals, show a meaningful negative deviation episode,
and preserve canonical order records for sell-pressure and stabilization audit.

## §7 Visualization Catalogue

Generate price-versus-fundamental, deviation over time, return series, return
distribution, sell-pressure share, stabilization ratio, and cross-variant
drawdown comparison plots.
