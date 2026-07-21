# FramingEffect RuleLLM — Analysis Guide

## §1 Analysis Objectives

RuleLLM analysis follows `../analysis-bases.md §1` and focuses on whether embedded rule text keeps LLM behavior close to the deterministic baseline while still permitting reasoning-driven variation.

## §2 Metric → Function Mapping

| Metric                          | Function                                                                      | analysis-bases.md Reference |
|---------------------------------|-------------------------------------------------------------------------------|-----------------------------|
| Framing Deviation Index         | `framing_deviation_index(price_history, fundamental)`                         | §2.1                        |
| Framing Asymmetry Ratio         | `framing_asymmetry_ratio(price_history, fundamental)`                         | §2.2                        |
| Framing Volume Impact           | `framing_volume_impact(net_demand_history, dev_history, threshold=0.02)`      | §2.3                        |
| Rational Correction Efficiency  | `rational_correction_efficiency(dev_history, lookahead=5, threshold=0.05)`    | §2.4                        |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5                        |
| Wealth Distribution Index       | `wealth_distribution_index(agent_wealth)`                                     | §2.6                        |

## §3 Data Loading and Structural Checks

`RuleLLM/analysis.py → main()` reuses the standard Rule analysis contract for
`summary.json`, structured validation output, and the fixed PNG set. Structural
review should additionally count parse failures and compare reasoning text
against the embedded `== DECISION RULES ==` sections.

## §4 Phase Analysis

Phase interpretation follows Rule: biased activation, rational correction, then redistribution. The RuleLLM-specific question is whether LLM wording changes timing or quantities while preserving the intended direction of rule-guided trades.

## §5 Cross-Variant Comparison

RuleLLM should sit between Rule and LLM. Close alignment with Rule indicates strong rule anchoring; drift toward LLM indicates the persona is dominating the embedded decision rules.

## §6 Expected Results and Validation

Valid samples should complete 200 rounds with parseable decisions, low retry counts, and no fallback holds. RuleLLM metric ranges should be near the Rule baseline unless reasoning text justifies a material deviation.

## §7 Visualization Catalogue

`RuleLLM/analysis.py` is a thin wrapper that delegates to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="RuleLLM")`. It writes the identical 9-panel dashboard as Rule with the `variant="RuleLLM"` label stamped into every title and into `summary.json`:

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

RuleLLM reports may additionally record rule-adherence tables classifying whether each LLM action matched the direction implied by the embedded `== DECISION RULES ==` sections.
