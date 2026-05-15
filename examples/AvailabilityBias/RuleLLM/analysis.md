# AvailabilityBias RuleLLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                    |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                         |
| **Analysis Script**                 | `Rule/analysis.py` (imported)                                                                                                                  |
| **Output Location**                 | `EXPERIMENT/AvailabilityBias/RuleLLM/records/analysis/`                                                                                        |
| **Variant-Specific Considerations** | Rule-constrained LLM; lower bias amplitude than pure LLM; key diagnostic is whether formula embedding prevents SystematicAnalyst contamination |

---

## 1. Metric Implementation

| Metric                       | Function              | analysis-bases.md Ref | RuleLLM-Specific Notes                                                                        |
|------------------------------|-----------------------|-----------------------|-----------------------------------------------------------------------------------------------|
| **Bias Amplitude**           | `calculate_metrics()` | `§2.1`                | Expected 3%–8%; tighter than LLM (5%–15%); closer to Rule (3%–10%)                            |
| **Correction Ratio**         | `calculate_metrics()` | `§2.2`                | Higher than LLM; formula anchoring helps SystematicAnalyst counter-trade at correct threshold |
| **Bias Persistence**         | `calculate_metrics()` | `§2.3`                | Shorter than LLM; rule constraints limit denial episodes                                      |
| **Return Autocorrelation**   | `calculate_metrics()` | `§2.4`                | Intermediate; formula-driven momentum but LLM quantity variation adds noise                   |
| **Agent-Type Volume**        | `calculate_metrics()` | `§2.5`                | Volumes closer to Rule; formula thresholds prevent spurious trading                           |
| **Availability Event Onset** | `calculate_metrics()` | `§2.6`                | Expected rounds 5–20; tighter than LLM (5–25)                                                 |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Bias Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation:** `load_simulation_data()` → `availabilitybias_rulellm_analysis.png`

**Variant-Specific Interpretation:**
RuleLLM bias trajectory should follow Rule's shape with 1–2 round timing variation. If bias amplitude > 10%, check whether RecencyOverweighter is computing formula correctly (its reasoning should show "perceived_signal = 3.0 × return_pct...").

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Key Diagnostic:** Does RuleLLMSystematicAnalyst's reasoning contain "return_pct" mentions? If yes, rule constraint prohibiting return_pct use is being violated — SystematicAnalyst contamination occurred despite rule embedding.

---

### Dimension 3: Correction Dynamics
*(Objective from analysis-bases.md §3.3)*

**Variant-Specific Interpretation:**
RuleLLM correction should be smoother than LLM. Formula-anchored SystematicAnalyst activates at exact ±0.03 deviation threshold. Compare correction_ratio trajectory to Rule and LLM baselines.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

RuleLLM is the "disciplined" hypothesis: does formula embedding successfully isolate the two availability channels and prevent contamination? Expected order: Rule ≤ RuleLLM bias < LLM bias.

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                          | How to Observe                                 |
|-----------------------------------------|----------------------------------------------------------------------|------------------------------------------------|
| **Formula Citation in Reasoning**       | Agents cite exact formula values (3.0×, 0.05 threshold) in reasoning | Grep reasoning for "3.0" or "perceived_signal" |
| **SystematicAnalyst Isolation Success** | LLMSystematicAnalyst does not mention return_pct in reasoning        | Grep SystematicAnalyst reasoning for "return"  |
| **Tighter Bias Range**                  | Multiple runs show narrower peak deviation IQR than LLM              | Run 5 seeds; compare IQR vs. LLM               |

---

## 4. Scaling and Sensitivity Analysis

| Parameter     | Change     | Expected Effect                                                          |
|---------------|------------|--------------------------------------------------------------------------|
| `temperature` | 0.7 → 1.0  | More variance; formula embedding less effective at constraining behavior |
| Seeds         | 1 → 5 runs | Confirm RuleLLM variance is between Rule (zero) and LLM (high)           |

---

## 5. Output Files Reference

| Output File                             | Generated By              | Contents                                         | Interpretation                    |
|-----------------------------------------|---------------------------|--------------------------------------------------|-----------------------------------|
| `availabilitybias_rulellm_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Agent Volume | Primary RuleLLM bias verification |
| `metrics.json`                          | `main()`                  | `{"variant": "RuleLLM", metrics}`                | Cross-variant comparison input    |

---

## 6. Cross-Variant Comparison Notes

- **Bias amplitude**: Intermediate (Rule ≤ RuleLLM < LLM expected order)
- **Correction**: Faster and more reliable than LLM due to SystematicAnalyst rule enforcement
- **Formula adherence**: Key test — does RecencyOverweighter compute formula in reasoning chain?

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §4` — Availability bias archetype specifications
- `Rule/analysis.py` — imported metric functions
