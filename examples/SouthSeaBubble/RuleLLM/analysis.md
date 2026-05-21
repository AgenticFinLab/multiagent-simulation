# SouthSeaBubble RuleLLM Analysis Plan

## §1 Objectives

The RuleLLM analysis checks whether explicit prompt rules preserve retained
threshold behavior while allowing natural-language bubble reasoning.

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

Review rule fidelity, bubble/correction timing, role attribution, reasoning
consistency, and parser fallback rate.

## §4 Phase Analysis

Use `analysis-bases.md §4`. RuleLLM should preserve Rule phase ordering unless
stochastic output changes quantities within documented role constraints.

## §5 Cross-Variant Comparison

Compare RuleLLM with Rule for threshold fidelity and with LLM for reduced schema
and mechanism drift.

## §6 Expected Results and Validation Criteria

A full RuleLLM sample should complete 200 rounds, preserve current-market
quantity payloads, and keep parser fallback within the documented quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_southseabubble_dynamics.png`, `02_southseabubble_analysis.png`, and
`03_summary.png`.
