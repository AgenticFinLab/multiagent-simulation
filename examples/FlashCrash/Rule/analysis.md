# FlashCrash Rule — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                                                                                        |
|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                                                                                             |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                                                                                                    |
| Output Location                 | `EXPERIMENT/FlashCrash/Rule/analysis/`                                                                                                                                                                                             |
| Imports From                    | Authoritative — this file owns `load_simulation_data`, `calculate_metrics`, `create_visualizations`, `validate_flash_crash`, `_write_standard_named_outputs`. LLM/RuleLLM/Rag re-use these symbols.                                |
| Variant-Specific Functions      | None (Rule is the reference implementation for all six metrics)                                                                                                                                                                    |
| Variant-Specific Considerations | Deterministic given fixed `seed`. Agent-type classification uses `_classify_agent_type()`, which prefers the `agent_type` payload field then falls back to substring matching against `strategy` (class name) so LLM/Rag reuse works. |

---

## 2. Metric Implementation

### Metric: crash_depth

- **Defined in**: `analysis-bases.md §2 — crash_depth`
- **Implemented in**: `analysis.py → crash_depth(price_history, fundamental)`, invoked by `calculate_metrics()`
- **Data source**: coordinator batch store `price` under `EXPERIMENT/FlashCrash/Rule/records/`
- **Implementation details**:
  ```python
  deviations = [(p - fundamental) / fundamental for p in price_history]
  return abs(min(deviations))
  ```
- **Variant-specific notes**: Deterministic — for fixed parameters and seed, `crash_depth` is reproducible to floating-point precision.
- **Expected range for this variant**: 0.05 – 0.12 (matches `analysis-bases.md §6`).

### Metric: liquidity_vacuum_duration

- **Defined in**: `analysis-bases.md §2 — liquidity_vacuum_duration`
- **Implemented in**: `analysis.py → liquidity_vacuum_duration(liquidity_history, low_threshold=50.0)`
- **Data source**: coordinator batch store `liquidity`
- **Implementation details**:
  ```python
  return sum(1 for liq in liquidity_history if liq <= low_threshold)
  ```
- **Variant-specific notes**: Purely a function of the market’s liquidity trajectory; Rule sets liquidity via the environment update rule, so this metric is fully determined by `volatility_threshold`.
- **Expected range for this variant**: 5 – 20 rounds.

### Metric: stop_loss_cascade_volume

- **Defined in**: `analysis-bases.md §2 — stop_loss_cascade_volume`
- **Implemented in**: `analysis.py → stop_loss_cascade_volume(orders_history)`
- **Data source**: reconstructed per-round from investor `turns.payloads()` (`bid_price`, `quantity`, `strategy`); rounds are indexed 0..T-1.
- **Implementation details**:
  ```python
  return sum(abs(o["quantity"]) for round_orders in orders_history
             for o in round_orders
             if _classify_agent_type(o) == "stoploss" and o["quantity"] < 0)
  ```
- **Variant-specific notes**: For Rule, `StopLossTrader` is a deterministic threshold rule — cumulative sell volume scales with the number of triggered agents and their position sizes.
- **Expected range for this variant**: 500 – 3000 shares.

### Metric: recovery_speed

- **Defined in**: `analysis-bases.md §2 — recovery_speed`
- **Implemented in**: `analysis.py → recovery_speed(price_history, trough_round, fundamental, recovery_threshold=0.02)`
- **Data source**: coordinator batch store `price`; `trough_round` derived from `calculate_max_drawdown()` inside `_detect_crash_window()`.
- **Implementation details**:
  ```python
  for i in range(trough_round, len(price_history)):
      if abs(price_history[i] - fundamental) / fundamental <= recovery_threshold:
          return i - trough_round
  return -1
  ```
- **Variant-specific notes**: Value depends on `FundamentalTrader.value_threshold` and the fundamental-trader population share.
- **Expected range for this variant**: 10 – 30 rounds.

### Metric: liquidity_provider_withdrawal_fraction

- **Defined in**: `analysis-bases.md §2 — liquidity_provider_withdrawal_fraction`
- **Implemented in**: `analysis.py → liquidity_provider_withdrawal_fraction(provides_liquidity_history, crash_start, crash_end)`
- **Data source**: investor turn payloads’ `provides_liquidity` flag; only agents that record the field contribute to the denominator.
- **Implementation details**:
  ```python
  crash_rounds = provides_liquidity_history[crash_start:crash_end]
  total = sum(sum(1 for v in r.values() if not v) for r in crash_rounds)
  denominator = sum(len(r) for r in crash_rounds)
  return total / max(denominator, 1)
  ```
- **Variant-specific notes**: Binary flag flipped by `HighFrequencyTrader.volatility_threshold`; Rule realises a step-function transition.
- **Expected range for this variant**: 0.6 – 1.0 during the crash window.

### Metric: price_amplification_ratio

- **Defined in**: `analysis-bases.md §2 — price_amplification_ratio`
- **Implemented in**: `analysis.py → price_amplification_ratio(observed_max_drop, baseline_max_drop)` with `baseline_max_drop` computed by `_rolling_baseline_max_drop()` over the first 10 (Normal-phase) rounds.
- **Data source**: coordinator `price` batch store.
- **Implementation details**:
  ```python
  baseline = crash_depth(prices[:window], fundamental) or 0.01
  return observed_max_drop / max(baseline, 1e-6)
  ```
- **Variant-specific notes**: Rule maximises this ratio because HFT withdrawal follows a hard threshold with no LLM hesitation.
- **Expected range for this variant**: 1.5 – 4.0×.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crash Severity

**Objective** (from analysis-bases.md §3): quantify how deep and how fast price falls.

**Implementation in `analysis.py`**:
- Function: `plot_fig3_crash_depth_analysis()`, `_detect_crash_window()`, `crash_depth()`.
- Input data: coordinator `price` series, config’s `fundamental`.
- Computation: pointwise deviation `(p - fundamental)/fundamental`, minimum, absolute value; trough index from `calculate_max_drawdown()`.
- Output: `fig3_crash_depth_analysis.png`, aliased to `02_flashcrash_analysis.png` via `_write_standard_named_outputs()`.

**Variant-Specific Interpretation**: For Rule, `crash_depth` should equal the analytic value implied by the price-impact formula and the HFT withdrawal window.

**Expected Output Description**: A two-panel figure — top: price versus fundamental with the trough highlighted; bottom: deviation curve dipping to −5 % … −12 % between rounds 16 and 30.

### Dimension 2: Liquidity Dynamics

**Objective**: measure when effective liquidity collapses and for how long.

**Implementation in `analysis.py`**:
- Function: `plot_fig1_price_liquidity_dynamics()`, `plot_fig4_liquidity_vacuum()`, `liquidity_vacuum_duration()`.
- Input data: coordinator `liquidity` batch store.
- Computation: threshold sweep at `low_threshold = 50.0`; contiguous vacuum shading.
- Output: `fig1_price_liquidity_dynamics.png` (→ `01_flashcrash_dynamics.png`) and `fig4_liquidity_vacuum.png`.

**Variant-Specific Interpretation**: A single well-defined vacuum window is expected; multi-modal vacuum shading indicates parameter mis-tuning.

**Expected Output Description**: liquidity trace stays near its baseline for the first 10 rounds, drops sharply below 50 during Cascade/Trough, and rebounds during Recovery.

### Dimension 3: Cascade Mechanics

**Objective**: measure stop-loss cascade timing and total volume.

**Implementation in `analysis.py`**:
- Function: `plot_fig5_stop_loss_cascade()`, `plot_fig7_agent_contribution()`, `stop_loss_cascade_volume()`.
- Input data: per-round `orders_history` reconstructed from investor payloads.
- Computation: per-round sum of |quantity| for StopLoss sells; per-round grouped bars per agent type.
- Output: `fig5_stop_loss_cascade.png` (→ `00_investor_bids.png`), `fig7_agent_contribution.png`.

**Variant-Specific Interpretation**: Bars should cluster in the Cascade phase; near-zero bars in Normal and Recovery.

**Expected Output Description**: strong bars in rounds 16–25 and a leading HFT-then-StopLoss ordering.

### Dimension 4: Recovery

**Objective**: identify who drives recovery and how long it takes to return within ±2 % of fundamental.

**Implementation in `analysis.py`**:
- Function: `plot_fig8_recovery_dynamics()`, `plot_fig6_hft_withdrawal()`, `recovery_speed()`, `liquidity_provider_withdrawal_fraction()`.
- Input data: post-trough price series, per-round `provides_liquidity` map.
- Computation: first round in `[trough, T)` re-entering the ±2 % band.
- Output: `fig8_recovery_dynamics.png` (→ `03_summary.png`), `fig6_hft_withdrawal.png`.

**Variant-Specific Interpretation**: withdrawal fraction should be near 1.0 during Cascade and drop back near 0 during Recovery; the recovery band should be crossed once, monotonically.

**Expected Output Description**: price curve reaches ±2 % band after 10–30 rounds; HFT-withdrawal panel shows a rectangular pulse aligned with the vacuum window.

### Dimension 5: Variant Differences

**Objective**: quantify how price amplification differs across variants.

**Implementation in `analysis.py`**: `price_amplification_ratio()` supplied to cross-variant `summary.json` diffing.

**Variant-Specific Interpretation**: Rule is the deterministic upper-bound reference; other variants should produce ratios less than or equal to Rule.

**Expected Output Description**: `summary.json → metrics.scenario_metrics.price_amplification_ratio` ≥ 1.5 for a well-tuned Rule run.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                    | Description                                                             | How to Observe                                                              | Contrast with Baseline Variant |
|-------------------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------------|
| Deterministic phase timing    | Cascade window aligns exactly with HFT `volatility_threshold` crossing  | `fig1_price_liquidity_dynamics.png` liquidity dip is a step function        | This is the baseline           |
| Threshold-locked stop-loss    | Every StopLossTrader with position triggers in the same round          | `fig5_stop_loss_cascade.png` shows a single dominant bar                    | This is the baseline           |
| Analytic amplification ratio | `price_amplification_ratio` matches the analytic price-impact formula   | `summary.json → metrics.scenario_metrics.price_amplification_ratio`         | This is the baseline           |

Rule is the reference: deterministic transitions, no reasoning stochasticity, no retrieval noise.

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                        | Phenomenon Clarity | Recommended for  |
|--------------|--------------------------------------------|--------------------|------------------|
| 100          | Cascade visible; recovery may be truncated | Low                | Quick testing    |
| 200          | Full Normal → Recovery arc                 | Medium             | Standard runs    |
| 500          | Statistical robustness across seeds        | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                    | Environment Dynamics                     |
|-------------|------------------------------------------------------------------------|------------------------------------------|
| 40          | Cascade still visible; noisier `stop_loss_cascade_volume`              | Low order density                        |
| 100         | Clean phase separation, stable metric estimates                         | Full mechanism observable                |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                    | Change | Expected Effect on This Variant's Analysis                                     |
|----------------------------------------------|--------|--------------------------------------------------------------------------------|
| `HighFrequencyTrader.volatility_threshold`   | +50 %  | Later withdrawal; shallower `crash_depth`; shorter `liquidity_vacuum_duration` |
| `HighFrequencyTrader.volatility_threshold`   | −50 %  | Earlier withdrawal; deeper crash; larger `price_amplification_ratio`           |
| `FundamentalTrader.value_threshold`          | +50 %  | Slower `recovery_speed`; recovery may not complete within total rounds         |
| `FundamentalTrader.value_threshold`          | −50 %  | Faster recovery; shallower trough                                              |
| `StopLossTrader` population share            | +50 %  | Larger `stop_loss_cascade_volume`; deeper crash                                |

---

## 6. Output Files Reference

All outputs written to `EXPERIMENT/FlashCrash/Rule/analysis/`.

| Output File                          | Generated By                                | Contents                                                       | How to Interpret                                                                             |
|--------------------------------------|---------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| `summary.json`                       | `main()`                                    | Metrics + validation + record path                             | `metrics.scenario_metrics` holds all six §2 values; `validation.is_valid` flags §6 ranges     |
| `00_investor_bids.png`               | `_write_standard_named_outputs()` alias of `fig5_stop_loss_cascade.png` | Per-round stop-loss sell volume                              | Bars concentrated in Cascade phase (rounds 16–25)                                           |
| `01_flashcrash_dynamics.png`         | alias of `fig1_price_liquidity_dynamics.png` | 3-panel price / liquidity / volume trajectory                | Trigger, Cascade, Trough, Recovery visible; liquidity dip aligned with price bottom          |
| `02_flashcrash_analysis.png`         | alias of `fig3_crash_depth_analysis.png`    | Deviation + trough diagnostic                                  | Deviation reaches −5 % … −12 %                                                              |
| `03_summary.png`                     | alias of `fig8_recovery_dynamics.png`       | Post-trough price arc with ±2 % band                           | Recovery within 10–30 rounds                                                                 |
| `fig2_phase_overlay.png`             | `plot_fig2_phase_overlay()`                 | Price with §4 phase bands shaded                              | Verify phase durations                                                                       |
| `fig4_liquidity_vacuum.png`          | `plot_fig4_liquidity_vacuum()`              | Liquidity with `low_threshold=50` line and shaded vacuum window | Single contiguous vacuum expected                                                          |
| `fig6_hft_withdrawal.png`            | `plot_fig6_hft_withdrawal()`                | Withdrawal fraction + crash-window bar                        | Pulse aligned with cascade                                                                   |
| `fig7_agent_contribution.png`        | `plot_fig7_agent_contribution()`            | Abs + signed volume by agent type                              | HFT and StopLoss dominate; FT re-enters during recovery                                       |

---

## 7. Cross-Variant Comparison Notes

Rule is the reference variant against which the LLM, RuleLLM, and Rag variants are compared (see `analysis-bases.md §5`).

| Comparison Axis        | Rule's Expected Position                       | Reason                                                                       |
|------------------------|------------------------------------------------|------------------------------------------------------------------------------|
| Phenomenon onset speed | Fastest                                        | Threshold rules trigger exactly at the boundary crossing                     |
| Phenomenon intensity   | Highest                                        | No discretionary hesitation; full HFT withdrawal                             |
| Behavioral realism     | Mechanistically clean; behaviourally simplistic | Individual agent behaviour ignores reasoning, narrative, or retrieved context |
| Decision quality       | Rule-optimal for the specified thresholds       | FTs recover value deterministically once `value_threshold` is crossed        |
