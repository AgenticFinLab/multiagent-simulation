# AsianFinancialCrisis Rule — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                            |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                 |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                        |
| **Output Location**                 | `EXPERIMENT/AsianFinancialCrisis/Rule/records/analysis/`                                                                               |
| **Variant-Specific Considerations** | Deterministic baseline; provides calibration reference for cross-variant comparison of crisis depth and contagion signal effectiveness |

---

## 1. Metric Implementation

All metrics defined in `../analysis-bases.md §2`. Rule `analysis.py` is the authoritative implementation — all other variants import from it.

| Metric                     | Function              | analysis-bases.md Ref | Rule-Specific Notes                                                                   |
|----------------------------|-----------------------|-----------------------|---------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `§2.1`                | Deterministic cascade; deviation follows predictable contagion spiral                 |
| **Maximum Drawdown**       | `calculate_metrics()` | `§2.2`                | Calibration target 30%–60%; Rule shows cleanest drawdown matching threshold formulas  |
| **Crisis Velocity**        | `calculate_metrics()` | `§2.3`                | Max price change per round; HotMoneyFunder + ContagionTrader combined selling visible |
| **Return Autocorrelation** | `calculate_metrics()` | `§2.4`                | AC1 > 0.2 during contagion phase; negative in recovery                                |
| **Agent-Type Volume**      | `calculate_metrics()` | `§2.5`                | HotMoneyFunder + ContagionTrader dominate sell volume; IMFRescuer dominates buy       |
| **Crisis Onset Round**     | `calculate_metrics()` | `§2.6`                | First round deviation < −10%; Rule: expected rounds 10–20                             |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crisis Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `asianfinancialcrisis_analysis.png` (4-panel: Price, Deviation, Returns, Distribution)

**Variant-Specific Interpretation:**
Rule shows clean, formula-driven contagion: as deviation deepens past −2%, HotMoneyFunder reverses; at −2.5% signal, ContagionTrader amplifies. If crisis doesn't reach −30%, check `price_impact` (should be 0.04) and agent instance counts.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records
- Output: `metrics.json` with volume breakdown by agent

**Variant-Specific Interpretation:**
HotMoneyFunder first sell round should match first round `deviation < −0.02`. ContagionTrader first sell depends on `price_return` signal — may lag by 1 round if price momentum just turned negative. IMFRescuer activates exactly at deviation < −0.05.

---

### Dimension 3: Contagion Signal Analysis
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: `returns = np.diff(prices) / prices[:-1]`; return distribution and autocorrelation
- Output: return time series (Panel 3); return distribution (Panel 4)

**Variant-Specific Interpretation:**
Return distribution should show strong left tail (large negative returns during contagion phase). Rolling return autocorrelation should be positive (0.2–0.5) during contagion then negative during recovery.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rule is the deterministic reference. Other variants compared against Rule's drawdown magnitude and crisis onset round. Key question: does LLM behavioral panic produce deeper or shallower drawdown than formula?

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                        | Description                                                                | How to Observe                                      | Contrast with LLM                           |
|-----------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------|---------------------------------------------|
| **Contagion Signal Cascade**      | ContagionTrader signal activates exactly when dual-negative conditions met | ContagionTrader first sell round vs. signal formula | LLM: may sell earlier from behavioral panic |
| **IMF Exact Threshold**           | IMFRescuer buys start exactly at deviation = −5%                           | First IMFRescuer buy round in order records         | LLM: patience may vary round-to-round       |
| **Deterministic Crisis Shape**    | Same crisis trajectory in each run (given same seed)                       | Multiple runs overlay — identical curves            | LLM: variable crisis shape and depth        |
| **ValueContrarian Exact Trigger** | ValueContrarian buys start exactly at deviation = −8%                      | First ValueContrarian buy round                     | LLM: buying may start at different levels   |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                   |
|----------------|-------------------------------------------------------|
| **50 rounds**  | Full crisis lifecycle (onset → peak → early recovery) |
| **100 rounds** | Complete recovery visible; all 5 phases observable    |

### Parameter Sensitivity

| Parameter            | Change        | Expected Effect                                         |
|----------------------|---------------|---------------------------------------------------------|
| `price_impact`       | 0.04 → 0.06   | Deeper crisis; faster depreciation cascade              |
| `contagion_weight`   | 0.60 → 0.80   | Stronger deviation-driven selling; earlier crisis onset |
| `rescue_threshold`   | −0.05 → −0.08 | Delayed IMF intervention; deeper trough before floor    |
| `oversold_threshold` | −0.08 → −0.15 | ValueContrarian provides floor only at deeper discounts |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/AsianFinancialCrisis/Rule/records/analysis/`.

| Output File                         | Generated By              | Contents                                         | Interpretation                            |
|-------------------------------------|---------------------------|--------------------------------------------------|-------------------------------------------|
| `asianfinancialcrisis_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Distribution | Primary crisis verification               |
| `metrics.json`                      | `main()`                  | price_metrics, deviation_metrics, crisis_metrics | Machine-readable cross-variant comparison |

---

## 6. Cross-Variant Comparison Notes

- **Crash emergence speed**: Rule shows fastest, most predictable crisis (immediate formula triggers)
- **Crash intensity**: Rule max drawdown is calibration reference (30–60%); other variants compared against this
- **Behavioral realism**: Rule is least realistic (no psychology) but most interpretable
- **Contagion clarity**: Rule shows purest dual-signal contagion; no LLM noise or persona variation

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §3.1` — price formula (λ=0.04 rationale)
- `../simulation-bases.md §4` — investor type specs and threshold rules
- `../simulation-bases.md §8` — historical calibration targets (30–60% drawdown)
