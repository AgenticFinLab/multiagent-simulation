# Volmageddon Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both Volmageddon market quality and retrieval quality.
It must verify the same feedback mechanism as RuleLLM while also reporting
whether each agent actually received non-empty retrieved context.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Volatility spike magnitude | `def compute_vol_spike_magnitude(vol_series: list[float]) -> float` | `analysis-bases.md §2.1` |
| Rebalance pressure | `def compute_rebalance_pressure(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Short-vol covering | `def compute_short_vol_covering(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Equity de-risking volume | `def compute_equity_derisking_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Arbitrage stabilization | `def compute_arbitrage_stabilization(orders: list[dict], deviation_series: list[float]) -> float` | `analysis-bases.md §2.5` |
| Spike onset round | `def compute_spike_onset(vol_series: list[float], threshold: float) -> int` | `analysis-bases.md §2.6` |
| Feedback intensity | `def compute_feedback_intensity(vol_series: list[float], orders: list[dict]) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review market feedback, role attribution, parser fallback rate, retrieval
success rate, retrieved-context coverage by agent, and whether RAG changes
quantity decisions without violating the current-market schema.

## §4 Phase Analysis

Use `analysis-bases.md §4`. Retrieval context should be examined by phase:
historical Volmageddon or inverse-ETN context is most relevant in trigger and
feedback phases, while hedging and arbitrage context may matter in stabilization
phases.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to isolate the effect of retrieved knowledge. Compare
against Rule and LLM for spike timing, feedback intensity, and quality metrics.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid quantity orders,
include `rag_context` for investor decisions, write `rag_stats.json`, and keep
retrieval failures and parser fallbacks within documented quality gates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volmageddon_dynamics.png`, `02_volmageddon_analysis.png`,
`03_summary.png`, and Rag-specific `rag_stats.json`.
