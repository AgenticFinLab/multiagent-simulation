# AvailabilityBias Rag — Analysis Documentation

## §1 Overview

| Item                                | Description                                                                                                                                       |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                            |
| **Analysis Script**                 | `Rule/analysis.py` (imported)                                                                                                                     |
| **Output Location**                 | `EXPERIMENT/AvailabilityBias/Rag/records/analysis/`                                                                                               |
| **Variant-Specific Considerations** | Knowledge-augmented variant; key question is whether behavioral finance literature reduces or sharpens availability bias expression in LLM agents |

---

## §2 Metric Implementation

| Metric                       | Function              | analysis-bases.md Ref | Rag-Specific Notes                                                                                      |
|------------------------------|-----------------------|-----------------------|---------------------------------------------------------------------------------------------------------|
| **Bias Amplitude**           | `calculate_metrics()` | `§2.1`                | Unknown direction vs. LLM — knowledge may amplify (more articulate bias) or dampen (debiasing effect)   |
| **Correction Ratio**         | `calculate_metrics()` | `§2.2`                | Potentially higher if SystematicAnalyst uses debiasing literature to resist contamination               |
| **Bias Persistence**         | `calculate_metrics()` | `§2.3`                | May be shorter if knowledge-armed SystematicAnalyst counter-trades more effectively                     |
| **Return Autocorrelation**   | `calculate_metrics()` | `§2.4`                | Similar to LLM unless debiasing literature significantly alters return momentum dynamics                |
| **Agent-Type Volume**        | `calculate_metrics()` | `§2.5`                | Key diagnostic: does SystematicAnalyst volume increase vs. LLM (debiasing) or decrease (contamination)? |
| **Availability Event Onset** | `calculate_metrics()` | `§2.6`                | Variable; knowledge-grounded agents may detect availability events earlier or later                     |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Bias Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation:** `load_simulation_data()` → `availabilitybias_rag_analysis.png`

**Variant-Specific Interpretation:**
Compare Rag bias amplitude to LLM baseline. If Rag < LLM: knowledge is debiasing. If Rag > LLM: retrieved bias literature is reinforcing/amplifying expression. Either result is scientifically interesting — must be compared to expectations from `../analysis-bases.md §6`.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Key Diagnostic:** Does RagSystematicAnalyst reasoning cite debiasing research ("research shows availability bias causes overreaction in this pattern")? Does it use this knowledge to counter-trade more aggressively? Presence of debiasing citations = knowledge is working as intended.

---

### Dimension 3: Correction Dynamics
*(Objective from analysis-bases.md §3.3)*

**Variant-Specific Interpretation:**
If correction_ratio is higher in Rag vs. LLM, SystematicAnalyst's knowledge-grounded debiasing is effective. Check whether RagSystematicAnalyst trades earlier and in larger size than LLM counterpart.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rag is the "informed" behavioral reference. Research question: does knowledge about cognitive biases make agents more or less biased? This is the primary scientific contribution of the Rag variant.

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                            | Description                                                                        | How to Observe                                             |
|---------------------------------------|------------------------------------------------------------------------------------|------------------------------------------------------------|
| **Debiasing via Research Citation**   | SystematicAnalyst cites bias research to justify counter-trading                   | Search reasoning for "research shows", "studies indicate"  |
| **Bias Reinforcement via Literature** | RecencyOverweighter cites experimental evidence for availability heuristic         | Search reasoning for "Tversky", "Kahneman", "availability" |
| **RAG Empty Context Rounds**          | Some rounds return "(No relevant knowledge)" — agent defaults to LLM behavior      | Count empty RAG rounds in reasoning logs                   |
| **Knowledge Quality Effect**          | Outcome depends on document source quality (behavioral finance papers vs. generic) | Compare runs with different document sources               |

---

## §5 Scaling and Sensitivity Analysis

| Parameter               | Change      | Expected Effect                                                                |
|-------------------------|-------------|--------------------------------------------------------------------------------|
| `top_k`                 | 3 → 5       | More debiasing context; potentially lower bias amplitude                       |
| Document source quality | thin → rich | Richer behavioral finance literature → stronger debiasing or more precise bias |
| `temperature`           | 0.7 → 1.0   | More variance in how knowledge is interpreted and applied                      |

---

## §6 Output Files Reference

| Output File                         | Generated By              | Contents                                         | Interpretation                 |
|-------------------------------------|---------------------------|--------------------------------------------------|--------------------------------|
| `availabilitybias_rag_analysis.png` | `create_visualizations()` | 4-panel: Price, Deviation, Returns, Agent Volume | Primary Rag bias verification  |
| `metrics.json`                      | `main()`                  | `{"variant": "Rag", metrics}`                    | Cross-variant comparison input |

---

## §7 Cross-Variant Comparison Notes

- **Bias amplitude**: Unknown direction vs. LLM — depends on document quality and retrieval success
- **Correction**: Potentially best of all variants if debiasing literature is effective
- **Scientific value**: Primary contribution is testing meta-knowledge effect on behavioral bias expression
- **Document dependency**: Rag value contingent on behavioral finance paper availability

Cross-variant comparison protocol: `../analysis-bases.md §5`.

References: `../analysis-bases.md`, `../simulation-bases.md §4.1-§4.5`,
`../analysis-bases.md §6`, `Rule/analysis.py`, and
`players.py -> RagLLMInvestor._build_prompt()`.
