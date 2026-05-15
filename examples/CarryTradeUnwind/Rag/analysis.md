# CarryTradeUnwind Rag Variant — Analysis Guide

## 1. Analysis Overview

This guide covers interpretation of results from the **CarryTradeUnwind Rag** variant.
Key question: *Does retrieved carry-trade knowledge improve agent crisis response
compared to the plain LLM baseline? Does the RAG pipeline retrieve relevant context?*

---

## 2. Metric Implementation (`Rag/analysis.py`)

Imports `calculate_metrics`, `load_simulation_data`, `create_visualizations` from
`Rule/analysis.py` (DRY pattern). Adds `analyze_rag_knowledge_effect()`.

All 7 core metrics from analysis-bases.md §2 apply identically.

### `analyze_rag_knowledge_effect()` — Key Function

```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

def analyze_rag_knowledge_effect(agent_records):
    # For each agent record: check rag_context field
    # success if rag_context != _RAG_FALLBACK
    # retrieval_success_rate = success_rounds / total_rounds
    # meets_target = rate >= 0.70
```

| Metric                   | Target       | Interpretation                                   |
|--------------------------|--------------|--------------------------------------------------|
| `retrieval_success_rate` | ≥ 0.70 (70%) | Fraction of rounds with non-fallback RAG context |
| `meets_target`           | True/False   | Whether knowledge base is adequately populated   |
| `success_rounds`         | Count        | Rounds where relevant knowledge was found        |
| `failure_rounds`         | Count        | Rounds returning fallback string                 |

---

## 3. Rag-Specific Output Files

Running `Rag/analysis.py` writes to `EXPERIMENT/CarryTradeUnwind/Rag/records/analysis/`:

| File                                 | Contents                                           |
|--------------------------------------|----------------------------------------------------|
| `carrytradeunwind_rag_analysis.png`  | 2×2 chart: price, deviation, returns, distribution |
| `carrytradeunwind_rag_retrieval.png` | Bar chart: retrieval success rate per agent        |
| `summary.json`                       | `{variant: "Rag", ...metrics}`                     |
| `rag_knowledge_effect.json`          | Per-agent retrieval statistics                     |

---

## 4. Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- Rag agents with high retrieval success (≥70%) should show more informed carry decisions
- Compare crisis_onset_round with LLM baseline: RAG knowledge may delay/prevent crisis

### 4.2 Deviation Time Series

- If Rag agents retrieve crisis-relevant knowledge early, expect:
  - Earlier stabilizing action (FundingCurrencyBuyer activates sooner)
  - Shallower negative deviation peak
- If retrieval_success_rate < 70%: Rag behaves like vanilla LLM

### 4.3 RAG Retrieval Rate Plot

- Green bars (≥70%): Agent has sufficient relevant knowledge in KnowledgeStore
- Red bars (<70%): KnowledgeStore needs more documents on this agent's topic

---

## 5. Variant-Specific Phenomena

### 5.1 Knowledge Quality Effect

Retrieval rate alone does not guarantee quality. Check:
- Does retrieved context mention "carry trade", "deviation", "leverage"?
- Do agents act differently after retrieval vs fallback rounds?

### 5.2 Fallback Behavior

When `rag_context == _RAG_FALLBACK`, the agent makes a pure LLM decision.
High fallback rate → Rag ≈ LLM variant. No significant difference expected.

### 5.3 Knowledge Store Requirements

For optimal retrieval (≥70%), the KnowledgeStore should contain documents covering:
- Carry trade mechanics and unwind scenarios
- Risk management under leverage
- Currency crisis historical examples (JPY/CHF appreciation events)

---

## 6. Cross-Variant Comparison

| Metric                   | Expected vs LLM                      |
|--------------------------|--------------------------------------|
| `max_drawdown_pct`       | Lower if RAG provides crisis context |
| `crisis_onset_round`     | Later or never if RAG prevents panic |
| `recovery_ratio`         | Higher (RAG-informed stabilizers)    |
| `retrieval_success_rate` | Target ≥ 70%                         |

Compare `rag_knowledge_effect.json` between agents to identify which agent benefits
most from carry-trade knowledge retrieval.

---

## 7. Knowledge Improvement Recommendations

If `retrieval_success_rate < 0.70` for any agent:

1. Add more carry-trade documents to `configs/CarryTradeUnwind/Rag/knowledge/`
2. Check KnowledgeQuery keywords match document terminology
3. Verify `KnowledgeStore` embedding model handles financial vocabulary
4. Consider reducing `top_k` threshold to return more diverse contexts
