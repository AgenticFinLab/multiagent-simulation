# BlackMonday1987 Rule — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                              |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                   |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                          |
| **Output Location**                 | `EXPERIMENT/BlackMonday1987/Rule/records/analysis/`                                                                                                      |
| **Variant-Specific Considerations** | Deterministic baseline (modulo NoiseTrader randomness); provides calibration reference for cross-variant comparison of crash depth and feedback strength |

---

## 1. Metric Implementation

All metrics defined in `../analysis-bases.md §2`. Rule `analysis.py` is the authoritative implementation — all other variants import from it.

| Metric                     | Function              | analysis-bases.md Ref | Rule-Specific Notes                                                        |
|----------------------------|-----------------------|-----------------------|----------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `§2.1`                | Deterministic cascade; deviation follows predictable feedback spiral       |
| **Maximum Drawdown**       | `calculate_metrics()` | `§2.2`                | Calibration target 15%–35%; Rule shows cleanest drawdown matching formulas |
| **Crash Velocity**         | `calculate_metrics()` | `§2.3`                | Max deviation rate per round; ProgramTrader amplification visible          |
| **Return Autocorrelation** | `calculate_metrics()` | `§2.4`                | AC1 > 0.3 during crash (feedback loop); AC1 < 0 during recovery            |
| **Agent-Type Volume**      | `calculate_metrics()` | `§2.5`                | PortfolioInsurer + ProgramTrader dominate sell volume; verifiable          |
| **Crash Onset Round**      | `calculate_metrics()` | `§2.6`                | First round deviation < −5%; Rule: expected rounds 5–20                    |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crash Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `blackmonday1987_analysis.png` (4-panel: Price, Deviation, Returns, Distribution)

**Variant-Specific Interpretation:**
Rule shows clean, formula-driven feedback: as deviation deepens, ProgramTrader sell orders grow (amplification formula). If crash doesn't reach −15%, check `feedback_strength` and `price_impact`.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records
- Output: `metrics.json` with volume breakdown by agent

**Variant-Specific Interpretation:**
ProgramTrader should show growing sell sizes per round (amplification). PortfolioInsurer sells should grow proportionally with deviation. ValueInvestor activates exactly at −15%.

---

### Dimension 3: Feedback Loop Intensity
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: `returns = np.diff(prices) / prices[:-1]`; return distribution
- Output: return time series; return distribution

**Variant-Specific Interpretation:**
Return distribution should show strong left tail (large negative returns during crash phase). Rolling return autocorrelation should be positive (0.3–0.6) during crash then negative during recovery.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rule is the deterministic reference. Other variants compared against Rule's drawdown magnitude and onset round.

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                      | Description                                                           | How to Observe                                 | Contrast with LLM                   |
|---------------------------------|-----------------------------------------------------------------------|------------------------------------------------|-------------------------------------|
| **Amplification Visible**       | ProgramTrader sell orders grow larger each round as deviation deepens | Per-round ProgramTrader volume records         | LLM: may not amplify proportionally |
| **Deterministic Crash Shape**   | Same crash curve in each run (given same seed)                        | Multiple runs overlay                          | LLM: variable crash shape           |
| **ValueInvestor Exact Trigger** | ValueInvestor buys start exactly at deviation = −15%                  | First ValueInvestor buy round in order records | LLM: buying may start earlier/later |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                   |
|----------------|-----------------------------------------------------------------------|
| **50 rounds**  | Full crash lifecycle visible (fast feedback loop); recovery beginning |
| **100 rounds** | Complete recovery visible; all phases observable                      |

### Parameter Sensitivity

| Parameter           | Change        | Expected Effect                               |
|---------------------|---------------|-----------------------------------------------|
| `feedback_strength` | 0.3 → 0.5     | Deeper crash; faster amplification            |
| `price_impact`      | 0.002 → 0.005 | Larger price moves per round; faster drawdown |
| `value_discount`    | 0.15 → 0.20   | Floor at deeper level; longer crash duration  |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/BlackMonday1987/Rule/records/analysis/`.

| Output File                    | Generated By              | Contents                                         | Interpretation                            |
|--------------------------------|---------------------------|--------------------------------------------------|-------------------------------------------|
| `blackmonday1987_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Distribution | Primary crash verification                |
| `metrics.json`                 | `main()`                  | price_metrics, deviation_metrics, volatility     | Machine-readable cross-variant comparison |

---

## 6. Cross-Variant Comparison Notes

- **Crash emergence speed**: Rule shows fastest, most predictable crash (immediate formula triggers)
- **Crash intensity**: Rule max drawdown is calibration target; other variants compared against this
- **Behavioral realism**: Rule is least realistic (no psychology) but most interpretable
- **Feedback clarity**: Rule shows purest feedback amplification signal; no LLM noise

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §3.1` — price formula
- `../simulation-bases.md §4` — investor type specs and rule-based behavior
- `../simulation-bases.md §6` — parameter calibration
