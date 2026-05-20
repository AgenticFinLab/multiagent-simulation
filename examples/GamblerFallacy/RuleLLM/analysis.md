# GamblerFallacy RuleLLM — Analysis Guide

## §1 Analysis Objectives

RuleLLM analysis follows `../analysis-bases.md §1` and asks whether embedded rule text keeps LLM behavior close to the deterministic baseline while preserving useful reasoning traces.

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

`RuleLLM/analysis.py` imports the Rule implementation. Quality review should additionally inspect rule-adherence in reasoning and parse-quality counters.

## §4 Phase Analysis

Use the same phases as Rule: streak emergence, biased amplification, arbitrage correction, and redistribution. RuleLLM-specific review checks whether reasoning changes trade size or direction despite embedded rules.

## §5 Cross-Variant Comparison

RuleLLM should sit between Rule and LLM. Close alignment with Rule indicates strong rule anchoring; drift toward LLM indicates persona or model reasoning dominates.

## §6 Expected Results and Validation

Valid samples complete 200 rounds with clean parse quality. Existing accepted RuleLLM sample is inheritable because this pass only adds docs and analysis files.

## §7 Visualization Catalogue

The inherited price-dynamics figure is primary. Reports may add rule-adherence and action-distribution summaries.
