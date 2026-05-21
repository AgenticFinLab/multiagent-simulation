# Reversal Effect Rag Analysis Plan

## §1 Objectives

This analysis checks whether retrieved domain knowledge changes reversal timing
or liquidity provision while preserving RuleLLM's structured order and market
contracts.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Overshoot magnitude | `def compute_overshoot_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Reversal return | `def compute_reversal_return(prices: list[float], onset: int, extreme: int) -> float` | `analysis-bases.md §2.2` |
| Contrarian order share | `def compute_contrarian_order_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Liquidity depth | `def compute_liquidity_depth(orders: list[dict], base_liquidity: float) -> float` | `analysis-bases.md §2.5` |
| API quality | `def compute_api_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review reversal dynamics, order flow, liquidity provision, parse quality,
conservative liquidity defaults, and retrieval coverage. `rag_stats.json` should
identify whether each player actually received non-empty retrieval context.

## §4 Phase Analysis

Analyze whether retrieved context changes the overreaction buildup, correction
phase, or terminal stabilization relative to RuleLLM.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to isolate retrieval effects. Compare against Rule
and LLM for broader mechanism preservation and API robustness.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, order-level liquidity
values, `rag_context` fields, and a `rag_stats.json` retrieval audit.
Deterministic RAG configuration or embedding failures invalidate the sample.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_reversaleffect_dynamics.png`, `02_reversaleffect_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
