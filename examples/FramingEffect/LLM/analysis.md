# FramingEffect LLM — Analysis Guide

## §1 Analysis Objectives

The LLM analysis reuses the metric foundation in `../analysis-bases.md §1` while adding quality attention to model reasoning, parse success, and whether persona-only prompts produce framing-like behavior.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Reference |
|---|---|---|
| Framing Deviation Index | `framing_deviation_index(price_history, fundamental)` | §2.1 |
| Framing Asymmetry Ratio | `framing_asymmetry_ratio(price_history, fundamental)` | §2.2 |
| Framing Volume Impact | `framing_volume_impact(net_demand_history, dev_history, threshold=0.02)` | §2.3 |
| Rational Correction Efficiency | `rational_correction_efficiency(dev_history, lookahead=5, threshold=0.05)` | §2.4 |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5 |
| Wealth Distribution Index | `wealth_distribution_index(agent_wealth)` | §2.6 |

## §3 Data Loading and Structural Checks

`LLM/analysis.py` imports the core functions from `Rule/analysis.py`. Structural quality review should additionally inspect LLM output logs for parse failures, retries, missing `<decision>` blocks, and malformed quantities.

## §4 Phase Analysis

Phase analysis follows `analysis-bases.md §4`: early frame-sensitive trades, deviation persistence, and correction. LLM-specific notes should record whether reasoning text cites gain/loss framing or instead behaves as generic momentum/value trading.

## §5 Cross-Variant Comparison

Compare LLM against Rule and RuleLLM. LLM differences are interpreted as persona-only model effects because the market and topology are inherited from Rule.

## §6 Expected Results and Validation

Valid LLM samples should complete 200 rounds with no fallback holds and with parseable decision JSON. A high parse-failure count or repeated invalid action schema is a quality issue even if the process exits successfully.

## §7 Visualization Catalogue

The inherited visualization `framingeffect_price_dynamics.png` is the core figure. LLM reports may add action-distribution and parse-quality tables alongside the metric output.
