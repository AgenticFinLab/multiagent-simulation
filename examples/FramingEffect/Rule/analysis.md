# FramingEffect Rule — Analysis Guide

## §1 Analysis Objectives

The Rule analysis verifies the deterministic baseline specified in `../analysis-bases.md §1`: framing-induced price deviation, biased-trader amplification, rational correction, and wealth redistribution.

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

`analysis.py → main()` loads the raw record set via `masim.evaluation.data_loader.load_data(results)` and derives four aligned series consumed by the metric layer:

* `market_prices[round] → price`
* `fundamentals[round] → fundamental_value` (falls back to the coordinator config's `extras.fundamental_value` when the recorded dict is empty)
* `investor_quantities[player_id][round] → signed_quantity` (used to build `net_demand_history`)
* `investor_payloads[player_id][round] → dict` (used to reconstruct `agent_wealth`)

Accepted data must include a non-empty `market_prices`; missing series degrade gracefully (`NaN`) rather than aborting the run.

The legacy ad-hoc helper `load_simulation_data(record_path)` remains available for single-file JSON inspection outside the standard pipeline.

## §4 Phase Analysis

The Rule baseline is interpreted in three phases from `analysis-bases.md §4`: early activation of biased traders near the 2% threshold, correction attempts once deviation exceeds rational thresholds, and final wealth redistribution after repeated biased trades.

## §5 Cross-Variant Comparison

Rule results provide the comparison anchor for LLM, RuleLLM, and RAG. Any later variant should be compared against Rule on FDI, FAR, VAF, and WDI before claiming stronger or weaker framing effects.

## §6 Expected Results and Validation

Expected Rule behavior is moderate FDI, nonzero asymmetry, higher volatility during framing-active rounds, and some wealth transfer from biased traders toward rational or arbitrage traders. A flat price path, empty order set, or zero deviation across all rounds indicates implementation or config failure.

## §7 Visualization Catalogue

`analysis.py → analyze_framingeffect(data, config, output_dir, variant="Rule")` renders the full 9-panel dashboard specified by `analysis-bases.md §7`, plus a structured `summary.json` and a console validation report. Every panel is title-stamped with the `variant` label so it is easy to spot which run produced which file.

| #  | File                            | Purpose                                                                   | analysis-bases.md Reference |
|----|---------------------------------|---------------------------------------------------------------------------|-----------------------------|
| 00 | `00_investor_bids.png`          | Per-investor bidding curves overlaid on market price + fundamental        | §3 Dim 1                    |
| 01 | `01_price_dynamics.png`         | Price vs fundamental with ±2% and ±5% deviation bands                     | §7                          |
| 02 | `02_deviation_timeseries.png`   | Deviation(t) with FDI/FAR annotation and phase thresholds                 | §2.1, §2.2, §4              |
| 03 | `03_volatility_regime.png`      | Return time-series + regime histogram (framing-active vs quiet) — VAF     | §2.5                        |
| 04 | `04_framing_metrics.png`        | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands      | §6.2                        |
| 05 | `05_agent_volume_breakdown.png` | Stacked buy/sell volume by agent type (binned across rounds)              | §3 Dim 2                    |
| 06 | `06_correction_efficiency.png`  | Large-deviation events with corrected/uncorrected markers — RCE           | §2.4                        |
| 07 | `07_wealth_by_agent.png`        | Final wealth by agent type with WDI annotation                            | §2.6, §3 Dim 3              |
| 08 | `08_summary.png`                | 2×2 combined summary: residual, return histogram, net demand, metric text | §3 Dim 4                    |

The legacy `create_visualizations(data, output_dir)` helper is retained purely for ad-hoc single-plot use and is **not** used by the standard pipeline.
