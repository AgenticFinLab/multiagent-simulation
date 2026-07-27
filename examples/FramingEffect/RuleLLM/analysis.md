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

## §4 Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                                                     | How to Observe                                                                | Contrast with Rule Baseline                     |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------|
| Rule-anchored framing timing            | Embedded `== DECISION RULES ==` block anchors gain/loss activation near the 2 % boundary                        | Order-payload `analysis` text cites the rule; timing tighter than pure LLM     | Timing close to Rule; softer edge               |
| LLM-modulated framing intensity         | Under the same trigger, LLM selects quantity within the rule-implied band                                       | `05_agent_volume_breakdown.png` shows quantity variance under fixed timing    | Quantity variance higher than Rule              |
| Persona × rule coherence                | Reasoning text combines gain/loss narrative with rule vocabulary ("gain +2 %", "loss −2 %")                     | Grep `reasoning` for both persona and rule keywords                           | Rule has no reasoning; LLM lacks rule anchors   |
| Reduced correction lag                  | Rule-anchored rational agents engage exactly at 5 % boundary but adapt size dynamically                         | `06_correction_efficiency.png` shows corrected markers tightly clustered      | Marker timing tighter than LLM                  |
| Deeper characterization                 | Embedded rules act as investor knowledge/habit, not as executable mandate                                       | Cross-check `reasoning` for rule-consistent divergence when LLM overrides     | Rule cannot override; LLM has no anchor         |

RuleLLM sits between Rule (fully deterministic) and LLM (fully unanchored). Embedded rules serve as **deeper investor characterization** rather than executable rules. FDI is expected within ±5 % of Rule; FAR within ±10 %.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Framing onset visible but seed variance elevated                       | Low                | Smoke testing    |
| 200          | Full Baseline → Correction arc; RuleLLM anchoring visible              | Medium             | Standard runs    |
| 500          | Rule-anchored FDI stabilizes; LLM quantity variance averages out       | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                  | Environment Dynamics                                |
|-------------|----------------------------------------------------------------------|-----------------------------------------------------|
| 20          | Framing measurable but LLM cost dominates                            | Sparse orders; FAR variance elevated                |
| 40          | Recommended: clean phase separation with tractable LLM budget         | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for rule-fidelity studies     | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                            |
|----------------------------------------|--------|---------------------------------------------------------------------------------------|
| Prompt rule wording (paraphrase)       | Test   | Adherence to `framing_scale` may drift; use as rule-fidelity probe                    |
| LLM temperature                        | +50 %  | FDI/FAR variance widens but centered on Rule value                                    |
| `framing_scale` (in rule text)         | +50 %  | Rule-anchored FDI rises toward 0.10; LLM may still soften edges                       |
| `RationalArbitrageur` share            | +50 %  | RCE approaches Rule upper band; FDI compresses                                        |
| `rational_threshold`                   | −50 %  | Correction begins earlier per rule; LLM quantity choice widens the effect             |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/FramingEffect/RuleLLM/analysis/`. `RuleLLM/analysis.py` delegates to `Rule/analysis.py → analyze_framingeffect(data, config, output_dir, variant="RuleLLM")`; every panel is title-stamped with `variant="RuleLLM"` and `summary.json` records the variant.

| Output File                     | Generated By                              | Contents                                                                   | How to Interpret                                                                     |
|---------------------------------|-------------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `summary.json`                  | `analyze_framingeffect(variant="RuleLLM")` | Metrics + validation + variant label                                       | Expect FDI within ±5 % of Rule; FAR within ±10 %                                     |
| `00_investor_bids.png`          | `analyze_framingeffect()`                 | Per-investor bidding curves overlaid on market price + fundamental          | Biased-trader bids anchored to rule threshold; quantities widen                      |
| `01_price_dynamics.png`         | `analyze_framingeffect()`                 | Price vs fundamental with ±2 % and ±5 % deviation bands                    | Price band close to Rule with slight softening                                       |
| `02_deviation_timeseries.png`   | `analyze_framingeffect()`                 | Deviation(t) with FDI/FAR annotation and phase thresholds                  | Activation tight but slightly gradual                                                |
| `03_volatility_regime.png`      | `analyze_framingeffect()`                 | Return time-series + regime histogram — VAF                                | Two clusters preserved; separation similar to Rule                                    |
| `04_framing_metrics.png`        | `analyze_framingeffect()`                 | Bar chart of FDI / FAR / RCE / VAF / WDI vs calibration target bands       | Bars close to Rule; RCE marginally higher                                            |
| `05_agent_volume_breakdown.png` | `analyze_framingeffect()`                 | Stacked buy/sell volume by agent type (binned)                             | Volume asymmetry preserved; per-bar bars slightly noisier                            |
| `06_correction_efficiency.png`  | `analyze_framingeffect()`                 | Large-deviation events with corrected/uncorrected markers — RCE            | Markers tightly clustered near 5 % boundary                                          |
| `07_wealth_by_agent.png`        | `analyze_framingeffect()`                 | Final wealth by agent type with WDI annotation                             | Rational vs biased wealth gap close to Rule                                          |
| `08_summary.png`                | `analyze_framingeffect()`                 | 2×2 combined summary                                                       | Headline chart; look for rule-anchored signature                                     |

RuleLLM reports may additionally record rule-adherence tables classifying whether each LLM action matched the direction implied by the embedded `== DECISION RULES ==` sections; these live alongside `summary.json` and stay outside the standard PNG contract.

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

---

## §7 Cross-Variant Comparison Notes

RuleLLM sits between Rule (fully deterministic) and LLM (fully unanchored). It is the direct control for measuring the effect of embedded rule text on LLM behavior. Cross-variant axes follow `../analysis-bases.md §5` and §6.3.

| Comparison Axis                | RuleLLM's Expected Position                                     | Reason                                                                                                                    |
|--------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Framing susceptibility (FDI)   | Within ±5 % of Rule; above LLM; above or equal to Rag           | Embedded `== DECISION RULES ==` anchor timing to Rule; LLM contributes only quantity variance                             |
| Behavioral asymmetry (FAR)     | Within ±10 % of Rule; higher than LLM                           | Loss-aversion asymmetry preserved via the rule text; LLM has no such anchor                                               |
| Rational correction (RCE)      | Marginally above Rule; below Rag                                | RationalArbitrageur rule keeps the 5 % boundary; LLM cannot proactively retrieve case studies (Rag can)                   |
| Volatility amplification (VAF) | Close to Rule; slightly softened                                | Regime clusters largely disjoint; small overlap from LLM quantity variance                                                |
| Reasoning traceability         | Highest signal-to-noise                                         | Reasoning cites both persona vocabulary and rule keywords ("gain +2 %", "loss −2 %") — usable as rule-fidelity probe      |
| Rule-fidelity risk             | Present — LLM may paraphrase or override the rule text          | Rule-adherence table quantifies action direction agreement with `== DECISION RULES ==`                                    |

**Comparison protocol**: run RuleLLM under the same parameters and seed set as Rule. Report `Δ vs Rule = RuleLLM − Rule` per metric, plus a rule-adherence rate (fraction of LLM decisions whose sign/direction matches the embedded rule prescription).

| Cross-Variant Test    | Expected Signature                                                                                                      | Detection                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| RuleLLM vs Rule       | FDI, FAR, VAF within ±5–10 %; RCE marginally higher                                                                     | Compare `summary.json` metrics side by side; check bar heights on `04_framing_metrics.png`    |
| RuleLLM vs LLM        | RuleLLM's timing is tighter; FAR further from 1.0                                                                       | `02_deviation_timeseries.png` activation edge sharper for RuleLLM                             |
| RuleLLM vs Rag        | RuleLLM's RCE lower; Rag retrieves case studies, RuleLLM only enforces threshold                                        | `06_correction_efficiency.png` marker density; `rag_stats.json` retrieval success             |

If RuleLLM produces `FDI` outside ±5 % of Rule or `FAR` outside ±10 %, inspect the rule-adherence table: significant drift suggests the LLM is overriding the embedded rule (rule text too weak or persona too strong). If FDI is *below* Rule beyond the ±5 % band, the LLM is behaving like the LLM variant; if *above*, the rule text is amplifying rather than anchoring.
