# FramingEffect LLM — Analysis Guide

## §1 Analysis Objectives

The LLM analysis reuses the metric foundation in `../analysis-bases.md §1` while adding quality attention to model reasoning, parse success, and whether persona-only prompts produce framing-like behavior.

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

`LLM/analysis.py` imports the core functions from `Rule/analysis.py`. Structural quality review should additionally inspect LLM output logs for parse failures, retries, missing `<decision>` blocks, and malformed quantities.

## §4 Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                                              | How to Observe                                                                | Contrast with Rule Baseline                       |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------|
| Reasoning-softened framing              | GainFrameFollower / LossFrameReactor sometimes hesitate; framing does not activate at exact 2 % boundary | Order `reasoning` fields cite the frame; entry rounds vary across seeds       | Softer than Rule step activation                  |
| Persona-consistent narratives           | Bid `reasoning` text mentions "gain", "loss", "avoid loss", "chase gains" without formula language       | Grep `reasoning` for framing vocabulary                                       | Rule has no reasoning; LLM captures the narrative |
| Emergent partial resistance             | LLM occasionally overrides frame when deviation is large; RCE tends higher than Rule                     | `06_correction_efficiency.png` shows corrected events at moderate deviations  | Rule waits until 5 % threshold                    |
| Cross-seed variance                     | FDI band widens; FAR migrates toward 1.0                                                                 | Repeat 5 seeds; report FDI/FAR mean ± std                                     | Rule dispersion driven only by ε(t)               |
| Parse-quality risk                      | Rare malformed `<decision>` blocks; fallback holds increase noise                                        | Inspect LLM output logs for parse failures                                    | Rule has no such failure mode                     |

The LLM variant tests whether persona-only prompts, without any explicit formula language, still produce a framing-like market signature. FDI is expected to be lower than Rule; FAR moves toward the symmetric ratio 1.0.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                              | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------|--------------------|------------------|
| 100          | Framing signature present but noisy; DPHL fit unreliable         | Low                | Smoke testing    |
| 200          | Full Baseline → Rational-Correction arc; parse quality stable    | Medium             | Standard runs    |
| 500          | Multiple framing episodes; LLM stochasticity averages out         | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                              | Environment Dynamics                                |
|-------------|------------------------------------------------------------------|-----------------------------------------------------|
| 20          | FDI measurable but LLM cost dominates run time                   | Sparse orders; FAR variance elevated                |
| 40          | Recommended: clean phase separation with tractable LLM budget    | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for prompt-variation runs | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                            |
|----------------------------------------|--------|---------------------------------------------------------------------------------------|
| LLM temperature (sampling)             | +50 %  | Wider FDI/FAR bands; reasoning becomes more speculative                               |
| Prompt persona strength (word choice)  | Test   | Stronger frame vocabulary → FDI approaches Rule; softer vocabulary → FDI drops        |
| `framing_scale` (market side)          | +50 %  | Even with LLM persona, market impact of biased bids grows                             |
| `RationalArbitrageur` share            | +50 %  | RCE rises further above Rule baseline; FDI compresses                                 |
| `rational_threshold`                   | −50 %  | LLM rationals engage earlier; correction more efficient                               |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/FramingEffect/LLM/analysis/`. `LLM/analysis.py` delegates to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="LLM")`; every panel is title-stamped with the `variant="LLM"` label and `summary.json` records the variant.

| Output File                     | Generated By                          | Contents                                                                   | How to Interpret                                                                     |
|---------------------------------|---------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_framingeffect(variant="LLM")` | Metrics (FDI/FAR/FVI/RCE/VAF/WDI) + validation + variant label            | Expect FDI slightly below Rule; FAR closer to 1.0                                   |
| `00_investor_bids.png`          | `analyze_framingeffect()`             | Per-investor bidding curves overlaid on market price + fundamental         | Biased-trader bids more diffuse than Rule                                            |
| `01_price_dynamics.png`         | `analyze_framingeffect()`             | Price vs fundamental with ±2 % and ±5 % deviation bands                    | Price band narrower than Rule                                                        |
| `02_deviation_timeseries.png`   | `analyze_framingeffect()`             | Deviation(t) with FDI/FAR annotation and phase thresholds                  | Activation gradual, not step-function                                                |
| `03_volatility_regime.png`      | `analyze_framingeffect()`             | Return time-series + regime histogram (framing-active vs quiet) — VAF      | Regime overlap; VAF smaller than Rule                                                |
| `04_framing_metrics.png`        | `analyze_framingeffect()`             | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands       | RCE bar higher than Rule; FAR closer to 1.0                                          |
| `05_agent_volume_breakdown.png` | `analyze_framingeffect()`             | Stacked buy/sell volume by agent type (binned)                             | Biased-trader volume spread across more rounds                                       |
| `06_correction_efficiency.png`  | `analyze_framingeffect()`             | Large-deviation events with corrected/uncorrected markers — RCE            | More corrected markers; earlier interventions                                        |
| `07_wealth_by_agent.png`        | `analyze_framingeffect()`             | Final wealth by agent type with WDI annotation                             | Wealth gap between biased and rational agents narrower than Rule                     |
| `08_summary.png`                | `analyze_framingeffect()`             | 2×2 combined summary: residual, return histogram, net demand, metric text  | Headline chart; check overall consistency and LLM regime label                       |

LLM reports may additionally record action-distribution and parse-quality tables alongside `summary.json` for reasoning-quality review; those extras live outside the shared visualization contract.

## §7 Visualization Catalogue

`LLM/analysis.py` is a thin wrapper that delegates to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="LLM")`. It writes the identical 9-panel dashboard as Rule with the `variant="LLM"` label stamped into every title and into `summary.json`:

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

LLM reports may additionally record action-distribution and parse-quality tables alongside `summary.json` for reasoning-quality review, but this stays outside the shared visualization contract.

---

## §7 Cross-Variant Comparison Notes

The LLM variant is compared against Rule (deterministic baseline), RuleLLM (rule-anchored LLM), and Rag (retrieval-augmented LLM) using the axes in `../analysis-bases.md §5` and §6.3.

| Comparison Axis                | LLM's Expected Position                                   | Reason                                                                                                            |
|--------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Framing susceptibility (FDI)   | Below Rule; comparable to Rag; slightly below RuleLLM     | Persona-only prompts do not enforce hard thresholds — reasoning occasionally overrides frame at moderate `|dev|`  |
| Behavioral asymmetry (FAR)     | Closer to 1.0 than Rule; usually closer than RuleLLM      | LLM lacks a fixed `framing_scale` multiplier; loss-aversion asymmetry weakens                                     |
| Rational correction (RCE)      | Higher than Rule; typically below Rag                     | LLM may recognize mispricing before the 5 % threshold, but has no retrieved case-study support                    |
| Volatility amplification (VAF) | Below Rule; regime clusters overlap                       | No step-function activation — reasoning smooths the transition between quiet and framing-active rounds            |
| Reasoning traceability         | Available via order `reasoning` text                      | Every accepted decision carries persona-consistent narrative; grep for gain/loss vocabulary                       |
| Parse-quality risk             | Present — Rule/RuleLLM/Rag also affected, but distinctly  | Malformed `<decision>` blocks and retries must be audited; treat silent fallback holds as quality failures        |

**Comparison protocol**: run LLM under the same parameters and seed set as Rule. Report `Δ vs Rule = LLM − Rule` per metric, plus reasoning-quality summary (parse success rate, mean reasoning length, persona vocabulary hit rate).

| Cross-Variant Test | Expected Signature                                                                                                           | Detection                                                                                     |
|--------------------|------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| LLM vs Rule        | FDI ↓, FAR → 1.0, RCE ↑, VAF ↓; wider cross-seed dispersion                                                                  | Compare `summary.json` metrics side by side across ≥ 5 seeds                                  |
| LLM vs RuleLLM     | LLM's timing is more diffuse; RuleLLM's activation edges tighter                                                              | `02_deviation_timeseries.png` — LLM has slower ramp near `|dev| = 0.02`; RuleLLM near-instant |
| LLM vs Rag         | LLM RCE typically < Rag RCE because RAG retrieves rational case studies                                                       | `06_correction_efficiency.png` marker density                                                 |

If LLM produces `FDI ≥ Rule` or `RCE ≤ Rule`, verify prompt persona strength: too-strong loss-frame vocabulary can restore Rule-like rigidity, while too-weak vocabulary may collapse framing altogether.
