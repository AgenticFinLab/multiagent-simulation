# SouthSeaBubble Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both bubble-mechanism quality and retrieval quality.
It verifies South Sea bubble metrics while ensuring each agent records retrieved
historical context.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Bubble magnitude | `def compute_bubble_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Narrative demand | `def compute_narrative_demand(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Insider timing profit | `def compute_insider_timing_profit(values: list[float]) -> float` | `analysis-bases.md §2.3` |
| Skeptical resistance | `def compute_skeptical_resistance(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Arbitrage correction | `def compute_arbitrage_correction(orders: list[dict]) -> float` | `analysis-bases.md §2.5` |
| Crash round | `def compute_crash_round(prices: list[float], drawdown_threshold: float) -> int` | `analysis-bases.md §2.6` |
| Agent attribution | `def compute_agent_attribution(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review bubble severity, retrieval coverage, parser fallback rate, narrative
demand, skeptical/arbitrage correction, and role attribution.

## §4 Phase Analysis

Use `analysis-bases.md §4`. Retrieved bubble-history context is most relevant
during narrative boom, peak overpricing, and correction phases.

## §5 Cross-Variant Comparison

Compare Rag with RuleLLM to isolate the effect of retrieved historical bubble
context.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid quantity orders,
include `rag_context`, write `rag_stats.json`, and keep retrieval failures and
parser fallbacks within quality gates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_southseabubble_dynamics.png`, `02_southseabubble_analysis.png`,
`03_summary.png`, and Rag-specific `rag_stats.json`.
