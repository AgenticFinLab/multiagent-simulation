# BlackMonday1987 Rag — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                     |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                            |
| **Output Location**                 | `EXPERIMENT/BlackMonday1987/Rag/records/analysis/`                                                                                         |
| **Variant-Specific Considerations** | RAG-augmented variant — key metric is RAG retrieval effect; when no knowledge is retrieved (`_RAG_FALLBACK`), behavior degrades to RuleLLM |

---

## 1. Metric Implementation

Rag `analysis.py` imports core functions from `Rule/analysis.py` and adds `analyze_rag_knowledge_effect()`.

| Metric                     | Function                         | analysis-bases.md Ref   | Rag-Specific Notes                                                                 |
|----------------------------|----------------------------------|-------------------------|------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()`            | `§2.1`                  | Enriched by domain knowledge; deeper or shallower deviation than RuleLLM possible  |
| **Maximum Drawdown**       | `calculate_metrics()`            | `§2.2`                  | Knowledge of 1987 crash may reduce over-shooting vs. RuleLLM                       |
| **Crash Velocity**         | `calculate_metrics()`            | `§2.3`                  | Domain knowledge of feedback spirals may cause faster crisis recognition           |
| **Return Autocorrelation** | `calculate_metrics()`            | `§2.4`                  | Near-RuleLLM if retrieval rate is high; near-Rule if low retrieval rounds dominate |
| **Agent-Type Volume**      | `calculate_metrics()`            | `§2.5`                  | IMF Rescuer knowledge may cause earlier buying; compared against Rule baseline     |
| **Crash Onset Round**      | `calculate_metrics()`            | `§2.6`                  | Knowledge of 1987 trigger conditions may shift onset earlier                       |
| **RAG Retrieval Effect**   | `analyze_rag_knowledge_effect()` | `§2` (variant-specific) | **Rag-only**: retrieval success rate, knowledge quality assessment per agent       |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crash Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price/fundamental from `records/market/*.json`
- Output: `blackmonday1987_rag_analysis.png` (Panel 1: Price vs Fundamental)

**Variant-Specific Interpretation:**
When agents retrieve high-quality 1987 crash knowledge, crash patterns may be modified (earlier or deeper). When retrieval fails (`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`), behavior reverts to RuleLLM patterns — compare crash curve with `RuleLLM/records`.

---

### Dimension 2: Agent Behavior + RAG Retrieval Rate
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Function: `analyze_rag_knowledge_effect()` — parses `analysis` field in order records for RAG fallback string presence
- Output: Plot 4 = RAG retrieval success rate bar chart per agent; `rag_stats.json`

**Variant-Specific Interpretation:**
Agents with >50% retrieval success should show richer reasoning. PortfolioInsurer + ProgramTrader knowledge usage most critical (core amplification). IndexArbitrageur benefits from futures-spot arbitrage knowledge from `simulation-bases.md §8`.

---

### Dimension 3: Feedback Loop + Knowledge Influence
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: return distribution, autocorrelation — same as Rule
- RAG-specific: compare return distribution against RuleLLM (knowledge-informed crash vs. blind formula)

**Variant-Specific Interpretation:**
If retrieval succeeds for most rounds: expect autocorrelation and fat tail similar to Rule. If retrieval frequently fails: expect slightly wider variance than RuleLLM (random LLM divergence).

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

Rag compared against Rule (baseline) and RuleLLM (knowledge-free formula). Key hypothesis: RAG retrieval enriches crash dynamics beyond pure rule following. Check `summary.json` `max_drawdown` vs. RuleLLM.

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                     | Description                                                                  | How to Observe                                                 | Contrast with RuleLLM              |
|--------------------------------|------------------------------------------------------------------------------|----------------------------------------------------------------|------------------------------------|
| **Knowledge-Reinforced Crash** | Retrieved 1987 crash documents amplify ProgramTrader sell signals            | ProgramTrader sell volumes on high-retrieval rounds            | RuleLLM: formula only, no context  |
| **IMF Rescue Awareness**       | IMFRescuer retrieves international lender texts; may intervene earlier       | ValueInvestor/IMFRescuer buy rounds vs. Rule threshold         | RuleLLM: waits for exact threshold |
| **Fallback = RuleLLM**         | When `_RAG_FALLBACK` string detected, agent behavior is identical to RuleLLM | `rag_stats.json` fallback rate; overlay with RuleLLM decisions | RuleLLM: constant; Rag: variable   |
| **Retrieval Failure Rate**     | Fraction of rounds where no relevant chunk retrieved                         | `rag_stats.json` — per-agent `fallback_rate` field             | RuleLLM: no RAG concept            |

---

## 4. Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                      |
|----------------|--------------------------------------------------------------------------|
| **50 rounds**  | Full crash + knowledge effect visible; partial recovery                  |
| **100 rounds** | Complete lifecycle; RAG benefit most visible in recovery phase reasoning |

### Parameter Sensitivity

| Parameter           | Change        | Expected Effect                                                  |
|---------------------|---------------|------------------------------------------------------------------|
| `rag_top_k`         | 2 → 5         | Higher retrieval quality; decisions closer to historically-aware |
| `feedback_strength` | 0.3 → 0.5     | Deeper crash; tests whether RAG mitigates amplification          |
| `price_impact`      | 0.002 → 0.005 | Faster price moves; retrieval lag becomes more relevant          |

---

## 5. Output Files Reference

All outputs written to `EXPERIMENT/BlackMonday1987/Rag/records/analysis/`.

| Output File                        | Generated By                     | Contents                                               | Interpretation                                     |
|------------------------------------|----------------------------------|--------------------------------------------------------|----------------------------------------------------|
| `blackmonday1987_rag_analysis.png` | `create_visualizations()`        | 4-panel: Price, Deviation, Returns, RAG Retrieval Rate | Primary Rag crash + retrieval quality verification |
| `summary.json`                     | `main()`                         | `{"variant": "Rag", metrics}`                          | Cross-variant comparison input                     |
| `rag_stats.json`                   | `analyze_rag_knowledge_effect()` | Per-agent retrieval success rate, fallback rate        | RAG knowledge quality validation                   |

---

## 6. Cross-Variant Comparison Notes

- **Crash emergence speed**: Similar to RuleLLM; knowledge may shift onset slightly
- **Crash intensity**: Within ±20% of Rule; enriched knowledge possible modifier
- **Behavioral realism**: Highest across all variants (rules + persona + domain knowledge)
- **RAG-specific value**: Detectable only when high retrieval rate + meaningful knowledge source

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §8` — Historical Cases (knowledge base source for RAG)
- `../simulation-bases.md §4 Rag Augmentation Notes` — RAG behavior description
- `analysis.py → analyze_rag_knowledge_effect()` — retrieval quality computation
- `Rule/analysis.py` — imported metric functions
- `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` — fallback detection string
