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

## §4 Variant-Specific Observable Phenomena

| Phenomenon                        | Description                                                                                             | How to Observe                                                              | Contrast with Baseline Variant |
|-----------------------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------|
| Threshold-triggered framing       | GainFrameFollower and LossFrameReactor activate the instant `|deviation| > 0.02`                        | `02_deviation_timeseries.png` shows step change in per-round bid volume     | This is the baseline           |
| Asymmetric wing intensity         | Positive-deviation rounds and negative-deviation rounds differ in |dev| magnitude by a fixed ratio      | `summary.json → metrics.framing_asymmetry_ratio` (FAR) close to design value | This is the baseline           |
| Reproducible correction lag       | RationalArbitrageur enters exactly when `|dev| > 0.05`; correction window is seed-invariant             | `06_correction_efficiency.png` marker positions identical across seeds      | This is the baseline           |
| Analytic wealth transfer          | Biased traders lose to arbitrageurs in a closed-form way; WDI stable across seeds                       | `07_wealth_by_agent.png` bar ordering identical across seeds                | This is the baseline           |
| Volatility regime step function   | VAF is a step function at the framing threshold; no reasoning-driven smoothing                          | `03_volatility_regime.png` two disjoint volatility clusters                 | This is the baseline           |

Rule is the deterministic reference for FramingEffect: every threshold is hard, every trigger fires the round the price crosses the boundary, and no reasoning or retrieval softens the response. Expected calibration targets: FDI ∈ [0.03, 0.10], FAR ∈ [0.8, 2.5], RCE ∈ [0.35, 0.65], VAF > 1.5.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                | Phenomenon Clarity | Recommended for  |
|--------------|--------------------------------------------------------------------|--------------------|------------------|
| 100          | Framing onset and one correction cycle visible                     | Low                | Quick testing    |
| 200          | Full Baseline → Rational-Correction arc; FDI/FAR stably estimated  | Medium             | Standard runs    |
| 500          | Multiple framing episodes; VAF and RCE tighten across seeds        | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                    | Environment Dynamics                        |
|-------------|------------------------------------------------------------------------|---------------------------------------------|
| 20          | FDI still measurable; per-round net demand is noisier                  | Low order density; FAR variance elevated    |
| 40          | Clean phase separation; all six §2 metrics stably estimated            | Full mechanism observable                   |
| 80          | Reduced per-seed variance; suitable for parameter sweeps               | Baseline mechanism with statistical mass    |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                          |
|----------------------------------------|--------|-------------------------------------------------------------------------------------|
| `framing_scale`                        | +50 %  | FDI rises above 0.10; FAR moves further from 1.0; VAF grows                         |
| `framing_scale`                        | −50 %  | FDI drops below 0.03; framing may fall below detection threshold                    |
| `price_impact` (λ)                     | +50 %  | Deviations larger per bid; FDI up, VAF up, RCE may drop as arbitrage saturates      |
| `RationalArbitrageur` share            | +50 %  | RCE approaches upper band; FDI compresses toward 0                                  |
| `rational_threshold`                   | −50 %  | Earlier correction; shorter mispricing episodes; RCE higher                         |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/FramingEffect/Rule/analysis/`. `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="Rule")` renders the full 9-panel dashboard plus `summary.json` and a console validation report. Every panel is title-stamped with the `variant` label.

| Output File                     | Generated By                       | Contents                                                                   | How to Interpret                                                                  |
|---------------------------------|------------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_framingeffect()`          | Metrics (FDI/FAR/FVI/RCE/VAF/WDI) + validation + variant label             | Compare against calibration targets: FDI [0.03, 0.10]; FAR [0.8, 2.5]              |
| `00_investor_bids.png`          | `analyze_framingeffect()`          | Per-investor bidding curves overlaid on market price + fundamental         | Biased-trader bids cluster near threshold crossings                               |
| `01_price_dynamics.png`         | `analyze_framingeffect()`          | Price vs fundamental with ±2 % and ±5 % deviation bands                    | Price should oscillate across the ±2 % band; brief excursions past ±5 %           |
| `02_deviation_timeseries.png`   | `analyze_framingeffect()`          | Deviation(t) with FDI/FAR annotation and phase thresholds                  | Look for step-function activation at ±2 %                                         |
| `03_volatility_regime.png`      | `analyze_framingeffect()`          | Return time-series + regime histogram (framing-active vs quiet) — VAF      | Two disjoint clusters expected for Rule                                           |
| `04_framing_metrics.png`        | `analyze_framingeffect()`          | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands       | All bars should fall within green target bands                                    |
| `05_agent_volume_breakdown.png` | `analyze_framingeffect()`          | Stacked buy/sell volume by agent type (binned across rounds)                | Biased-trader volume peaks during Active Framing phase                            |
| `06_correction_efficiency.png`  | `analyze_framingeffect()`          | Large-deviation events with corrected/uncorrected markers — RCE            | RCE ≈ 0.35–0.65 range; markers evenly distributed                                 |
| `07_wealth_by_agent.png`        | `analyze_framingeffect()`          | Final wealth by agent type with WDI annotation                             | RationalArbitrageur wealth > biased traders                                       |
| `08_summary.png`                | `analyze_framingeffect()`          | 2×2 combined summary: residual, return histogram, net demand, metric text  | Headline chart; check overall consistency                                         |

The legacy `create_visualizations(data, output_dir)` helper is retained purely for ad-hoc single-plot use and is **not** used by the standard pipeline.

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

---

## §7 Cross-Variant Comparison Notes

Rule is the deterministic reference variant against which LLM, RuleLLM, and Rag are compared. Cross-variant axes are drawn from `../analysis-bases.md §5` and §6.3.

| Comparison Axis          | Rule's Expected Position                            | Reason                                                                                              |
|--------------------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Framing susceptibility (FDI) | Highest — upper bound for the four variants     | Threshold rules fire the instant `|dev| > 0.02`; no reasoning-based softening                       |
| Behavioral asymmetry (FAR)   | Most asymmetric — closest to the λ=2.25 target  | LossFrameReactor `framing_scale` is a hard multiplier; nothing dampens the asymmetry                |
| Rational correction (RCE)    | Baseline — RationalArbitrageur engages at exact 5 % boundary | Fixed threshold; no persona-driven early or late correction                              |
| Volatility amplification (VAF) | Highest — clean step function between regimes | Framing-active vs quiet regimes are disjoint because activation is deterministic                    |
| Reasoning richness           | None — payloads carry no `reasoning` text       | Rule agents emit only numeric decisions; use LLM/RuleLLM/Rag for reasoning-quality inspection       |

**Comparison protocol** (from `../analysis-bases.md §6.2`): run Rule with 10 seeds, take mean FDI/FAR/RCE/VAF as the reference, then run LLM/RuleLLM/Rag under the same parameters and same seed set. Report each variant's metrics as absolute value and as `Δ vs Rule = variant − Rule`.

| Downstream Variant | Predicted Direction vs Rule                                    | Detection Test                                                                                                             |
|--------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| LLM                | FDI ↓, FAR → 1.0, RCE ↑, VAF ↓                                 | LLM persona softens threshold activation; reasoning-driven partial override at moderate deviations                         |
| RuleLLM            | FDI ≈ Rule ± 5 %, FAR ≈ Rule ± 10 %, RCE marginally ↑          | Embedded `== DECISION RULES ==` anchors timing to Rule; LLM contributes quantity variance rather than timing variance      |
| Rag                | FDI ↓ vs Rule (when retrieval hits), RCE highest across variants | Retrieved case studies (Tversky-Kahneman, Barber-Odean, Shleifer-Vishny) uplift rational correction; fallback rounds drift toward LLM baseline |

If any downstream variant produces `FDI ≥ Rule` or `FAR > Rule`, treat that as a calibration alert: either the retrieval / prompt is failing (Rag / LLM) or the embedded rule text is amplifying rather than moderating framing (RuleLLM). Rule itself should never be exceeded by a well-tuned variant.
