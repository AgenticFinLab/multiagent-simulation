# AsianFinancialCrisis RuleLLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                      |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                           |
| **Analysis Script**                 | `Rule/analysis.py` (imported — RuleLLM uses Rule analysis functions)                                                                             |
| **Output Location**                 | `EXPERIMENT/AsianFinancialCrisis/RuleLLM/records/analysis/`                                                                                      |
| **Variant-Specific Considerations** | Rule-constrained LLM; lower variance than pure LLM; expected to stay within ~10% of Rule drawdown range; reasoning fields confirm rule adherence |

---

## 1. Metric Implementation

RuleLLM shares all metric functions with `Rule/analysis.py` — no separate analysis.py needed.

| Metric                     | Function              | analysis-bases.md Ref | RuleLLM-Specific Notes                                                                   |
|----------------------------|-----------------------|-----------------------|------------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `§2.1`                | Lower variance than LLM; rule anchoring prevents extreme behavioral deviation            |
| **Maximum Drawdown**       | `calculate_metrics()` | `§2.2`                | Expected 25%–55%; tighter range than LLM (30%–70%); closer to Rule (30%–60%)             |
| **Crisis Velocity**        | `calculate_metrics()` | `§2.3`                | Moderate; rule-anchored agents trigger at near-threshold rather than before it           |
| **Return Autocorrelation** | `calculate_metrics()` | `§2.4`                | Similar to Rule; rule constraints reduce spurious momentum from behavioral amplification |
| **Agent-Type Volume**      | `calculate_metrics()` | `§2.5`                | Volume patterns closer to Rule; HotMoneyFunder sells near −2%, not significantly before  |
| **Crisis Onset Round**     | `calculate_metrics()` | `§2.6`                | Expected rounds 10–25; tighter range than LLM (8–30)                                     |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crisis Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `asianfinancialcrisis_rulellm_analysis.png` (4-panel: Price, Deviation, Returns, Distribution)

**Variant-Specific Interpretation:**
RuleLLM should produce crisis trajectories that broadly follow Rule's shape but with 1–3 round variation in onset timing. If crisis depth significantly exceeds Rule, check reasoning fields: are agents ignoring embedded rules and behaving as pure LLM?

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records
- RuleLLM-specific: inspect `reasoning` field — should cite rule thresholds (e.g., "deviation is −0.025 which exceeds my threshold")

**Variant-Specific Interpretation:**
Key diagnostic: does RuleLLMContagionTrader's `reasoning` field contain the signal computation (0.60 × deviation + 0.40 × return) or just qualitative language? Signal computation present = rule adherence confirmed. Absent = pure behavioral reasoning dominant.

---

### Dimension 3: Contagion Signal Analysis
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: return distribution and autocorrelation — same as Rule
- RuleLLM-specific: compare distribution width vs. Rule and LLM baselines

**Variant-Specific Interpretation:**
RuleLLM return distribution should be intermediate between Rule (narrow, deterministic) and LLM (wide, stochastic). If distribution is as wide as LLM, rule embedding is ineffective. If as narrow as Rule, LLM component adds no value.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

RuleLLM serves as the "disciplined hybrid" reference point. Key question: does rule embedding successfully constrain LLM variance? Expected: RuleLLM drawdown range ≈ [Rule center ± 10%], narrower than LLM's [Rule center ± 20%].

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                      | Description                                                                  | How to Observe                                       | Contrast with LLM                               |
|---------------------------------|------------------------------------------------------------------------------|------------------------------------------------------|-------------------------------------------------|
| **Rule Citation in Reasoning**  | Agents reference specific thresholds in reasoning field                      | Grep reasoning for threshold values (−0.02, −0.025)  | LLM: qualitative language only                  |
| **Reduced Behavioral Variance** | Multiple runs show tighter drawdown range than pure LLM                      | Run 5 seeds, compare IQR of max drawdown             | LLM: wide IQR; Rule: zero variance              |
| **Near-Threshold Triggering**   | Agent actions cluster near (not randomly distributed around) rule thresholds | Histogram of deviation values at agent action rounds | LLM: actions spread across deviation range      |
| **Intermediate Crisis Depth**   | Max drawdown between Rule and LLM extremes                                   | Plot drawdown: Rule < RuleLLM ≤ LLM (expected order) | Rule: deterministic floor; LLM: stochastic peak |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                                  |
|----------------|--------------------------------------------------------------------------------------|
| **50 rounds**  | Full crisis lifecycle; rule adherence visible in agent timing vs. Rule baseline      |
| **100 rounds** | Complete recovery; rule-anchored agents show more predictable recovery path than LLM |

### Parameter Sensitivity

| Parameter     | Change         | Expected Effect                                                             |
|---------------|----------------|-----------------------------------------------------------------------------|
| `temperature` | 0.7 → 1.0      | Higher LLM variance; rule embedding becomes less effective                  |
| Seeds         | 1 run → 5 runs | Variance characterization; confirm RuleLLM is between Rule and LLM variance |
| `lm_name`     | pro → lite     | Weaker rule adherence with smaller model; reasoning quality degrades        |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/AsianFinancialCrisis/RuleLLM/records/analysis/`.

| Output File                                 | Generated By              | Contents                                         | Interpretation                      |
|---------------------------------------------|---------------------------|--------------------------------------------------|-------------------------------------|
| `asianfinancialcrisis_rulellm_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Distribution | Primary RuleLLM crisis verification |
| `metrics.json`                              | `main()`                  | `{"variant": "RuleLLM", metrics}`                | Cross-variant comparison input      |

---

## 6. Cross-Variant Comparison Notes

- **Crash emergence speed**: Closer to Rule than LLM; threshold-anchored agents trigger at expected deviation levels
- **Crash intensity**: Intermediate; rule constraints dampen but do not eliminate behavioral amplification
- **Behavioral realism**: Moderate; rule-embedded prompts produce reasoning that references quantitative thresholds
- **Reproducibility**: Better than LLM; rule anchoring reduces run-to-run variance

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §5` — RuleLLM variant description in agent diversity table
- `../analysis-bases.md §6` — Expected RuleLLM result ranges
- `Rule/analysis.py` — imported metric functions (`calculate_metrics`, `load_simulation_data`)
- `prompts.py → RULELLM_*_SYS` — Rule-embedded behavioral persona prompts
