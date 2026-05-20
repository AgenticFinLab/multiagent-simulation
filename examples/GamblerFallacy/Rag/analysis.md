# GamblerFallacy Rag — Analysis Guide

## §1 Analysis Objectives

RAG analysis follows `../analysis-bases.md §1` and adds retrieval-quality review: whether retrieved knowledge is present and whether it changes streak-bias dynamics relative to RuleLLM.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Reference |
|---|---|---|
| Gambler's Fallacy Index | `gambler_fallacy_index(price_history, fundamental)` | §2.1 |
| Streak Asymmetry Ratio | `streak_asymmetry_ratio(price_history, fundamental)` | §2.2 |
| Hot Hand Momentum | `hot_hand_momentum(net_demand_history, dev_history, threshold=0.02)` | §2.3 |
| Arbitrage Correction Index | `arbitrage_correction_index(dev_history, lookahead=5, threshold=0.05)` | §2.4 |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5 |
| Wealth Distribution Index | `wealth_distribution_index(agent_wealth)` | §2.6 |
| RAG Knowledge Effect | `analyze_rag_knowledge_effect(records)` | RAG extension to §5 comparison |

## §3 Data Loading and Structural Checks

`Rag/analysis.py` imports Rule metrics and adds `_RAG_FALLBACK` plus `analyze_rag_knowledge_effect()`. Review must check round count, order schema, parse quality, and RAG context availability.

## §4 Phase Analysis

Use the same phases as RuleLLM, then examine whether retrieved context appears during high-deviation streak periods and whether it reinforces or moderates biased demand.

## §5 Cross-Variant Comparison

RAG should be compared first to RuleLLM. Any RAG-only metric difference should be interpreted together with retrieval success and fallback rates.

## §6 Expected Results and Validation

Valid RAG outputs should complete 200 rounds, maintain valid decision JSON, and show retrievable context or explicit fallback context in records.

## §7 Visualization Catalogue

The inherited price-dynamics figure is primary. RAG reports should add retrieval success rate, fallback rate, and count of RAG context observations.
