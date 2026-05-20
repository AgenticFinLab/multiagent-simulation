# LUNACollapse LLM — Analysis Guide

## §1 Objectives

This guide traces LLM analysis to `../analysis-bases.md`. The LLM variant tests
whether persona-driven discretionary decisions reproduce or distort the
death-spiral baseline established by Rule.

## §2 Metric Mapping

| analysis-bases.md Metric | Implementation |
|---|---|
| §2.1 Price Deviation | `analysis.py` reuses Rule `calculate_metrics()` on the LLM record path |
| §2.2 Maximum Drawdown | `calculate_metrics()` records the largest one-round return drop |
| §2.3 Crash Velocity | Interpreted from the most negative one-round return |
| §2.4 Sell Pressure Share | Post-run order aggregation attributes sell orders to LLM agent identities |
| §2.5 Stabilization Ratio | Post-run aggregation compares ValueBuyer buy volume with destabilizing sell volume |
| §2.6 Collapse Onset Round | Derived from the first material negative-deviation round |
| §2.7 Volume Acceleration | Post-run checks whether market volume accelerates during collapse |

## §3 Analysis Dimensions

Evaluate price path, prompt-output legality, retry frequency, sell/buy balance,
and whether discretionary reasoning delays or amplifies the Rule baseline.

## §4 Phase Analysis

Compare LLM phase timing to Rule: stable, peg stress, panic selling,
stabilization attempt, and residual recovery or collapse. Any malformed-output
retry must be logged and included in quality notes.

## §5 Cross-Variant Comparison

LLM may differ most from Rule because it uses persona reasoning rather than
explicit formulas. RuleLLM and Rag should help distinguish prompt rule anchoring
from discretionary behavior.

## §6 Expected Results

Valid LLM outputs must complete the full configured round count, contain
valid `<decision>` JSON for each accepted action, avoid silent fallback, and
produce finite prices, positions, and cash balances.

## §7 Visualization Catalogue

Use price-versus-fundamental, deviation bands, retry/failure counts, agent
sell-pressure shares, ValueBuyer stabilization ratio, and cross-variant
drawdown plots.
