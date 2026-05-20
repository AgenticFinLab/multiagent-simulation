# LUNACollapse Rag — Analysis Guide

## §1 Objectives

This guide traces Rag analysis to `../analysis-bases.md`. Rag tests whether
retrieved stablecoin and DeFi crisis context changes action timing, panic
intensity, or stabilization relative to RuleLLM.

## §2 Metric Mapping

| analysis-bases.md Metric | Implementation |
|---|---|
| §2.1 Price Deviation | `analysis.py` reuses Rule `calculate_metrics()` on the Rag record path |
| §2.2 Maximum Drawdown | `calculate_metrics()` records the largest one-round return drop |
| §2.3 Crash Velocity | Interpreted from the most negative one-round return |
| §2.4 Sell Pressure Share | Level-2 audit attributes sell orders to Rag agent identities |
| §2.5 Stabilization Ratio | Level-2 audit compares ValueBuyer demand against destabilizing sell volume |
| §2.6 Collapse Onset Round | Level-2 audit finds the first material negative-deviation round |
| §2.7 Volume Acceleration | Level-2 audit checks whether volume accelerates with crisis context |

## §3 Analysis Dimensions

Assess retrieval health, prompt-output validity, fallback count, sell-pressure
timing, and whether retrieved context amplifies or dampens RuleLLM behavior.

## §4 Phase Analysis

Rag should follow stable, peg-stress, death-spiral, stabilization-attempt, and
late recovery/collapse phases. Retrieved context should be inspected when phase
timing differs sharply from RuleLLM.

## §5 Cross-Variant Comparison

Compare Rag first against RuleLLM to isolate the knowledge effect, then against
Rule and LLM for market-level consequences.

## §6 Expected Results

Accepted samples must complete full rounds, use valid RAG assets and embedding
config, preserve canonical decision JSON, and report any malformed-output or
retrieval fallback in Level-2 quality notes.

## §7 Visualization Catalogue

Plot price/fundamental, deviation, retrieval/fallback counts, agent sell-pressure
shares, stabilization ratio, and cross-variant drawdown.
