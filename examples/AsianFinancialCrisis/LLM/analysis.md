# AsianFinancialCrisis LLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                             |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                  |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                         |
| **Output Location**                 | `EXPERIMENT/AsianFinancialCrisis/LLM/records/analysis/`                                                                                                 |
| **Variant-Specific Considerations** | Behavioral/stochastic variant; highest variance across metrics; measures whether LLM personas produce realistic contagion without any formula anchoring |

---

## 1. Metric Implementation

LLM `analysis.py` imports core functions from `Rule/analysis.py` — all metrics are identical; only outcome values differ.

| Metric                     | Function              | analysis-bases.md Ref | LLM-Specific Notes                                                                      |
|----------------------------|-----------------------|-----------------------|-----------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `§2.1`                | High variance; LLM persona panic may cause deeper deviation than Rule                   |
| **Maximum Drawdown**       | `calculate_metrics()` | `§2.2`                | Expected 30%–70%; wider range than Rule; behavioral panic amplifies or inhibits         |
| **Crisis Velocity**        | `calculate_metrics()` | `§2.3`                | Variable; LLMHotMoneyFunder may exit faster or slower than Rule                         |
| **Return Autocorrelation** | `calculate_metrics()` | `§2.4`                | Positive AC1 possible if behavioral panic creates momentum; may be weaker than Rule     |
| **Agent-Type Volume**      | `calculate_metrics()` | `§2.5`                | Volumes stochastic; LLM personas may trade different quantities than rule-based targets |
| **Crisis Onset Round**     | `calculate_metrics()` | `§2.6`                | Highly variable (8–30 rounds); LLM persona sensitivity varies by run                    |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crisis Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `asianfinancialcrisis_llm_analysis.png` (4-panel: Price, Deviation, Returns, Distribution)

**Variant-Specific Interpretation:**
LLM shows wider crisis variability. If deviation fails to reach −30%, check LLMHotMoneyFunder reasoning field — the agent may be rationalizing a hold ("temporary noise"). If deviation exceeds −60%, behavioral panic amplification is dominant.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records; `reasoning` field logs LLM decision rationale
- Output: `summary.json` with volume breakdown

**Variant-Specific Interpretation:**
Check LLMIMFRescuer `reasoning` field — does it cite "emergency" or "threshold breach"? Does LLMContagionTrader explicitly mention "contagion spreading across borders" in its reasoning? These qualitative signals validate persona-fidelity.

---

### Dimension 3: Contagion Signal Analysis
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: return distribution and autocorrelation — same as Rule
- LLM-specific: wider return distribution tail (both directions) from behavioral stochasticity

**Variant-Specific Interpretation:**
LLM return distribution should show fatter tails than Rule in both directions. Left tail reflects panic selling; right tail reflects possible overreaction recovery. The distribution width is the primary LLM-specific fingerprint.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

LLM is the high-variance behavioral reference. RuleLLM and Rag should stay closer to Rule baseline. If LLM drawdown is consistently deeper than Rule, behavioral panic amplification is occurring; if shallower, personas are insufficiently responsive to deviation signals.

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                         | Description                                                                  | How to Observe                                      | Contrast with Rule                        |
|------------------------------------|------------------------------------------------------------------------------|-----------------------------------------------------|-------------------------------------------|
| **Behavioral Panic Amplification** | LLM agents sell more aggressively at moderate deviation than Rule thresholds | Compare crisis onset round LLM vs. Rule             | Rule: formula triggers at exact −2%       |
| **IMF Rescue Timing Variation**    | LLMIMFRescuer intervenes at subjective "emergency" level, not exact −5%      | IMFRescuer first buy round distribution across runs | Rule: always first buy at deviation < −5% |
| **Denial Psychology**              | LLMHotMoneyFunder may hold through moderate stress ("just temporary noise")  | HotMoneyFunder sell round vs. deviation timeline    | Rule: immediate sell at −2%               |
| **Stochastic Crisis Shape**        | Each run shows different crisis depth and onset round                        | Run 5+ seeds and overlay price curves               | Rule: identical curves per seed           |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                            |
|----------------|--------------------------------------------------------------------------------|
| **50 rounds**  | Full crisis lifecycle visible; persona variation most apparent in onset timing |
| **100 rounds** | Complete recovery; LLM recovery patterns may differ significantly from Rule    |

### Parameter Sensitivity

| Parameter     | Change         | Expected Effect                                                      |
|---------------|----------------|----------------------------------------------------------------------|
| `temperature` | 0.7 → 1.0      | More behavioral variance; more extreme crisis outcomes possible      |
| Seeds         | 1 run → 5 runs | Higher variance range visible; LLM stochasticity fully characterized |
| Agent count   | ×1 → ×2        | Crisis amplified; more LLM behavioral diversity in aggregate         |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/AsianFinancialCrisis/LLM/records/analysis/`.

| Output File                             | Generated By | Contents                                         | Interpretation                  |
|-----------------------------------------|--------------|--------------------------------------------------|---------------------------------|
| `asianfinancialcrisis_llm_analysis.png` | `main()`     | 4-panel: Price, Deviation, Returns, Distribution | Primary LLM crisis verification |
| `summary.json`                          | `main()`     | `{"variant": "LLM", metrics}`                    | Cross-variant comparison input  |

---

## 6. Cross-Variant Comparison Notes

- **Crash emergence speed**: Variable; persona sensitivity determines onset round
- **Crash intensity**: Highest variance; LLM panic can deepen or weaken crisis vs. Rule
- **Behavioral realism**: Highest (pure persona decisions); least formula-constrained
- **Reproducibility**: Lowest; each seed produces different crisis dynamics

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §5` — LLM variant description in agent diversity table
- `../analysis-bases.md §6` — Expected LLM result ranges (30%–70% drawdown)
- `Rule/analysis.py` — imported metric functions (`calculate_metrics`, `load_simulation_data`)
