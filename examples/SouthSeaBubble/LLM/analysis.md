# SouthSeaBubble LLM Analysis Plan

## §1 Objectives

The LLM analysis checks whether persona-conditioned API decisions preserve the
South Sea bubble mechanism while changing narrative conviction, quantity, and
reasoning.

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

Review mechanism preservation, role attribution, reasoning consistency, parser
fallback rate, and current-market quantity payload quality.

## §4 Phase Analysis

Use the phase framework in `analysis-bases.md §4` and compare LLM against Rule
for amplification or weakening of narrative boom and correction phases.

## §5 Cross-Variant Comparison

Compare LLM with Rule for mechanism drift and with RuleLLM for the stabilizing
effect of explicit prompt rules.

## §6 Expected Results and Validation Criteria

A full LLM sample should complete 200 rounds with valid `action`, `quantity`,
`agent_type`, `reasoning`, and explicit parser fallback fields.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_southseabubble_dynamics.png`, `02_southseabubble_analysis.png`, and
`03_summary.png`.
