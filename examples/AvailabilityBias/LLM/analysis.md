# AvailabilityBias LLM — Analysis Documentation

## §1 Overview

| Item                                | Description                                                                                                                                    |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                         |
| **Analysis Script**                 | `Rule/analysis.py` (imported — LLM variant uses Rule analysis functions)                                                                       |
| **Output Location**                 | `EXPERIMENT/AvailabilityBias/LLM/records/analysis/`                                                                                            |
| **Variant-Specific Considerations** | Behavioral/stochastic variant; highest bias amplitude and variance; measures whether LLM personas reproduce availability distortions naturally |

---

## §2 Metric Implementation

LLM variant shares all metric functions with `Rule/analysis.py`.

| Metric                       | Function              | analysis-bases.md Ref | LLM-Specific Notes                                                                             |
|------------------------------|-----------------------|-----------------------|------------------------------------------------------------------------------------------------|
| **Bias Amplitude**           | `calculate_metrics()` | `§2.1`                | Expected higher than Rule (5–15%); persona panic amplifies overreaction                        |
| **Correction Ratio**         | `calculate_metrics()` | `§2.2`                | Variable; LLM agents may resist correction through narrative rationalization                   |
| **Bias Persistence**         | `calculate_metrics()` | `§2.3`                | Longer than Rule; "denial" in LLMRecentEventOverweighter may extend bias duration              |
| **Return Autocorrelation**   | `calculate_metrics()` | `§2.4`                | Higher positive AC during bias phase; behavioral momentum creates stronger return continuation |
| **Agent-Type Volume**        | `calculate_metrics()` | `§2.5`                | LLM volumes stochastic; RecencyOverweighter may trade larger than formula-derived quantity     |
| **Availability Event Onset** | `calculate_metrics()` | `§2.6`                | Variable (5–25 rounds from event); persona sensitivity determines reaction timing              |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Bias Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → price/fundamental from `records/market/*.json`
- Output: `availabilitybias_llm_analysis.png` (4-panel: Price, Deviation, Returns, Agent Volume)

**Variant-Specific Interpretation:**
LLM bias amplitude should exceed Rule's 3–10% range. If bias < 3%, check RecencyOverweighter reasoning — is it citing return_pct or just deviation? If bias > 15%, persona panic amplification is dominant. Inspect `reasoning` field for mentions of "recent dramatic move" or "media narrative."

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Computation: per-agent volume from order records; `reasoning` field logs LLM decision rationale
- Output: volume breakdown by agent type

**Variant-Specific Interpretation:**
Check LLMSystematicAnalyst reasoning — does it say "I ignore recent noise" (correct persona) or "given the recent dramatic move" (availability contamination)? Contaminated SystematicAnalyst is a key failure mode — it would reduce the correction force.

---

### Dimension 3: Correction Dynamics
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: correction_ratio over time
- LLM-specific: correction may be non-monotonic (reverse corrections possible from behavioral stochasticity)

**Variant-Specific Interpretation:**
LLM correction curve may show plateaus (narrative persistence) or reversals (new media framing). Contrast with Rule's smooth monotonic correction. High variance in correction_ratio across runs is the expected LLM fingerprint.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

LLM is the high-bias behavioral reference. RuleLLM and Rag should show lower bias amplitude. Key question: do LLM availability personas naturally replicate the two-channel bias (recency + media) or do they collapse to a single undifferentiated signal?

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                          | Description                                                                      | How to Observe                                              | Contrast with Rule                                |
|-------------------------------------|----------------------------------------------------------------------------------|-------------------------------------------------------------|---------------------------------------------------|
| **Return_pct Over-Reliance**        | RecencyOverweighter cites return_pct more than deviation in reasoning            | Search reasoning fields for "recent return" vs. "deviation" | Rule: algebraic formula — no visible reasoning    |
| **Media Narrative Persistence**     | MediaInfluencedTrader continues selling/buying after deviation begins correcting | MediaInfluencedTrader volume during correction phase        | Rule: formula trigger disappears at threshold     |
| **SystematicAnalyst Contamination** | LLMSystematicAnalyst references return_pct in reasoning (should ignore it)       | Grep reasoning for "return" or "recent move"                | Rule: SystematicAnalyst always ignores return_pct |
| **Variable Bias Amplitude**         | Each run shows different peak deviation from same parameter settings             | Run 5 seeds, compare peak deviation IQR                     | Rule: identical peak per seed                     |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                             |
|----------------|---------------------------------------------------------------------------------|
| **50 rounds**  | Bias event + peak; correction may be incomplete; persona variation most visible |
| **100 rounds** | Full correction if LLMSystematicAnalyst uncorrupted; high variance runs visible |

### Parameter Sensitivity

| Parameter     | Change         | Expected Effect                                                           |
|---------------|----------------|---------------------------------------------------------------------------|
| `temperature` | 0.7 → 1.0      | More persona variance; higher bias amplitude range; more denial episodes  |
| Seeds         | 1 run → 5 runs | Full behavioral variance characterization                                 |
| `lm_name`     | pro → lite     | Weaker persona fidelity; availability bias may not manifest authentically |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/AvailabilityBias/LLM/records/analysis/`.

| Output File                         | Generated By              | Contents                                         | Interpretation                 |
|-------------------------------------|---------------------------|--------------------------------------------------|--------------------------------|
| `availabilitybias_llm_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Agent Volume | Primary LLM bias verification  |
| `metrics.json`                      | `main()`                  | `{"variant": "LLM", metrics}`                    | Cross-variant comparison input |

---

## §7 Cross-Variant Comparison Notes

- **Bias amplitude**: Highest; LLM persona amplification produces deeper overreaction than formula
- **Correction ratio**: Lowest; behavioral denial slows or prevents full correction
- **Behavioral realism**: Highest; availability bias emerges from persona without formula anchoring
- **Reproducibility**: Lowest; each seed produces different bias dynamics

Cross-variant comparison protocol: `../analysis-bases.md §5`.

References: `../analysis-bases.md`, `../simulation-bases.md §4.1`,
`../simulation-bases.md §4.2`, `../analysis-bases.md §6`, and
`Rule/analysis.py`.
