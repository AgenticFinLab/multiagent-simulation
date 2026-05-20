# GamblerFallacy LLM — Analysis Guide

## §1 Analysis Objectives

LLM analysis reuses `../analysis-bases.md §1` and adds quality review of parse success, reasoning coherence, and whether persona-only prompts produce gambler's-fallacy or hot-hand behavior.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Reference |
|---|---|---|
| Gambler's Fallacy Index | `gambler_fallacy_index(price_history, fundamental)` | §2.1 |
| Streak Asymmetry Ratio | `streak_asymmetry_ratio(price_history, fundamental)` | §2.2 |
| Hot Hand Momentum | `hot_hand_momentum(net_demand_history, dev_history, threshold=0.02)` | §2.3 |
| Arbitrage Correction Index | `arbitrage_correction_index(dev_history, lookahead=5, threshold=0.05)` | §2.4 |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5 |
| Wealth Distribution Index | `wealth_distribution_index(agent_wealth)` | §2.6 |

## §3 Data Loading and Structural Checks

`LLM/analysis.py` imports the Rule analysis functions. Quality review should additionally inspect model responses for malformed JSON, missing decisions, retry loops, and fallback holds.

## §4 Phase Analysis

Interpret the run in streak emergence, biased demand amplification, rational correction, and wealth redistribution phases. LLM-specific notes should distinguish reversal reasoning from hot-hand continuation reasoning.

## §5 Cross-Variant Comparison

LLM results are compared against Rule and RuleLLM. Differences from Rule represent persona-only model effects under the same market.

## §6 Expected Results and Validation

Valid LLM outputs complete 200 rounds with clean parse quality.

## §7 Visualization Catalogue

The inherited price-dynamics figure is primary. Reports may add LLM action distribution and parse-quality summaries.
