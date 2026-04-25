# ConfirmationBias Rag Variant — Analysis Guide

## 1. Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias Rag** variant.
Key questions:
1. *Does retrieved knowledge about confirmation bias reduce mispricing?*
2. *Do stabilizing agents benefit more from RAG than biased agents?*
3. *Is the KnowledgeStore adequately populated (retrieval ≥ 70%)?*

---

## 2. Metric Implementation (`Rag/analysis.py`)

Imports `calculate_metrics`, `load_simulation_data` from `Rule/analysis.py` (DRY pattern).
Adds `analyze_rag_knowledge_effect()` — the primary Rag-specific metric.

### `analyze_rag_knowledge_effect()` — Key Function

```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

def analyze_rag_knowledge_effect(agent_records):
    # For each agent record: check rag_context field
    # success if rag_context != _RAG_FALLBACK and not empty
    # retrieval_success_rate = success_rounds / total_rag_rounds
    # meets_target = rate >= 0.70
```

| Metric                   | Target     | Interpretation                           |
|--------------------------|------------|------------------------------------------|
| `retrieval_success_rate` | ≥ 0.70     | Fraction of rounds with useful knowledge |
| `meets_target`           | True/False | Whether KnowledgeStore is adequate       |
| `success_rounds`         | Count      | Rounds with retrieved context            |
| `failure_rounds`         | Count      | Rounds returning fallback                |

---

## 3. Rag-Specific Output Files

Running `Rag/analysis.py` writes to `EXPERIMENT/ConfirmationBias/Rag/records/analysis/`:

| File                                | Contents                                                    |
|-------------------------------------|-------------------------------------------------------------|
| `confirmationbias_rag_analysis.png` | 2×2 chart with RAG retrieval bar                            |
| `summary.json`                      | `{variant: "Rag", ...metrics, rag_knowledge_effect: {...}}` |
| `rag_knowledge_effect.json`         | Per-agent retrieval statistics                              |

---

## 4. Dimension-by-Dimension Interpretation

### 4.1 Price vs Fundamental

- Compare `bias_amplitude_pct` Rag vs LLM:
  - If Rag < LLM: retrieved knowledge moderating bias
  - If Rag ≈ LLM: knowledge not effective or `retrieval_success_rate` too low

### 4.2 Deviation Time Series

- If stabilizing agents (BalancedAnalyst, ContrarianTrader) retrieve relevant content:
  earlier activation → shorter bias_persistence_rounds
- If BeliefAnchor retrieves content about its own bias and ignores it:
  bias amplitude unchanged but deviation may oscillate more

### 4.3 RAG Retrieval Bar Chart

- **Green bars** (≥ 70%): KnowledgeStore has sufficient relevant documents
- **Red bars** (< 70%): Need more documents for this agent's topic
- Expected: BalancedAnalyst and ContrarianTrader should have high retrieval
  (rational trading documents easy to find); BeliefAnchor may have lower
  retrieval if KnowledgeStore lacks bias-specific documents

---

## 5. Variant-Specific Phenomena

### 5.1 Knowledge Quality vs Quantity

High retrieval rate ≠ high quality. Inspect `rag_knowledge_effect.json`
and also manually check a few retrieved contexts:
- Does retrieved text mention "confirmation bias" explicitly?
- Is retrieved text actionable for the agent's decision?

### 5.2 Bias Agent Response to Knowledge

Interesting research question: Can `BeliefAnchor` overcome its bias
when retrieved text explains the mechanism of confirmation bias?

Possible outcomes:
1. **Knowledge ignored**: BeliefAnchor continues buying despite retrieved warning
2. **Knowledge heeded**: BeliefAnchor reduces buying after retrieval
3. **Knowledge amplifying**: BeliefAnchor uses retrieved confirmation examples
   to justify even stronger belief

### 5.3 Fallback Behavior

When `retrieval_success_rate < 70%`, Rag ≈ LLM (no knowledge benefit).
In this case, focus improvements on KnowledgeStore content, not agent prompts.

---

## 6. Knowledge Store Requirements

For `retrieval_success_rate ≥ 70%`, add documents to `configs/ConfirmationBias/Rag/knowledge/`:

| Document Topic                            | Relevant For                   |
|-------------------------------------------|--------------------------------|
| Confirmation bias definition and examples | BeliefAnchor, SelectiveScanner |
| Biased assimilation in financial markets  | All biased agents              |
| Rational Bayesian updating                | BalancedAnalyst                |
| Contrarian investment strategies          | ContrarianTrader               |
| Market mispricing correction mechanisms   | All stabilizing agents         |
| Cognitive debiasing techniques            | All agents                     |

---

## 7. Cross-Variant Comparison

| Metric                    | Expected vs LLM                       |
|---------------------------|---------------------------------------|
| `bias_amplitude_pct`      | Lower if stabilizers benefit from RAG |
| `bias_persistence_rounds` | Shorter if RAG accelerates correction |
| `correction_ratio`        | Higher (more effective stabilization) |
| `retrieval_success_rate`  | Target ≥ 70%                          |

Use `rag_knowledge_effect.json` to rank agents by retrieval quality.
Agents with lowest retrieval are the highest priority for KnowledgeStore improvement.
