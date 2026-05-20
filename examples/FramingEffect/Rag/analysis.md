# FramingEffect Rag — Analysis Guide

## §1 Analysis Objectives

RAG analysis follows `../analysis-bases.md §1` and adds retrieval-quality review: whether retrieved knowledge is present, whether fallback context is common, and whether RAG changes framing intensity relative to RuleLLM.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Reference |
|---|---|---|
| Framing Deviation Index | `framing_deviation_index(price_history, fundamental)` | §2.1 |
| Framing Asymmetry Ratio | `framing_asymmetry_ratio(price_history, fundamental)` | §2.2 |
| Framing Volume Impact | `framing_volume_impact(net_demand_history, dev_history, threshold=0.02)` | §2.3 |
| Rational Correction Efficiency | `rational_correction_efficiency(dev_history, lookahead=5, threshold=0.05)` | §2.4 |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5 |
| Wealth Distribution Index | `wealth_distribution_index(agent_wealth)` | §2.6 |
| RAG Knowledge Effect | `analyze_rag_knowledge_effect(records)` | RAG extension to §5 comparison |

## §3 Data Loading and Structural Checks

`Rag/analysis.py` imports Rule metrics and adds `_RAG_FALLBACK` plus `analyze_rag_knowledge_effect()`. Quality review must verify full round count, valid order schema, parse quality, and presence of `rag_context` observations.

## §4 Phase Analysis

Use the same framing phases as Rule and RuleLLM, then inspect whether retrieved context appears more often during high-deviation periods and whether it reinforces or moderates frame-sensitive behavior.

## §5 Cross-Variant Comparison

RAG should be compared first to RuleLLM because both use rule-embedded personas. Any RAG-only difference should be interpreted alongside retrieval success rate and fallback rate.

## §6 Expected Results and Validation

Valid RAG samples should complete 200 rounds, have low fallback context rate, and avoid parse-failure-driven hold substitutions. A clean process exit is not sufficient if retrieval is absent or malformed.

## §7 Visualization Catalogue

The inherited price-dynamics figure remains the primary plot. RAG reports should also include a retrieval-quality table with retrieval success rate, fallback rate, and count of RAG context observations.
