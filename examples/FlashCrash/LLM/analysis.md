# FlashCrash LLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                             |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                  |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                         |
| Output Location                 | `EXPERIMENT/FlashCrash/LLM/analysis/`                                                                                                                   |
| Imports From                    | `../Rule/analysis.py`: `load_simulation_data`, `calculate_metrics`, `validate_flash_crash`, `create_visualizations`, `_write_standard_named_outputs`. |
| Variant-Specific Functions      | `analyze_action_distribution(agent_records)` — per-agent action frequencies, reasoning-length statistics, decision-entropy.                          |
| Variant-Specific Considerations | LLM decisions are stochastic. Cascade timing has run-to-run variance; multi-seed averaging is recommended for cross-variant comparison.                 |

---

## 2. Metric Implementation

All six §2 metrics are reused verbatim from `Rule/analysis.py`. Only variant-specific interpretation notes are documented here.

### Metric: crash_depth

- **Defined in**: `analysis-bases.md §2 — crash_depth`
- **Implemented in**: `Rule/analysis.py → calculate_metrics()`
- **Data source**: `EXPERIMENT/FlashCrash/LLM/records/` (coordinator `price` batch store)
- **Implementation details**:
  ```python
  from examples.FlashCrash.Rule.analysis import calculate_metrics
  metrics = calculate_metrics(load_simulation_data(config), config)
  ```
- **Variant-specific notes**: Higher variance across seeds; some LLM investors hesitate and delay stop-loss triggers, yielding slightly shallower crashes than the deterministic Rule baseline.
- **Expected range for this variant**: 0.04 – 0.11 (matches §6 with a slight downward bias).

### Metric: liquidity_vacuum_duration

- **Defined in**: `analysis-bases.md §2 — liquidity_vacuum_duration`
- **Implemented in**: `Rule/analysis.py → liquidity_vacuum_duration()`
- **Data source**: coordinator `liquidity`.
- **Implementation details**:
  ```python
  return sum(1 for liq in liquidity_history if liq <= low_threshold)
  ```
- **Variant-specific notes**: LLM market makers may re-enter earlier or later than the Rule threshold rule dictates; expect wider run-to-run spread.
- **Expected range for this variant**: 5 – 20 rounds.

### Metric: stop_loss_cascade_volume

- **Defined in**: `analysis-bases.md §2 — stop_loss_cascade_volume`
- **Implemented in**: `Rule/analysis.py → stop_loss_cascade_volume()` with agent classification via `_classify_agent_type` (substring match on `LLMStopLossTrader`).
- **Data source**: LLM investor payloads (`bid_price`, `quantity`, `strategy = "LLMStopLossTrader"`).
- **Implementation details**:
  ```python
  from examples.FlashCrash.Rule.analysis import stop_loss_cascade_volume
  vol = stop_loss_cascade_volume(data["orders_history"])
  ```
- **Variant-specific notes**: LLM stop-loss agents can rationalise holding a losing position; cumulative cascade volume tends to be slightly lower than Rule.
- **Expected range for this variant**: 400 – 3000 shares.

### Metric: recovery_speed

- **Defined in**: `analysis-bases.md §2 — recovery_speed`
- **Implemented in**: `Rule/analysis.py → recovery_speed()`.
- **Data source**: coordinator `price`.
- **Implementation details**:
  ```python
  # invoked inside calculate_metrics()
  ```
- **Variant-specific notes**: LLM fundamental traders may "recognise" undervaluation earlier via narrative reasoning; recovery can begin one or two rounds sooner.
- **Expected range for this variant**: 8 – 30 rounds.

### Metric: liquidity_provider_withdrawal_fraction

- **Defined in**: `analysis-bases.md §2 — liquidity_provider_withdrawal_fraction`
- **Implemented in**: `Rule/analysis.py → liquidity_provider_withdrawal_fraction()`.
- **Data source**: investor payloads’ `provides_liquidity` flag.
- **Implementation details**:
  ```python
  frac = liquidity_provider_withdrawal_fraction(data["provides_liquidity_history"], crash_start, crash_end)
  ```
- **Variant-specific notes**: probabilistic — LLM MMs may return provision partially during cascade if their reasoning under-weights the vol signal.
- **Expected range for this variant**: 0.5 – 1.0.

### Metric: price_amplification_ratio

- **Defined in**: `analysis-bases.md §2 — price_amplification_ratio`
- **Implemented in**: `Rule/analysis.py → price_amplification_ratio()`.
- **Data source**: coordinator `price` series.
- **Variant-specific notes**: Typically 10 – 30 % lower than Rule due to LLM hesitation and inconsistent threshold adherence.
- **Expected range for this variant**: 1.2 – 3.5×.

### Metric: LLM action distribution (variant-specific)

- **Defined in**: this variant’s `analysis.py`
- **Implemented in**: `analysis.py → analyze_action_distribution(agent_records)`
- **Data source**: investor `turns.payloads()` — fields `action`, `quantity`, `reasoning`.
- **Implementation details**:
  ```python
  actions = per-agent Counter({"buy", "sell", "hold"})
  reasoning_len = [len(payload["reasoning"]) for payload in rounds]
  decision_entropy = -sum(p * log2(p) for p in normalized action counts if p > 0)
  ```
- **Variant-specific notes**: Reported in `summary.json → llm_action_distribution`; aggregate contains fleet-wide entropy over all decisions.
- **Expected range for this variant**: aggregate `decision_entropy` between 0.5 and 1.5 bits (rarely maxed out at log2(3) ≈ 1.585 because the LLM tends to concentrate on 1–2 actions per phase).

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crash Severity

**Objective**: quantify how deep and how fast price falls.

**Implementation**: `calculate_metrics()` from `Rule/analysis.py`; visualised by `plot_fig3_crash_depth_analysis()`.

**Variant-Specific Interpretation**: LLM realises the same qualitative arc as Rule but with softer edges — the trough may be shallower and split across two adjacent rounds.

**Expected Output Description**: deviation curve dips to −4 % … −11 %; trough marker may appear one round later than in Rule.

### Dimension 2: Liquidity Dynamics

**Objective**: measure liquidity collapse timing and duration.

**Implementation**: `liquidity_vacuum_duration()`, `plot_fig1_price_liquidity_dynamics()`, `plot_fig4_liquidity_vacuum()`.

**Variant-Specific Interpretation**: The liquidity dip may not be a perfect step function — LLM MMs sometimes partially re-enter mid-cascade.

**Expected Output Description**: `01_flashcrash_dynamics.png` shows a noisy dip; the vacuum band on `fig4` can be discontinuous.

### Dimension 3: Cascade Mechanics

**Objective**: measure stop-loss cascade timing and volume.

**Implementation**: `stop_loss_cascade_volume()`, `plot_fig5_stop_loss_cascade()`, `plot_fig7_agent_contribution()`, plus `analyze_action_distribution()` for per-agent action mix.

**Variant-Specific Interpretation**: LLM stop-loss agents can decide to hold; the cascade histogram is broader and may lag Rule by 1–2 rounds.

**Expected Output Description**: `00_investor_bids.png` shows several adjacent bars in Cascade instead of a single spike; `llm_action_distribution.per_agent` shows `sell`-dominated entropy for LLMStopLossTrader.

### Dimension 4: Recovery

**Objective**: identify recovery drivers and speed.

**Implementation**: `recovery_speed()`, `plot_fig8_recovery_dynamics()`, `plot_fig6_hft_withdrawal()`.

**Variant-Specific Interpretation**: Fundamental-trader LLM reasoning may accelerate recognition of undervaluation; recovery speed distribution can be bimodal.

**Expected Output Description**: `03_summary.png` shows the ±2 % band crossed within 8–30 rounds; some seeds may not recover.

### Dimension 5: Variant Differences (LLM specifics)

**Objective**: characterise reasoning stochasticity.

**Implementation**: `analyze_action_distribution()` — per-agent action mix, mean/median reasoning length, decision-entropy in bits.

**Variant-Specific Interpretation**: A rising trend in reasoning length during Cascade is expected; entropy near 0 for a single agent implies rule-locked behaviour, entropy near 1.585 implies uniform buy/sell/hold — a red flag for LLM prompt failure.

**Expected Output Description**: per-agent block in `summary.json → llm_action_distribution.per_agent[id]` reporting `actions`, `mean_reasoning_len`, `median_reasoning_len`, `decision_entropy`, `total_rounds`.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                        | Description                                                              | How to Observe                                                        | Contrast with Baseline Variant                                     |
|-----------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| Hesitation before stop-loss       | LLM stop-loss agents reason before triggering; cascade lags 1–2 rounds  | `fig5_stop_loss_cascade.png` bars smeared across Cascade phase        | Rule fires exactly at the threshold                                |
| Reasoning-length surge in Cascade | Mean payload `reasoning` length grows during Cascade                     | `summary.json → llm_action_distribution.per_agent[id].mean_reasoning_len` | Rule payloads carry no reasoning field                             |
| Narrative recovery                | Fundamental LLM agents cite “oversold” language ahead of Rule threshold  | Manual inspection of `reasoning` in per-round payloads                 | Rule triggers on `value_threshold` only                            |
| Uniform-entropy failure mode      | Decision entropy near log2(3) ≈ 1.585 across all phases                  | `summary.json → llm_action_distribution.aggregate.decision_entropy`   | Rule has zero entropy; RuleLLM in between                          |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                             | Phenomenon Clarity | Recommended for  |
|--------------|-----------------------------------------------------------------|--------------------|------------------|
| 100          | Cascade visible; noisy recovery                                 | Low                | Quick testing    |
| 200          | Full arc; single-seed metrics reliable                          | Medium             | Standard runs    |
| 500          | Multi-seed averaging yields tight cross-variant confidence intervals | High          | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                              | Environment Dynamics                              |
|-------------|------------------------------------------------------------------|---------------------------------------------------|
| 40          | Cascade still triggers; per-agent entropy dominated by noise     | Small population inflates per-run variance        |
| 100         | Aggregate entropy statistically meaningful                       | Full mechanism observable                         |

### Parameter Sensitivity (Variant-Specific)

| Parameter                        | Change                            | Expected Effect on This Variant's Analysis                                   |
|----------------------------------|-----------------------------------|------------------------------------------------------------------------------|
| LLM temperature                  | Higher                            | Larger `decision_entropy`; more inter-seed variance in `crash_depth`         |
| LLM temperature                  | Lower                             | Behaviour approaches Rule; entropy near zero                                 |
| System prompt (risk instruction) | Adds explicit "stop-out" guidance | Cascade sharpens; `stop_loss_cascade_volume` approaches Rule                 |

---

## 6. Output Files Reference

All outputs written to `EXPERIMENT/FlashCrash/LLM/analysis/`. Files 00–03 and `fig1`–`fig8` are identical to the Rule variant. Additional payload:

| Output File                    | Generated By                                | Contents                                                              | How to Interpret                                                                       |
|--------------------------------|---------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| `summary.json`                 | `main()`                                    | Metrics + validation + `llm_action_distribution`                       | New block `llm_action_distribution` under top-level key                                |
| `00_investor_bids.png`         | alias of `fig5_stop_loss_cascade.png`       | Per-round stop-loss sell volume                                        | Broader histogram than Rule                                                            |
| `01_flashcrash_dynamics.png`   | alias of `fig1_price_liquidity_dynamics.png` | Price, liquidity, volume, net-demand                                 | Same layout as Rule; visually noisier                                                  |
| `02_flashcrash_analysis.png`   | alias of `fig3_crash_depth_analysis.png`    | Crash-depth diagnostic                                                 | Trough may be less sharp                                                               |
| `03_summary.png`               | alias of `fig8_recovery_dynamics.png`       | Post-trough price arc                                                  | Recovery may straddle the ±2 % band                                                    |
| `fig2` – `fig8`                | (same as Rule)                              | (same as Rule)                                                          | (same as Rule)                                                                          |

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | LLM Variant's Expected Position                                                 | Reason                                                                       |
|------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Phenomenon onset speed | Slightly slower than Rule                                                       | LLM reasoning introduces per-turn latency in threshold crossings             |
| Phenomenon intensity   | Slightly lower than Rule                                                        | Some agents rationalise holding; cascade never reaches Rule’s hard ceiling   |
| Behavioral realism     | Higher                                                                          | Narrative reasoning approximates human trader psychology                     |
| Decision quality       | Mixed — LLM fundamental agents may recover earlier; LLM stop-loss agents may over-hold | Prompt design dominates outcome distribution                              |
