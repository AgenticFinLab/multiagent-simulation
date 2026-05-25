# Market Crash Rag Analysis Plan

## §1 Objectives

Verify that the retrieval-augmented variant preserves crash structure while
recording usable per-round RAG evidence.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Maximum drawdown | `def compute_maximum_drawdown(prices: list[float]) -> float` | `analysis-bases.md §2.1` |
| Largest one-round drop | `def compute_largest_one_round_drop(prices: list[float]) -> float` | `analysis-bases.md §2.2` |
| Volatility spike | `def compute_volatility_spike(returns: list[float], window: int) -> float` | `analysis-bases.md §2.3` |
| Forced-selling pressure | `def compute_forced_selling_pressure(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Liquidity withdrawal | `def compute_liquidity_withdrawal(orders: list[dict], liquidity: list[float]) -> float` | `analysis-bases.md §2.5` |
| Panic contribution | `def compute_panic_contribution(orders: list[dict], returns: list[float]) -> float` | `analysis-bases.md §2.6` |
| Bottom-fisher absorption | `def compute_bottom_fisher_absorption(orders: list[dict]) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze market path, investor behavior, liquidity provision, and retrieval
coverage together.

## §4 Phase Analysis

Pre-crash positioning, stress onset, deleveraging cascade, liquidity stress,
and stabilization or failed recovery.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare Rag against RuleLLM and isolate whether
retrieved crisis knowledge changes urgency, liquidity decisions, or stabilization
timing.

## §6 Expected Results And Validation Criteria

Successful runs should complete 200 rounds, preserve the RuleLLM market
contract, record `rag_context` in player turns, and produce `rag_stats.json`.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
