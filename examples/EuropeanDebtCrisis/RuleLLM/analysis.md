# EuropeanDebtCrisis RuleLLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                              |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                    |
| Analysis Script                 | `analysis.py` in this directory                                                                                          |
| Output Location                 | `EXPERIMENT/EuropeanDebtCrisis/RuleLLM/analysis/`                                                                         |
| Imports From                    | `examples/EuropeanDebtCrisis/Rule/analysis.py` — reuses the full analysis pipeline verbatim                               |
| Variant-Specific Functions      | None; `analysis.py` is a thin driver that calls the shared Rule pipeline                                                  |
| Variant-Specific Considerations | RuleLLM embeds Rule thresholds into the LLM prompt while retaining Rule decision logic. Metrics are computed identically to Rule; interpretation focuses on whether embedded rules keep behavior near the Rule baseline. |

Measure whether embedded threshold rules preserve Rule baseline crisis
dynamics while adding LLM quantity adaptability. Key questions:

- Does rule embedding maintain CDI and CD within the Rule baseline range?
- Does LLM quantity adaptation within thresholds affect IER or SRT?
- How does RuleLLM sit between Rule (stable) and LLM (variable) on all metrics?

---

## 2. Metric Implementation

Every metric below inherits its definition and Python implementation from
the Rule variant. This document only records how the interpretation shifts.

### Metric: Crisis Depth Index (CDI)

- **Defined in**: `analysis-bases.md §2 — Crisis Depth Index`
- **Implemented in**: `Rule/analysis.py → crisis_depth_index(price_history, fundamental)`
- **Data source**: `EXPERIMENT/EuropeanDebtCrisis/RuleLLM/records/market/**`
- **Variant-specific notes**: RuleLLM prompts embed the same `sell_threshold`/`panic_threshold`/`intervention_threshold` constants used by Rule; therefore CDI clusters around the Rule mean with an LLM-only noise term coming from quantity choice.
- **Expected range for this variant**: `0.14 – 0.32`.

### Metric: Crisis Duration (CD)

- **Defined in**: `analysis-bases.md §2 — Crisis Duration`
- **Implemented in**: `Rule/analysis.py → crisis_duration(...)`
- **Variant-specific notes**: CD range is narrower than pure LLM; embedded thresholds pin onset and exit windows.
- **Expected range for this variant**: `10 – 28` rounds.

### Metric: Amplification Ratio (AR)

- **Defined in**: `analysis-bases.md §2 — Amplification Ratio`
- **Implemented in**: `Rule/analysis.py → amplification_ratio(...)`
- **Variant-specific notes**: `RuleLLMCreditorPanicker` still fires when `deviation < panic_threshold`; the LLM only adjusts *quantity*. AR upper bound remains close to Rule.
- **Expected range for this variant**: `0.8 – 1.4`.

### Metric: Intervention Effectiveness Ratio (IER)

- **Defined in**: `analysis-bases.md §2 — Intervention Effectiveness Ratio`
- **Implemented in**: `Rule/analysis.py → intervention_effectiveness_ratio(...)`
- **Variant-specific notes**: `RuleLLMECBIntervenor` triggers via the same threshold as Rule but may buy more aggressively within `[0, 800]`; IER stays similar to Rule.
- **Expected range for this variant**: `0.72 – 0.95`.

### Metric: Spread Recovery Time (SRT)

- **Defined in**: `analysis-bases.md §2 — Spread Recovery Time`
- **Implemented in**: `Rule/analysis.py → spread_recovery_time(...)`
- **Variant-specific notes**: LLM-driven quantity sizing tends to shorten recovery when ECB buys aggressively; expect SRT slightly shorter than Rule.
- **Expected range for this variant**: `4 – 18` rounds.

### Metric: Arbitrage Profit Rate (APR)

- **Defined in**: `analysis-bases.md §2 — Arbitrage Profit Rate`
- **Implemented in**: `Rule/analysis.py → arbitrage_profit_rate(...)`
- **Variant-specific notes**: HedgedFund still trades within `entry_threshold` bounds; quantity sizing varies with LLM guidance.
- **Expected range for this variant**: `0.04 – 0.22`.

### Metric: API and RAG Quality (AQR)

- **Defined in**: `analysis-bases.md §2 — API And RAG Quality`
- **Variant-specific notes**: RuleLLM has no RAG contexts; API-quality is captured by parse-retry logs in `RuleLLM/players.py`. Parse failures must fail fast (no silent hold fallback).

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crisis severity — CDI, CD

- **Function**: `calculate_metrics` (inherited).
- **Variant-specific interpretation**: RuleLLM CDI should track Rule within ±5%; larger deviations imply a broken prompt (thresholds inconsistent with `players.yml`).
- **Expected output description**: `fig2_crisis_depth.png` looks nearly identical to Rule's, with the trough shifted by at most 1–2 rounds due to LLM-driven quantity fluctuations.

### Dimension 2: Doom loop — AR, sell volume attribution

- **Function**: `plot_fig3_doom_loop`.
- **Variant-specific interpretation**: Stacked bar shapes and the rolling AR curve should match Rule closely; only the bar heights vary because LLM tunes quantity.

### Dimension 3: Policy response — IER, SRT

- **Function**: `plot_fig4_intervention_timeline`, `plot_fig5_recovery`.
- **Variant-specific interpretation**: ECB fires on the same rounds as Rule; expect slightly larger green bars (LLM sizes up in deep crises).

### Dimension 4: Arbitrage channel — APR, action volume

- **Function**: `plot_fig8_hedgedfund_pnl`.
- **Variant-specific interpretation**: Position trajectory keeps Rule's monotonic build-up during the trough; APR may be slightly higher if quantity sizing is more aggressive.

### Dimension 5: API quality

- **Function**: N/A — RuleLLM does not run RAG.
- **Interpretation**: Parse audit logs (retry counts) captured during the simulation run; these are not summarized in `summary.json` for RuleLLM.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                       | Description                                                            | How to Observe                       | Contrast with Rule / LLM                                             |
|----------------------------------|------------------------------------------------------------------------|--------------------------------------|-----------------------------------------------------------------------|
| Quantity-only variation           | Threshold triggers exact; quantities drift within LLM-generated ranges  | Compare per-round quantity histograms | Rule has fixed `base_size`; LLM has full discretion                   |
| Prompt has both PERSONA and RULES sections | Explicit rules in prompt regulate the LLM output                | Inspect prompt files                  | Pure LLM lacks the RULES section                                      |
| Compressed CDI variance across seeds | Threshold triggers dominate stochasticity                          | CDI std across seeds < 0.05           | LLM std can exceed 0.10                                               |
| Slightly deeper drawdowns when LLM sizes up | Adaptive sizing can amplify a single crisis                    | `fig2` trough vs Rule                 | LLM may drop harder due to prompt-driven aggression                   |
| No degenerate agents              | Rule-embedded prompt ensures buy/sell reasoning per round               | `_aggregate` action distribution      | Pure LLM can degenerate to hold; RuleLLM never should                 |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                | Phenomenon Clarity | Recommended for  |
|--------------|----------------------------------------------------|--------------------|------------------|
| 100          | Onset + trough; incomplete recovery for some seeds | Low                | Quick testing    |
| 200          | Full crisis lifecycle matching Rule shape          | Medium             | Standard runs    |
| 500          | Rule-like reproducibility over multiple cycles     | High               | Research quality |

### Agent Count Scaling

| Agent Count    | Expected Observable | Environment Dynamics                             |
|----------------|---------------------|--------------------------------------------------|
| Minimum viable | Same as Rule minimum | Threshold triggers may occur but not amplify well |
| Recommended    | Full doom loop and stabilization | CDI 0.15–0.30, IER 0.72–0.95           |

### Parameter Sensitivity (RuleLLM-specific)

| Parameter                        | Change   | Expected Effect on This Variant's Analysis                             |
|----------------------------------|----------|-------------------------------------------------------------------------|
| Temperature (`generation_config`)| +50%     | Higher quantity variance; CDI variance grows moderately                 |
| Removing `== DECISION RULES ==`  | On/Off   | Removing rules degrades variant to pure LLM; CDI variance explodes      |
| `intervention_threshold`         | ±10%     | Same IER shift as Rule (thresholds are shared)                          |
| Persona strength                 | High/Low | Higher persona weight lengthens reasoning but does not change triggers  |

---

## 6. Output Files Reference

All outputs written to: `EXPERIMENT/EuropeanDebtCrisis/RuleLLM/analysis/`

| Output File                              | Generated By                     | Contents                                                     | How to Interpret                                                          |
|------------------------------------------|----------------------------------|--------------------------------------------------------------|---------------------------------------------------------------------------|
| `fig1_price_fundamental.png` … `fig8_hedgedfund_pnl.png` | `create_visualizations()` (inherited) | Same eight scenario plots as Rule                          | Interpret as Rule with mild quantity-driven variance                      |
| `00_investor_bids.png`, `01_..._dynamics.png`, `02_..._analysis.png`, `03_summary.png` | `_write_standard_named_outputs()` | Standard-contract aliases                                    | Shared 4-plot contract                                                    |
| `summary.json`                           | `analyze_europeandebtcrisis()`   | Core 7 metrics + validation                                  | Compare `metrics.*` with Rule's `summary.json` element-wise               |

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | This Variant's Expected Position                    | Reason                                                    |
|------------------------|-----------------------------------------------------|-----------------------------------------------------------|
| Phenomenon onset speed | Same as Rule                                        | Shared thresholds                                          |
| Phenomenon intensity   | Same central tendency, slightly wider tails        | LLM-driven quantities                                     |
| Behavioral realism     | Higher than Rule, lower than pure LLM              | Persona is present but tightly constrained               |
| Decision quality       | Deterministic contract compliance from prompt rules | `== DECISION RULES ==` section drives the LLM output      |

**Quality checks**:

- Confirm the run completed 200 configured rounds.
- Confirm prompts contain both `== PERSONA ==` and `== DECISION RULES ==` sections.
- Confirm parse failures do not silently become hold decisions; contract failures must fail fast.
- Confirm accepted decisions preserve canonical order payloads with `action`, `bid_price`, `quantity`, and `reasoning`.
- Compare `summary.json.metrics.crisis_depth_index` against Rule's — deviation > 5% flags a prompt-vs-config drift.
