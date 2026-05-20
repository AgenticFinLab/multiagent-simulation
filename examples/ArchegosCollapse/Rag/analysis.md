# ArchegosCollapse Rag — Analysis Documentation

## §1 Analysis Objectives

| Item                                | Description                                                                                                                                         |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                              |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                     |
| **Output Location**                 | `EXPERIMENT/ArchegosCollapse/Rag/records/analysis/`                                                                                                 |
| **Variant-Specific Considerations** | RAG-augmented hybrid — key metric is RAG retrieval effect: do rounds with successful retrieval show different decision patterns vs fallback rounds? |

---

## §2 Metric → Function Mapping

All metrics are defined in `../analysis-bases.md §2`. Rag `analysis.py` imports core functions from `Rule/analysis.py` and adds `analyze_rag_knowledge_effect()`.

```python
from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    load_simulation_data,
)
```

| Metric                     | Function                         | analysis-bases.md Ref   | Rag-Specific Notes                                                                           |
|----------------------------|----------------------------------|-------------------------|----------------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()`            | `analysis-bases.md §2.1` | Near-RuleLLM baseline; knowledge may accelerate or modify cascade depth                      |
| **Maximum Drawdown**       | `calculate_metrics()`            | `analysis-bases.md §2.2` | Expected similar to RuleLLM; historical knowledge may deepen or buffer cascade               |
| **Cascade Volatility**     | `calculate_metrics()`            | `analysis-bases.md §2.3` | May show lower volatility if RAG provides stabilizing historical context                     |
| **Return Autocorrelation** | `calculate_metrics()`            | `analysis-bases.md §2.4` | Near-RuleLLM; RAG effect on autocorrelation depends on knowledge content                     |
| **Agent-Type Volume**      | `calculate_metrics()`            | `analysis-bases.md §2.5` | Similar to RuleLLM; RAG may increase BlockTradeBuyer conviction (historical recovery)        |
| **Cascade Onset Round**    | `calculate_metrics()`            | `analysis-bases.md §2.6` | Near-RuleLLM; historical urgency cues may slightly advance broker liquidation                |
| **Recovery Half-Life**     | `calculate_metrics()`            | `analysis-bases.md §2.7` | Historical context may affect how quickly agents support recovery after the trough           |
| **RAG Retrieval Effect**   | `analyze_rag_knowledge_effect()` | `§2` (variant-specific) | **Rag-only**: retrieval success vs fallback rate per agent; decision distribution comparison |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Cascade Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Functions: `load_simulation_data()` + `calculate_metrics()` (imported from Rule)
- Input data: `EXPERIMENT/ArchegosCollapse/Rag/records/market/price/`
- Output: `archegsoscollapse_rag_analysis.png` — 4-panel with RAG retrieval bar chart (Plot 4)

**Variant-Specific Interpretation:**
Rag cascade dynamics expected near-RuleLLM (same system prompts). Key question: does retrieved Archegos/LTCM knowledge cause agents to act more urgently (deeper cascade, earlier onset) or more cautiously (smaller quantities, delayed panic)?

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Function: `analyze_rag_knowledge_effect()` — classifies rounds by retrieval success vs fallback
- Fallback detection: `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
- Computation: compare decision distribution (action frequencies) in retrieval-success vs fallback rounds
- Output: Plot 4 = RAG retrieval success rate bar chart per agent; `rag_stats.json`

**Variant-Specific Interpretation:**
If retrieval success rate > 80% and decisions differ significantly between retrieved vs. fallback rounds, RAG knowledge is having a material impact. If decisions are identical regardless of retrieval, the knowledge content may need enrichment.

---

### Dimension 3: Cascade Intensity and Lifecycle
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: same as Rule/RuleLLM; `returns = np.diff(prices) / prices[:-1]`
- Output: subplot 3 (returns), subplot 4 replaced by RAG retrieval success bar chart

**Variant-Specific Interpretation:**
Monitor whether cascade phases align with RAG retrieval patterns. High retrieval rounds during cascade onset may indicate agents are accessing relevant historical precedents, potentially modifying cascade dynamics vs. RuleLLM baseline.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

**Rag's position in cross-variant comparison:**
- Cascade onset speed: Near-RuleLLM (same rules); knowledge may slightly shift timing
- Cascade depth: Variable by knowledge quality; deeper historical precedents may reinforce cascade
- Behavioral realism: Highest — agents reason with both formulas and historical case knowledge
- Decision quality: Potentially best if historical knowledge guides optimal timing

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                       | Description                                                                | How to Observe                                               | Contrast with RuleLLM Baseline              |
|----------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------|---------------------------------------------|
| **Knowledge-Reinforced Urgency** | Brokers cite historical Archegos/LTCM cases to justify faster liquidation  | Agent reasoning logs; `rag_stats.json` — high retrieval rate | RuleLLM: no historical context in reasoning |
| **Fallback = RuleLLM Behavior**  | In fallback rounds, agent behaves identically to RuleLLM                   | Compare fallback-round decisions vs RuleLLM baseline         | Direct behavioral equivalence when no RAG   |
| **Historical Anchoring Effect**  | BlockTradeBuyer buys more aggressively after retrieving recovery case data | BlockTradeBuyer volumes in high-retrieval rounds vs fallback | RuleLLM: fixed ±20% range                   |
| **Retrieval Failure Rate**       | Rounds where no relevant knowledge is retrieved (fallback rate)            | `rag_stats.json` — `retrieval_failure_rate` per agent        | N/A — Rag-only metric                       |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                                         |
|----------------|---------------------------------------------------------------------------------------------|
| **50 rounds**  | RAG effect partially observable; need more rounds for statistical comparison                |
| **100 rounds** | Adequate for retrieval success rate estimation; cascade lifecycle + RAG effect both visible |
| **200 rounds** | High confidence RAG effect measurement; enough rounds for retrieved vs. fallback comparison |

### Agent Count Scaling

| Agent Count            | Expected Observable                                                   |
|------------------------|-----------------------------------------------------------------------|
| **5 agents (default)** | Each agent's retrieval rate independently measurable                  |
| **10+ agents**         | More varied retrieval patterns; some agents retrieve more than others |

### Parameter Sensitivity

| Parameter        | Change               | Expected Effect on Rag Analysis                                 |
|------------------|----------------------|-----------------------------------------------------------------|
| `rag.top_k`      | 3 → 5                | More context; potentially richer reasoning; longer prompts      |
| `rag.top_k`      | 3 → 1                | Less context; less influence on decisions; closer to RuleLLM    |
| Knowledge corpus | Add LTCM 1998 data   | Richer historical analogy; may increase broker urgency          |
| Knowledge corpus | Remove Archegos data | Fewer relevant matches; higher fallback rate; closer to RuleLLM |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/ArchegosCollapse/Rag/records/analysis/`.

| Output File                          | Generated By                     | Contents                                                | Interpretation                                       |
|--------------------------------------|----------------------------------|---------------------------------------------------------|------------------------------------------------------|
| `archegsoscollapse_rag_analysis.png` | `main()`                         | 4-panel: Price, Deviation, Returns, RAG Retrieval Bar   | Primary Rag cascade + knowledge effect visualization |
| `summary.json`                       | `main()`                         | `{"variant": "Rag", price_metrics, deviation_metrics}`  | Cross-variant comparison input                       |
| `rag_stats.json`                     | `analyze_rag_knowledge_effect()` | Per-agent retrieval_success_rate, fallback_rate, totals | RAG knowledge effectiveness measurement              |

---

## §7 Cross-Variant Comparison Notes

- **Phenomenon emergence speed**: Near-RuleLLM; historical urgency cues may slightly accelerate broker liquidation timing
- **Phenomenon intensity**: Variable — rich historical Archegos precedents may deepen cascade; recovery precedents may buffer it
- **Behavioral realism**: Highest of all four variants — agents combine rule structure, persona psychology, and historical knowledge
- **Decision quality**: Potentially best if RAG knowledge guides BlockTradeBuyer to optimal entry points and InformationTrader to better-timed exits

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

### References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §8` — Historical Case Studies (source of RAG knowledge base content)
- `../simulation-bases.md §9 (Rag column)` — expected variant behavior from knowledge retrieval
- `analysis.py → analyze_rag_knowledge_effect()` — RAG knowledge effect computation
- `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` — fallback detection constant
- `Rule/analysis.py` — imported metric functions
