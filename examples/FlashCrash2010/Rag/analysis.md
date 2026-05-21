# 2010 Flash Crash Rag Analysis Plan

## §1 Objectives

This analysis checks whether the Rag variant produces a complete, analyzable 2010 Flash Crash trajectory while preserving the RuleLLM order schema, class-mapped `agent_type`, and retrieval audit artifact contract.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Maximum Drawdown | `def max_drawdown(price_history: list) -> float` | `analysis-bases.md §2` |
| Depth Collapse Ratio | `def depth_collapse_ratio(depth_history: list, base_depth: float) -> float` | `analysis-bases.md §2` |
| Spread Widening Factor | `def spread_widening_factor(spread_history: list, normal_spread: float = 0.0001) -> float` | `analysis-bases.md §2` |
| HFT Withdrawal Rounds | `def hft_withdrawal_rounds(hft_orders_by_round: list, withdrawal_threshold: int = 0) -> int` | `analysis-bases.md §2` |
| Cascade Trigger Rounds | `def cascade_trigger_rounds(stoploss_orders_by_round: list) -> list` | `analysis-bases.md §2` |
| Recovery Time | `def recovery_time(price_history: list, trough_round: int, fundamental: float, threshold: float = 0.02) -> int` | `analysis-bases.md §2` |
| RAG Knowledge Effect | `def analyze_rag_knowledge_effect(records: dict) -> dict` | `analysis-bases.md §7` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. Rag review should additionally inspect retrieval failures, conservative liquidity defaults, parse failures, and whether class-mapped HFT orders are present.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: normal depth, trigger, cascade, trough, and recovery. Each phase should be measured with state, order-flow, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on drawdown, depth collapse, spread widening, HFT withdrawal timing, stop-loss waves, recovery time, retrieval coverage, and structural quality.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and mechanism-specific behavior consistent with `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`, `01_flashcrash2010_dynamics.png`, `02_flashcrash2010_analysis.png`, `03_summary.png`, and `rag_stats.json`.
