# EndowmentEffect RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether embedded rule constraints in the RuleLLM variant preserve the Rule baseline endowment effect while adding LLM quantity adaptability. Key questions:
- Does rule embedding maintain volume suppression levels comparable to Rule?
- Does LLM quantity selection within constraints improve or impair price stability?
- How does RuleLLM compare to both Rule (lower bound) and LLM (upper bound) on MAD?

## §2 Metric → Function Mapping

| Metric                                | Function                                                                                          | analysis-bases.md ref |
|---------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                  | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)         | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Half-Life (DPHL)            | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)        | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR) | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)          | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 RuleLLM-Specific Notes

- **RuleLLMEndowedHolder (§4.1)**: Sell threshold is rule-locked; VSR should be close to Rule baseline; LLM only affects quantity, not decision timing
- **RuleLLMStatusQuoSeller (§4.2)**: Inertia threshold is embedded; LLM cannot sell prematurely — DPHL expected to be similar to Rule
- **RuleLLMRationalArbitrageur (§4.3)**: arb_threshold rule is embedded; LLM adapts order size based on deviation magnitude — may produce more efficient EPCR than pure Rule
- **RuleLLMNewBuyer (§4.4)**: Buy threshold is encoded; LLM adjusts quantity dynamically — may reduce MAD faster than Rule if LLM buys more aggressively
- **RuleLLMNoiseTrader (§4.5)**: Trade probability encoded; LLM selects quantity and direction within rule bounds — noise profile similar to Rule but with correlated quantity selection
- **vs. Rule**: Expected MAD within ±5% of Rule baseline; VSR within ±5% of Rule baseline

## §4 Variant-Specific Observable Phenomena

| Phenomenon                                | Description                                                                                            | How to Observe                                                                | Contrast with Rule Baseline                                     |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-----------------------------------------------------------------|
| Rule-anchored sell threshold              | Embedded `endowment_premium` rule in the persona guides but does not force sell timing                 | `metrics.endowment_premium_capture_rate` within ±5 % of Rule                  | Timing tighter than pure LLM; slightly softer than Rule         |
| LLM-modulated order size                  | Under the same threshold trigger, LLM selects a quantity from a data-conditioned range                 | `strategy_summary[*].total_volume` variance across seeds                      | Quantity variance higher than Rule; timing near Rule            |
| Reasoning text with quantitative anchors  | Order `reasoning` fields cite the embedded formula language (e.g. "premium 5 % + margin")              | Grep `reasoning` for "premium", "threshold"                                   | Rule payloads carry no reasoning; LLM payloads are unanchored   |
| Persona × rule consistency                | RuleLLM investors give persona-consistent narratives that reference embedded rules                     | Human review of order-payload `analysis` and `reasoning` fields               | Provides deeper characterization than either Rule or LLM alone  |

RuleLLM treats embedded rules as **deeper investor characterization** (knowledge, habits, decision-making framework) rather than as executable mandates. MAD and EPCR are expected to fall within ±5 % of the Rule band, with slightly widened dispersion driven by LLM quantity choice.

**RuleLLM expected ranges** (vs. Rule baseline):

| Metric              | RuleLLM Expected Range | vs. Rule Baseline                   |
|---------------------|------------------------|-------------------------------------|
| MAD                 | 0.03–0.12              | Within ±5 % of Rule                 |
| DPHL                | 15–50 rounds           | Within ±10 % of Rule                |
| VSR                 | 0.40–0.65              | Within ±5 % of Rule                 |
| EPCR                | 0.45–0.75              | Slightly softer (adaptive quantity) |
| PWR (EndowedHolder) | 0.90–1.10              | Similar to Rule                     |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Resistance visible; per-seed MAD dispersion still noisy                | Low                | Smoke testing    |
| 200          | Full Initialization → Convergence arc; RuleLLM stability visible       | Medium             | Standard runs    |
| 500          | Rule-anchored EPCR and MAD stabilize; LLM quantity variance averages out | High             | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                  | Environment Dynamics                                |
|-------------|----------------------------------------------------------------------|-----------------------------------------------------|
| 20          | EPCR measurable but LLM cost dominates run time                      | Sparse orders; MAD variance elevated                |
| 40          | Recommended: clean phase separation with tractable LLM budget        | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for prompt-variation studies | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                          |
|----------------------------------------|--------|-------------------------------------------------------------------------------------|
| `EndowedHolder.endowment_premium`      | +50 %  | Prompt-embedded threshold tightens; EPCR rises; LLM may still select smaller sells  |
| `EndowedHolder.endowment_premium`      | −50 %  | LLM occasionally overrides rule for narrative reasons; EPCR drops more than in Rule |
| `RationalArbitrageur` share            | +50 %  | LLM adjusts arbitrage size dynamically; DPHL shortens toward Rule                   |
| LLM temperature (sampling)             | +50 %  | MAD variance across seeds grows; EPCR still centered on Rule value                  |
| Prompt rule wording (paraphrase)       | Test   | Adherence to `endowment_premium` may drift; use as robustness probe                 |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/EndowmentEffect/RuleLLM/analysis/`. RuleLLM reuses the Rule pipeline (`load_simulation_data`, `calculate_metrics`, `create_visualizations`).

| Output File                            | Generated By                             | Contents                                                | How to Interpret                                                                          |
|----------------------------------------|------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------------------------|
| `summary.json`                         | `main()` (imported from `Rule/analysis.py`) | Metrics + validation + strategy summary               | Compare `mean_absolute_deviation`, `endowment_premium_capture_rate` to Rule reference     |
| `00_investor_bids.png`                 | `create_visualizations()` alias          | Per-strategy total volume                               | EndowedHolder / StatusQuoSeller bars should approximate Rule shape                        |
| `01_endowmenteffect_dynamics.png`      | `create_visualizations()`                | Price path vs. fundamental                              | Above-fundamental band with slightly noisier trajectory than Rule                         |
| `02_endowmenteffect_analysis.png`      | `create_visualizations()` alias          | Volume-by-strategy view                                 | Asymmetry preserved; LLM quantity choice may broaden bars                                 |
| `03_summary.png`                       | `create_visualizations()` alias          | Volume overview                                         | Headline chart for reports                                                                |
| `price_path.png`                       | `create_visualizations()`                | Helper price plot                                       | Sanity-check price trace                                                                  |
| `strategy_volume.png`                  | `create_visualizations()`                | Helper volume plot                                      | Sanity-check strategy asymmetry                                                           |

`summary.json → metrics.strategy_summary[*].reasoning`-derived text is not written by default but can be inspected directly from `EXPERIMENT/EndowmentEffect/RuleLLM/records/` for qualitative rule-adherence review.

---

## §7 Cross-Variant Comparison Notes

RuleLLM sits between Rule (deterministic) and LLM (unanchored) on the anchoring axis. Comparison targets follow `analysis-bases.md §5`:

| Comparison Axis         | RuleLLM's Expected Position                                        | Reason                                                                                          |
|-------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Phenomenon onset speed  | Near Rule (marginally slower)                                      | Rules anchor timing; LLM occasionally waits an extra round for narrative confirmation           |
| Phenomenon intensity    | Between Rule and LLM; EPCR band widened by ±5 % vs. Rule           | Embedded rules bound the drift; LLM softens hard thresholds                                     |
| Behavioral realism      | Highest: persona + explicit decision framework                     | Rules act as characterization, not mandates; reasoning is coherent with quantitative anchors    |
| Decision quality        | Similar to Rule on average; slightly higher variance per seed      | LLM quantity choice occasionally outperforms fixed-size Rule but also introduces sampling noise |
