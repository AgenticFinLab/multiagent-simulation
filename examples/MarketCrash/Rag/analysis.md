# Market Crash Rag Analysis Plan

## §1 Objectives

Verify that the retrieval-augmented variant preserves crash structure while
recording usable per-round RAG evidence.

## §2 Core Metrics

| Metric | Interpretation |
|---|---|
| Maximum drawdown | Crash severity |
| Largest one-round drop | Crash velocity |
| Volatility spike | Stress amplification |
| Liquidity withdrawal | `provides_liquidity` participation under stress |
| Bottom-fisher absorption | Stabilizing demand after discount triggers |
| Retrieval quality | Success versus fallback retrieval rounds in `rag_stats.json` |

## §3 Analysis Dimensions

Analyze market path, investor behavior, liquidity provision, and retrieval
coverage together.

## §4 Phase Analysis

Pre-crash positioning, stress onset, deleveraging cascade, liquidity stress,
and stabilization or failed recovery.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to determine whether retrieved crisis knowledge
changes urgency, liquidity decisions, or stabilization timing.

## §6 Expected Results And Validation Criteria

Successful runs should complete 200 rounds, preserve the RuleLLM market
contract, record `rag_context` in player turns, and produce `rag_stats.json`
without placeholder-only analysis outputs.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
