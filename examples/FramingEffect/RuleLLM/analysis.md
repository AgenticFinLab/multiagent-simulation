# FramingEffect RuleLLM — Analysis Guide

## §1 Analysis Objectives

RuleLLM analysis follows `../analysis-bases.md §1` and focuses on whether embedded rule text keeps LLM behavior close to the deterministic baseline while still permitting reasoning-driven variation.

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

`RuleLLM/analysis.py` reuses the Rule analysis implementation. Structural review should additionally count parse failures and compare reasoning text against the embedded rule sections.

## §4 Phase Analysis

Phase interpretation follows Rule: biased activation, rational correction, then redistribution. The RuleLLM-specific question is whether LLM wording changes timing or quantities while preserving the intended direction of rule-guided trades.

## §5 Cross-Variant Comparison

RuleLLM should sit between Rule and LLM. Close alignment with Rule indicates strong rule anchoring; drift toward LLM indicates the persona is dominating the embedded decision rules.

## §6 Expected Results and Validation

Valid samples should complete 200 rounds with parseable decisions, low retry counts, and no fallback holds. RuleLLM metric ranges should be near the Rule baseline unless reasoning text justifies a material deviation.

## §7 Visualization Catalogue

The core price-dynamics figure is inherited from Rule. Reports may add rule-adherence tables that classify whether each LLM action matched the direction implied by the embedded rules.
