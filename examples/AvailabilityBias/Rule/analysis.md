# AvailabilityBias Rule — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                      |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                           |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                  |
| **Output Location**                 | `EXPERIMENT/AvailabilityBias/Rule/records/analysis/`                                                                             |
| **Variant-Specific Considerations** | Deterministic baseline; availability bias channels are algebraic — provides calibration reference for LLM/RuleLLM/Rag comparison |

---

## 1. Metric Implementation

All metrics defined in `../analysis-bases.md §2`. Rule `analysis.py` is the reference implementation — all other variants import from it.

| Metric                       | Function              | analysis-bases.md Ref | Rule-Specific Notes                                                                       |
|------------------------------|-----------------------|-----------------------|-------------------------------------------------------------------------------------------|
| **Bias Amplitude**           | `calculate_metrics()` | `§2.1`                | Peak deviation from fundamental caused by availability bias; target 3–10%                 |
| **Correction Ratio**         | `calculate_metrics()` | `§2.2`                | Fraction of bias corrected by end of simulation; Rule shows cleanest correction shape     |
| **Bias Persistence**         | `calculate_metrics()` | `§2.3`                | Rounds until price returns within 1% of fundamental; Rule provides minimum persistence    |
| **Return Autocorrelation**   | `calculate_metrics()` | `§2.4`                | Positive AC during bias amplification; negative during correction; Rule is deterministic  |
| **Agent-Type Volume**        | `calculate_metrics()` | `§2.5`                | RecentEventOverweighter + MediaInfluencedTrader dominate overreaction phase volume        |
| **Availability Event Onset** | `calculate_metrics()` | `§2.6`                | Round when bias exceeds 3% threshold; Rule: predictable from noise_std and recency_weight |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Bias Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → price/fundamental from `records/market/*.json`
- Output: `availabilitybias_analysis.png` (4-panel: Price, Deviation, Returns, Agent Volume)

**Variant-Specific Interpretation:**
Rule shows cleanest bias shape: sharp overreaction when `return_pct` triggers RecencyOverweighter, followed by media amplification, then systematic correction. If bias amplitude < 3%, noise_std may be too low or recency_weight too weak.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records
- Output: `metrics.json` with volume breakdown by agent type and phase

**Variant-Specific Interpretation:**
RecencyOverweighter first buys should match first round where `|return_pct| > 0.05 / recency_weight`. MediaInfluencedTrader activates when `|deviation| > threshold / (media_weight × social_amplification)`. SystematicAnalyst's counter-trades should appear immediately after bias creates |deviation| > 0.03.

---

### Dimension 3: Correction Dynamics
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: rolling correction_ratio = (peak_deviation − current_deviation) / peak_deviation
- Output: correction ratio time series in Panel 2

**Variant-Specific Interpretation:**
Rule correction is smooth and monotonic (no behavioral noise). ValueTrader + SystematicAnalyst progressively correct bias. If correction_ratio < 0.5 by end of run, availability bias is persistent (mean reversion too weak).

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rule is the deterministic reference. Key question: do LLM availability personas produce deeper or shallower bias than formula? Expected: LLM bias amplitude higher (persona panic); Rag bias lower (historical calibration moderates overreaction).

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                          | Description                                                                     | How to Observe                                       | Contrast with LLM                           |
|-------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------|---------------------------------------------|
| **Dual-Channel Availability**       | Both recency and media channels fire simultaneously during event                | RecencyOverweighter + MediaInfluencedTrader buying   | LLM: channels may fire at different rounds  |
| **SystematicAnalyst Exact Trigger** | Counter-trade starts exactly at deviation = ±0.03                               | First SystematicAnalyst trade round                  | LLM: subjective "overvalued" assessment     |
| **Deterministic Bias Shape**        | Same bias trajectory in each run (given same seed)                              | Multiple runs overlay — identical curves             | LLM: variable bias amplitude per run        |
| **Recency Decay**                   | Bias fades as return_pct reverts; RecencyOverweighter stops trading after shock | RecencyOverweighter volume drops in correction phase | LLM: may linger due to behavioral narrative |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                     |
|----------------|-------------------------------------------------------------------------|
| **50 rounds**  | Bias event + peak + early correction; full lifecycle if noise_std ≥ 0.5 |
| **100 rounds** | Complete correction + stabilization; all 5 phases observable            |

### Parameter Sensitivity

| Parameter              | Change      | Expected Effect                                                  |
|------------------------|-------------|------------------------------------------------------------------|
| `recency_weight`       | 3.0 → 5.0   | Deeper bias amplitude; faster RecencyOverweighter activation     |
| `social_amplification` | 1.5 → 2.5   | Amplified media channel; bias_amplitude increases proportionally |
| `evidence_threshold`   | 0.03 → 0.05 | SystematicAnalyst activates later; longer bias persistence       |
| `price_impact`         | 0.01 → 0.02 | Faster price response to orders; sharper bias spike              |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/AvailabilityBias/Rule/records/analysis/`.

| Output File                     | Generated By              | Contents                                         | Interpretation                            |
|---------------------------------|---------------------------|--------------------------------------------------|-------------------------------------------|
| `availabilitybias_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Agent Volume | Primary bias verification                 |
| `metrics.json`                  | `main()`                  | bias_metrics, correction_metrics, agent_volumes  | Machine-readable cross-variant comparison |

---

## 6. Cross-Variant Comparison Notes

- **Bias amplitude**: Rule is calibration reference (3–10%); LLM expected higher; Rag expected lower
- **Correction speed**: Rule fastest and most predictable; LLM slowest (behavioral denial possible)
- **Behavioral realism**: Rule is least realistic; provides pure formula baseline
- **Channel independence**: Rule channels are algebraically independent; LLM channels may co-vary through narrative

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §3.1, §3.3` — Price formula and broadcast variables (return_pct)
- `../simulation-bases.md §4` — Investor type specs and threshold formulas
- `../simulation-bases.md §8` — Historical calibration targets (availability event magnitude)
