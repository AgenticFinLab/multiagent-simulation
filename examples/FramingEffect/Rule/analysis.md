# FramingEffect Rule — Analysis Guide

## §1 Analysis Objectives

The Rule analysis verifies the deterministic baseline specified in `../analysis-bases.md §1`: framing-induced price deviation, biased-trader amplification, rational correction, and wealth redistribution.

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

`analysis.py → load_simulation_data(record_path)` loads JSON records from the selected record directory. Accepted data must include a non-empty `price_history` and positive `fundamental` before metrics are calculated.

## §4 Phase Analysis

The Rule baseline is interpreted in three phases from `analysis-bases.md §4`: early activation of biased traders near the 2% threshold, correction attempts once deviation exceeds rational thresholds, and final wealth redistribution after repeated biased trades.

## §5 Cross-Variant Comparison

Rule results provide the comparison anchor for LLM, RuleLLM, and RAG. Any later variant should be compared against Rule on FDI, FAR, VAF, and WDI before claiming stronger or weaker framing effects.

## §6 Expected Results and Validation

Expected Rule behavior is moderate FDI, nonzero asymmetry, higher volatility during framing-active rounds, and some wealth transfer from biased traders toward rational or arbitrage traders. A flat price path, empty order set, or zero deviation across all rounds indicates implementation or config failure.

## §7 Visualization Catalogue

`analysis.py → create_visualizations(data, output_dir)` creates `framingeffect_price_dynamics.png`, plotting price against fundamental value across rounds. Additional scenario reports may add per-agent contribution and wealth-distribution figures using the metric functions above.
