# FramingEffect Rag — Analysis Guide

## §1 Analysis Objectives

RAG analysis follows `../analysis-bases.md §1` and adds retrieval-quality review: whether retrieved knowledge is present, whether fallback context is common, and whether RAG changes framing intensity relative to RuleLLM.

## §2 Metric → Function Mapping

| Metric                          | Function                                                                      | analysis-bases.md Reference    |
|---------------------------------|-------------------------------------------------------------------------------|--------------------------------|
| Framing Deviation Index         | `framing_deviation_index(price_history, fundamental)`                         | §2.1                           |
| Framing Asymmetry Ratio         | `framing_asymmetry_ratio(price_history, fundamental)`                         | §2.2                           |
| Framing Volume Impact           | `framing_volume_impact(net_demand_history, dev_history, threshold=0.02)`      | §2.3                           |
| Rational Correction Efficiency  | `rational_correction_efficiency(dev_history, lookahead=5, threshold=0.05)`    | §2.4                           |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5                           |
| Wealth Distribution Index       | `wealth_distribution_index(agent_wealth)`                                     | §2.6                           |
| RAG Knowledge Effect            | `analyze_rag_knowledge_effect(records)`                                       | RAG extension to §5 comparison |

## §3 Data Loading and Structural Checks

`Rag/analysis.py → main()` imports the standard Rule analysis contract and adds
`_RAG_FALLBACK`, `analyze_rag_knowledge_effect()`, and `rag_stats.json`.
Quality review must verify full round count, valid order schema, parse quality,
and presence of `rag_context` observations.

## §4 Phase Analysis

Use the same framing phases as Rule and RuleLLM, then inspect whether retrieved context appears more often during high-deviation periods and whether it reinforces or moderates frame-sensitive behavior.

## §5 Cross-Variant Comparison

RAG should be compared first to RuleLLM because both use rule-embedded personas. Any RAG-only difference should be interpreted alongside retrieval success rate and fallback rate.

## §6 Expected Results and Validation

Valid RAG samples should complete 200 rounds, have low fallback context rate, and avoid parse-failure-driven hold substitutions. A clean process exit is not sufficient if retrieval is absent or malformed.

## §7 Visualization Catalogue

`Rag/analysis.py` delegates the core FramingEffect analysis to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="Rag")`, then augments the summary with retrieval statistics. It writes the identical 9-panel dashboard as Rule (with `variant="Rag"` stamped into every title and `summary.json`), plus `rag_stats.json`:

| #  | File                            | Purpose                                                                   | analysis-bases.md Reference |
|----|---------------------------------|---------------------------------------------------------------------------|-----------------------------|
| 00 | `00_investor_bids.png`          | Per-investor bidding curves overlaid on market price + fundamental        | §3 Dim 1                    |
| 01 | `01_price_dynamics.png`         | Price vs fundamental with ±2% and ±5% deviation bands                     | §7                          |
| 02 | `02_deviation_timeseries.png`   | Deviation(t) with FDI/FAR annotation and phase thresholds                 | §2.1, §2.2, §4              |
| 03 | `03_volatility_regime.png`      | Return time-series + regime histogram (framing-active vs quiet) — VAF     | §2.5                        |
| 04 | `04_framing_metrics.png`        | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands      | §6.2                        |
| 05 | `05_agent_volume_breakdown.png` | Stacked buy/sell volume by agent type (binned)                            | §3 Dim 2                    |
| 06 | `06_correction_efficiency.png`  | Large-deviation events with corrected/uncorrected markers — RCE           | §2.4                        |
| 07 | `07_wealth_by_agent.png`        | Final wealth by agent type with WDI annotation                            | §2.6, §3 Dim 3              |
| 08 | `08_summary.png`                | 2×2 combined summary: residual, return histogram, net demand, metric text | §3 Dim 4                    |
| —  | `rag_stats.json`                | Retrieval success rate, fallback rate, and RAG context observation count  | RAG extension to §5         |
