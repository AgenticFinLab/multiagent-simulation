# FlashCrash RuleLLM — Analysis Documentation

## 1. Overview

| Item                            | Description                                                                                                                                                     |
|---------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                          |
| Analysis Script                 | `analysis.py` in this directory (thin reuse — delegates to `../Rule/analysis.py:main`)                                                                          |
| Output Location                 | `EXPERIMENT/FlashCrash/RuleLLM/analysis/`                                                                                                                       |
| Imports From                    | `../Rule/analysis.py`: `main` (which internally uses `load_simulation_data`, `calculate_metrics`, `validate_flash_crash`, `create_visualizations`, `_write_standard_named_outputs`) |
| Variant-Specific Functions      | None                                                                                                                                                            |
| Variant-Specific Considerations | RuleLLM investors embed the Rule threshold logic inside an LLM prompt so the *characterisation* is richer but the *decision boundary* is the same as Rule. Downstream metrics therefore match Rule closely, with a residual LLM stochasticity around the boundary. |

---

## 2. Metric Implementation

All six metrics are reused verbatim from `Rule/analysis.py`. The script contains only a thin re-entry:

```python
# examples/FlashCrash/RuleLLM/analysis.py
from examples.FlashCrash.Rule.analysis import main
__all__ = ["main"]
if __name__ == "__main__":
    main()
```

`Rule/analysis.py:load_simulation_data()` classifies agents by `_classify_agent_type()`, which substring-matches strategy class names (`RuleLLMStopLossTrader`, `RuleLLMHighFrequencyTrader`, …). No RuleLLM-specific dispatch is required.

### Metric: crash_depth

- **Defined in**: `analysis-bases.md §2 — crash_depth`
- **Implemented in**: `Rule/analysis.py → crash_depth()`
- **Data source**: `EXPERIMENT/FlashCrash/RuleLLM/records/` coordinator `price` batch store.
- **Implementation details**:
  ```python
  # via Rule.main(): calculate_metrics(data, config)["scenario_metrics"]["crash_depth"]
  ```
- **Variant-specific notes**: matches Rule within ~10 % — the embedded LLM only softens the decision boundary rather than replacing it.
- **Expected range for this variant**: 0.05 – 0.12.

### Metric: liquidity_vacuum_duration

- **Defined in**: `analysis-bases.md §2 — liquidity_vacuum_duration`
- **Implemented in**: `Rule/analysis.py → liquidity_vacuum_duration()`
- **Data source**: coordinator `liquidity`.
- **Variant-specific notes**: same as Rule; the LLM does not participate in liquidity computation.
- **Expected range for this variant**: 5 – 20 rounds.

### Metric: stop_loss_cascade_volume

- **Defined in**: `analysis-bases.md §2 — stop_loss_cascade_volume`
- **Implemented in**: `Rule/analysis.py → stop_loss_cascade_volume()`
- **Data source**: RuleLLM investor payloads (`bid_price`, `quantity`, `strategy = "RuleLLMStopLossTrader"`).
- **Variant-specific notes**: expected to be very close to Rule because the RuleLLM stop-loss agent still enforces the rule; small deviations arise only when the LLM parse falls back.
- **Expected range for this variant**: 500 – 3000 shares.

### Metric: recovery_speed

- **Defined in**: `analysis-bases.md §2 — recovery_speed`
- **Implemented in**: `Rule/analysis.py → recovery_speed()`
- **Data source**: coordinator `price`.
- **Variant-specific notes**: modest variance around Rule.
- **Expected range for this variant**: 10 – 30 rounds.

### Metric: liquidity_provider_withdrawal_fraction

- **Defined in**: `analysis-bases.md §2 — liquidity_provider_withdrawal_fraction`
- **Implemented in**: `Rule/analysis.py → liquidity_provider_withdrawal_fraction()`
- **Data source**: RuleLLM investor payloads `provides_liquidity`.
- **Variant-specific notes**: HFT agent still uses the rule threshold; withdrawal fraction ≈ Rule.
- **Expected range for this variant**: 0.6 – 1.0.

### Metric: price_amplification_ratio

- **Defined in**: `analysis-bases.md §2 — price_amplification_ratio`
- **Implemented in**: `Rule/analysis.py → price_amplification_ratio()`
- **Data source**: coordinator `price`.
- **Variant-specific notes**: intermediate between Rule (upper bound) and pure LLM (lower bound).
- **Expected range for this variant**: 1.4 – 3.8×.

---

## 3. Dimension-by-Dimension Analysis

### Dimension 1: Crash Severity

**Objective**: quantify how deep and how fast price falls.

**Implementation**: `Rule/analysis.py → calculate_metrics()` / `plot_fig3_crash_depth_analysis()`.

**Variant-Specific Interpretation**: matches Rule to within LLM parse noise; trough depth may be one round earlier or later than Rule.

**Expected Output Description**: `02_flashcrash_analysis.png` looks nearly identical to the Rule figure.

### Dimension 2: Liquidity Dynamics

**Objective**: measure liquidity collapse timing and duration.

**Implementation**: `liquidity_vacuum_duration()`, `plot_fig1_price_liquidity_dynamics()`, `plot_fig4_liquidity_vacuum()`.

**Variant-Specific Interpretation**: same as Rule.

**Expected Output Description**: same as Rule.

### Dimension 3: Cascade Mechanics

**Objective**: measure stop-loss cascade timing and volume.

**Implementation**: `stop_loss_cascade_volume()`, `plot_fig5_stop_loss_cascade()`, `plot_fig7_agent_contribution()`.

**Variant-Specific Interpretation**: The bar histogram at Cascade may show a small right-tail relative to Rule (LLM occasionally delays fire).

**Expected Output Description**: `00_investor_bids.png` largely matches Rule; small residual tail expected.

### Dimension 4: Recovery

**Objective**: identify recovery drivers and speed.

**Implementation**: `recovery_speed()`, `plot_fig8_recovery_dynamics()`, `plot_fig6_hft_withdrawal()`.

**Variant-Specific Interpretation**: LLM-augmented fundamental traders may reason about oversold conditions faster; recovery speed distribution has a small left-shift.

**Expected Output Description**: `03_summary.png` shows recovery within 10–30 rounds.

### Dimension 5: Variant Differences

**Objective**: characterise the residual LLM effect on rule-embedded agents.

**Implementation**: cross-variant `summary.json` comparison.

**Variant-Specific Interpretation**: distance between RuleLLM and Rule metrics quantifies the *cost* of LLM boundary approximation; distance between RuleLLM and pure LLM quantifies the *value* of explicit quantitative guidance.

**Expected Output Description**: `metrics.scenario_metrics` values slightly perturbed from Rule.

---

## 4. Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                | How to Observe                                                             | Contrast with Baseline Variant                              |
|-----------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------|
| Rule-locked cascade with LLM commentary | Cascade timing matches Rule, but investor `reasoning` payloads narrate the boundary crossing | Inspect investor `turns.payloads()` `reasoning` field around the vacuum window | Rule payloads carry no `reasoning`; pure LLM cascade drifts |
| LLM parse-fallback events               | Occasional LLM parse failure defaults to the embedded Rule action          | Investor `strategy` is `RuleLLM*` but payload lacks `reasoning`             | Rule never falls back; pure LLM has no rule to fall back to |
| Reduced amplification ratio             | `price_amplification_ratio` slightly below Rule                            | `summary.json → metrics.scenario_metrics.price_amplification_ratio`         | Rule is the upper bound                                     |

---

## 5. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                          | Phenomenon Clarity | Recommended for  |
|--------------|----------------------------------------------|--------------------|------------------|
| 100          | Cascade visible; parse-fallback events rare  | Low                | Quick testing    |
| 200          | Full arc; RuleLLM ≈ Rule metrics             | Medium             | Standard runs    |
| 500          | Enough LLM samples to see boundary softening | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                              | Environment Dynamics                              |
|-------------|------------------------------------------------------------------|---------------------------------------------------|
| 40          | Metrics dominated by shot noise                                 | Rule-like                                         |
| 100         | Stable metrics                                                  | Full mechanism observable                         |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                                          |
|----------------------------------------|--------|-----------------------------------------------------------------------------------------------------|
| LLM temperature                        | +      | Larger boundary jitter; recovery-speed variance grows                                              |
| LLM temperature                        | −      | RuleLLM converges to Rule                                                                          |
| Embedded rule threshold (volatility)   | ±50 %  | Same qualitative effect as Rule (see Rule/analysis.md §5)                                          |

---

## 6. Output Files Reference

All outputs written to `EXPERIMENT/FlashCrash/RuleLLM/analysis/`. Files are identical in name and interpretation to the Rule variant, produced by `Rule/analysis.py:main()`:

| Output File                    | Generated By                                | Contents                                       | How to Interpret                                                             |
|--------------------------------|---------------------------------------------|------------------------------------------------|------------------------------------------------------------------------------|
| `summary.json`                 | `Rule.analysis.main()` (delegated)          | Metrics + validation + record path             | Metric values should track Rule within a few percent                         |
| `00_investor_bids.png`         | alias of `fig5_stop_loss_cascade.png`       | Per-round stop-loss sell volume                | Compare against Rule; light smearing expected                                |
| `01_flashcrash_dynamics.png`   | alias of `fig1_price_liquidity_dynamics.png` | Price / liquidity / volume trajectory        | Same shape as Rule                                                            |
| `02_flashcrash_analysis.png`   | alias of `fig3_crash_depth_analysis.png`    | Crash-depth diagnostic                         | Trough within one round of Rule                                              |
| `03_summary.png`               | alias of `fig8_recovery_dynamics.png`       | Post-trough price arc                          | Recovery within 10–30 rounds                                                 |
| `fig2` – `fig8`                | (same as Rule)                              | (same as Rule)                                  | (same as Rule)                                                                |

---

## 7. Cross-Variant Comparison Notes

| Comparison Axis        | RuleLLM Variant's Expected Position                                              | Reason                                                                              |
|------------------------|----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| Phenomenon onset speed | Same as Rule                                                                     | Threshold still triggers deterministically inside the embedded LLM prompt           |
| Phenomenon intensity   | Slightly below Rule                                                              | Occasional LLM boundary softening reduces peak cascade                              |
| Behavioral realism     | Higher than Rule, lower than LLM                                                 | Embedded reasoning adds narrative without departing from the rule                   |
| Decision quality       | Best-of-both — quantitative guidance plus reasoning-augmented characterisation   | Combines Rule’s discipline with LLM interpretability                                |
