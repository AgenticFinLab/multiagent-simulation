# EndowmentEffect Rule — Analysis Documentation

## §1 Analysis Objectives

This variant analysis establishes the deterministic baseline for the EndowmentEffect simulation. Objectives:
1. Verify that rule-encoded endowment premium produces measurable price stickiness above fundamental
2. Confirm volume suppression ratio of 40–60% vs. rational baseline
3. Establish half-life target range [15–50 rounds] as calibration anchor for LLM/RuleLLM/Rag comparison
4. Validate that RationalArbitrageur achieves higher PWR than EndowedHolder

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                          | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| Price Deviation (PD)                   | `price_deviation(price_history, fundamental)`                                                     | §2.1                  |
| Mean Absolute Deviation (MAD)          | `mean_absolute_deviation(price_history, fundamental)`                                             | §2.2                  |
| Deviation Persistence Half-Life (DPHL) | `deviation_half_life(price_history, fundamental)`                                                 | §2.3                  |
| Volume Suppression Ratio (VSR)         | `volume_suppression_ratio(actual_volume, rational_volume_estimate)`                               | §2.4                  |
| Endowment Premium Capture Rate (EPCR)  | `endowment_premium_capture_rate(price_history, fundamental, endowment_premium)`                   | §2.5                  |
| Portfolio Wealth Ratio (PWR)           | `portfolio_wealth_ratio(agent_cash_history, agent_position_history, final_price, initial_wealth)` | §2.6                  |

## §3 Rule-Specific Notes

- **EndowedHolder (§4.1)**: Sells only when `deviation > endowment_premium + 0.05`. In Rule variant, this threshold is exact and deterministic; EPCR expected > 0.7.
- **StatusQuoSeller (§4.2)**: Sells only when `deviation > status_quo_threshold`. Typically holds even longer than EndowedHolder; contributes strongly to VSR suppression.
- **RationalArbitrageur (§4.3)**: Symmetric trader; active seller in overvaluation phase; expected PWR 1.05–1.15 in Rule variant (cleanest signal).
- **NewBuyer (§4.4)**: Buys continuously at or below fundamental; provides demand support that limits overcorrection.
- **NoiseTrader (§4.5)**: ~30% per-round activity; provides background volume; does not affect directional bias.
- **MAD**: Rule variant provides the most interpretable MAD signal — no stochastic LLM variability.

## §4 Variant-Specific Observable Phenomena

| Phenomenon                           | Description                                                                                          | How to Observe                                                            | Contrast with Baseline Variant |
|--------------------------------------|------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|--------------------------------|
| Threshold-exact sell abstention      | EndowedHolder sells only when `deviation > endowment_premium + 0.05`; boundary is razor-sharp        | `summary.json → metrics.endowment_premium_capture_rate` ≈ 0.65–0.85       | This is the baseline           |
| Deterministic volume suppression     | Sum of per-round volume divides cleanly by mean strategy volume; VSR is reproducible seed-to-seed    | `metrics.volume_suppression_ratio` ≈ 0.40–0.65                            | This is the baseline           |
| Analytic MAD trajectory              | Per-round `price_deviation` traces a piecewise-monotone curve; no LLM-driven jitter                  | `01_endowmenteffect_dynamics.png` price curve is smooth above fundamental | This is the baseline           |
| Symmetric arbitrageur execution      | RationalArbitrageur trades exactly when `|deviation| > arb_threshold`; PWR converges tightly         | `strategy_summary[RationalArbitrageur].total_volume` stable across seeds  | This is the baseline           |

Rule is the reference variant for EndowmentEffect: deterministic thresholds, no reasoning stochasticity, no retrieved context. MAD and EPCR are expected to fall inside the calibration bands with variance driven only by the exogenous noise term ε(t).

**Rule expected ranges** (calibration anchors for cross-variant comparison):

| Metric                    | Rule Expected Range | Interpretation                                      |
|---------------------------|---------------------|-----------------------------------------------------|
| MAD                       | 0.03–0.12           | Target calibration range per Kahneman et al. (1990) |
| DPHL                      | 15–50 rounds        | Moderate persistence; achievable by 5-agent mix     |
| VSR                       | 0.40–0.65           | 40–65 % of rational market volume                   |
| EPCR (EndowedHolder)      | 0.65–0.85           | Holder rarely meets endowment threshold             |
| EPCR (StatusQuoSeller)    | 0.55–0.75           | Inertia keeps seller in hold most rounds            |
| PWR (RationalArbitrageur) | 1.05–1.15           | Profits from premium selling                        |
| PWR (EndowedHolder)       | 0.95–1.05           | Near breakeven; misses optimal sell timing          |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                              | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------|--------------------|------------------|
| 100          | Resistance phase visible; DPHL fit may be truncated              | Low                | Quick testing    |
| 200          | Full Initialization → Convergence arc; MAD/DPHL stably estimated | Medium             | Standard runs    |
| 500          | Stable DPHL across seeds; EPCR band tightens                     | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                              | Environment Dynamics                     |
|-------------|------------------------------------------------------------------|------------------------------------------|
| 20          | EPCR still measurable; VSR noisier due to sparse order flow      | Low order density; MAD variance elevated |
| 40          | Clean phase separation; stable estimates for all six §2 metrics  | Full mechanism observable                |
| 80          | Reduced per-seed variance; suitable for parameter sweeps          | Baseline mechanism plus statistical mass |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                          |
|----------------------------------------|--------|-------------------------------------------------------------------------------------|
| `EndowedHolder.endowment_premium`      | +50 %  | Higher EPCR; larger MAD; longer DPHL; VSR drops (more holds)                        |
| `EndowedHolder.endowment_premium`      | −50 %  | Lower EPCR; MAD compresses toward 0.03; DPHL shortens                               |
| `RationalArbitrageur` share            | +50 %  | Faster mean-reversion; DPHL < 15; VSR rises; EndowedHolder PWR falls                |
| `RationalArbitrageur` share            | −50 %  | DPHL > 60; MAD widens; overvaluation persists near end of run                       |
| `StatusQuoSeller.status_quo_threshold` | +50 %  | Volume suppression deepens; VSR drops below 0.40; MAD elevated in resistance phase  |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/EndowmentEffect/Rule/analysis/`.

| Output File                            | Generated By                     | Contents                                                            | How to Interpret                                                                    |
|----------------------------------------|----------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| `summary.json`                         | `main()`                         | Metrics + validation + fundamental + per-strategy volume summary    | `metrics.mean_absolute_deviation`, `endowment_premium_capture_rate` are top signals |
| `00_investor_bids.png`                 | `create_visualizations()` alias  | Per-strategy total volume (bar)                                     | EndowedHolder + StatusQuoSeller bars should be short vs. Arbitrageur + NoiseTrader  |
| `01_endowmenteffect_dynamics.png`      | `create_visualizations()`        | Price path with fundamental reference line                          | Price sits above fundamental in resistance phase; converges by round ≈ 80           |
| `02_endowmenteffect_analysis.png`      | `create_visualizations()` alias  | Strategy-volume bar chart (secondary view)                          | Volume asymmetry across strategies is the endowment signature                       |
| `03_summary.png`                       | `create_visualizations()` alias  | Strategy-volume overview                                            | Use as headline chart in reports                                                    |
| `price_path.png`                       | `create_visualizations()`        | Helper price plot (source for `01_...png`)                          | Sanity-check price trace                                                            |
| `strategy_volume.png`                  | `create_visualizations()`        | Helper strategy-volume plot (source for `00_/02_/03_...png`)        | Sanity-check volume asymmetry                                                       |

---

## §7 Cross-Variant Comparison Notes

Rule is the deterministic baseline against which LLM, RuleLLM, and Rag variants are compared (see `analysis-bases.md §5`).

| Comparison Axis         | Rule's Expected Position                        | Reason                                                                 |
|-------------------------|-------------------------------------------------|------------------------------------------------------------------------|
| Phenomenon onset speed  | Fastest / immediate                             | Sell thresholds trigger the round they are crossed                     |
| Phenomenon intensity    | Tightest MAD band; highest EPCR                 | No LLM hesitation to break the endowment threshold                     |
| Behavioral realism      | Mechanistically clean; behaviourally simplistic | Ignores narrative, framing, and retrieved-context effects              |
| Decision quality        | Rule-optimal for the specified thresholds       | RationalArbitrageur captures the premium every time the boundary flips |
