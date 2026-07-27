# ConfirmationBias Rag Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias Rag** variant.
Key questions:
1. *Does retrieved knowledge about confirmation bias reduce mispricing?*
2. *Do stabilizing agents benefit more from RAG than biased agents?*
3. *Is the KnowledgeStore adequately populated (retrieval ≥ 70%)?*

---

## §2 Metric Implementation (`Rag/analysis.py`)

Imports the shared metric and visualization functions from `Rule/analysis.py`
(DRY pattern). Adds `analyze_rag_knowledge_effect()` as the primary
Rag-specific metric, while base market metrics map to `analysis-bases.md §2.1`
through `analysis-bases.md §2.7`.

| Metric | Implementation | Reference |
|---|---|---|
| `bias_amplitude_pct` | `analyze_confirmation_bias()` | `analysis-bases.md §2.1` |
| `bias_persistence` | `analyze_confirmation_bias()` | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | Shared price-deviation calculations | `analysis-bases.md §2.3` |
| `belief_flip_count` | RAG reasoning/action proxy interpretation | `analysis-bases.md §2.4` |
| `correction_ratio` | `analyze_confirmation_bias()` | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1` | `analyze_confirmation_bias()` | `analysis-bases.md §2.6` |
| `annualized_vol_pct` | Shared return-volatility calculations | `analysis-bases.md §2.7` |

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

## §3 Rag-Specific Output Files

Running `Rag/analysis.py` writes to `EXPERIMENT/ConfirmationBias/Rag/records/analysis/`:

| File                               | Contents                                  |
|------------------------------------|-------------------------------------------|
| `summary.json`                     | Metrics, validation, and RAG stats        |
| `00_investor_bids.png`             | Market price and per-agent bid traces     |
| `01_confirmationbias_dynamics.png` | Price/fundamental and deviation dynamics  |
| `02_confirmationbias_analysis.png` | Volatility and cumulative bias diagnostics|
| `03_summary.png`                   | Agent VWAP and trading-volume summary     |
| `rag_stats.json`                   | Per-agent retrieval statistics            |

---

## §4 Variant-Specific Observable Phenomena

Under the Rag variant, agent decisions depend not only on the observed
deviation and persona, but also on the `rag_context` string retrieved before
each decision. When retrieval fails the shared fallback sentinel
`_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` is
substituted, and the agent proceeds as in the LLM variant for that round.

| Phenomenon                                | Trigger condition                                                    | Expected metric signature                                          |
|-------------------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------|
| Knowledge-informed stabilization          | `rag_context != _RAG_FALLBACK` for BalancedAnalyst/ContrarianTrader  | `correction_ratio` above LLM baseline; `bias_persistence` shorter  |
| Sparse-KB fallback regime                 | `retrieval_success_rate < 0.70` for biased agents                    | Rag metrics converge to LLM baseline; `meets_target` = false       |
| Retrieval-modulated belief revision       | BeliefAnchor receives debiasing text                                 | Reduced `bias_amplitude_pct`; occasional belief-flip event         |
| Amplifying-knowledge failure mode         | BeliefAnchor retrieves confirming rather than debiasing content      | `bias_amplitude_pct` at or above LLM; `belief_flip_count` low      |
| Context-dependent phenomenon variability  | Knowledge base composition changes                                   | Rag results shift while Rule/LLM/RuleLLM remain stable             |

### Retrieval Fallback Contract

Every agent record surfaces a `rag_context` field. If retrieval returns no
documents (empty index, no matches, or invalid embedding), the field is set
to `_RAG_FALLBACK`. `analyze_rag_knowledge_effect()` classifies such rounds
as `failure_rounds`; downstream analysis must **not** treat the sentinel
string as a real retrieved snippet.

### Dimension-Level Interpretation

- **Price vs Fundamental**: compare `bias_amplitude_pct` Rag vs LLM; if
  Rag < LLM the retrieval is genuinely moderating bias, otherwise
  `retrieval_success_rate` is likely below target.
- **Deviation Time Series**: stabilizer agents receiving relevant text
  activate earlier, shortening `bias_persistence_rounds`.
- **RAG Retrieval Bar Chart**: green bars (≥ 70%) mean the KnowledgeStore
  covers the agent's topic; red bars flag gaps to prioritize.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Round count | Expected metric behavior                                                                   |
|-------------|--------------------------------------------------------------------------------------------|
| 100         | Retrieval success rate stabilizes within first 30 rounds; correction ratio partially seen  |
| 200         | Bias amplitude vs LLM diverges clearly if KB is adequate                                   |
| 500         | Long-horizon regime: fallback rate stabilizes; steady-state `correction_ratio` observable  |

### Agent Count Scaling

| Configuration                                       | Expected effect on metrics                                                       |
|-----------------------------------------------------|----------------------------------------------------------------------------------|
| +50% stabilizer agents (BalancedAnalyst/Contrarian) | Retrieval load spreads; `correction_ratio` rises if KB covers rational trading   |
| +50% biased agents                                  | KB coverage per biased agent drops; `retrieval_success_rate` may fall below 0.70 |
| Uniform doubling                                    | Total retrieval calls double; latency budget matters more than metric shape      |

### Parameter Sensitivity (±50%)

| Parameter                        | Effect on Rag-specific metrics                                                    |
|----------------------------------|-----------------------------------------------------------------------------------|
| KnowledgeStore document count    | Higher → higher `retrieval_success_rate`; below threshold → fallback dominates    |
| Retrieval top-k                  | Higher → richer context but more noise; watch belief-flip stability               |
| Similarity threshold             | Lower → fewer fallbacks but noisier context; raise if amplifying-knowledge occurs |
| `confirmation_strength` (0.7)    | Same directional effect as Rule variant, moderated by retrieval quality           |
| Stabilizer `analysis_threshold`  | Lower → stabilizers act earlier; combined with RAG boosts `correction_ratio`      |

### Fallback Behaviour

When `retrieval_success_rate < 70%`, Rag ≈ LLM and no knowledge benefit is
observed; the recommended remediation is to enrich the KnowledgeStore rather
than tune agent prompts.

---

## §6 Knowledge Store Requirements

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

## §7 Cross-Variant Comparison

| Metric                    | Expected vs LLM                       |
|---------------------------|---------------------------------------|
| `bias_amplitude_pct`      | Lower if stabilizers benefit from RAG |
| `bias_persistence_rounds` | Shorter if RAG accelerates correction |
| `correction_ratio`        | Higher (more effective stabilization) |
| `retrieval_success_rate`  | Target ≥ 70%                          |

Use `rag_stats.json` to rank agents by retrieval quality.
Agents with lowest retrieval are the highest priority for KnowledgeStore improvement.
