# EchoChamber Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both EchoChamber social-dynamics quality and retrieval
coverage for model decisions.

## §2 Core Metrics

| Metric | Implementation Trace | Source |
|---|---|---|
| Polarization amplification | `analysis.py:compute_polarization_amplification` | `analysis-bases.md §2.1` |
| Polarization persistence | `analysis.py:compute_polarization_persistence` | `analysis-bases.md §2.2` |
| Cluster separation | `analysis.py:compute_cluster_separation` | `analysis-bases.md §2.3` |
| Polarize activity | `analysis.py:compute_polarize_activity` | `analysis-bases.md §2.4` |
| Depolarize activity | `analysis.py:compute_depolarize_activity` | `analysis-bases.md §2.5` |
| Opinion dispersion | `analysis.py:compute_opinion_dispersion` | `analysis-bases.md §2.6` |
| Retrieval/API quality | `analysis.py:compute_api_quality` and `analyze_rag_knowledge_effect` | `analysis-bases.md §2.7` |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §3 Analysis Dimensions

Analyze polarization path, action validity, role-specific activity, retrieval
success rate, and explanation quality.

## §4 Phase Analysis

Compare retrieval coverage across initialization, reinforcement, cluster
formation, depolarizing response, and terminal phases.

## §5 Cross-Variant Comparison

Rag is compared against RuleLLM to isolate the effect of retrieved context.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid special-schema
actions, and write `rag_context` plus `rag_stats.json`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, `03_summary.png`,
and `rag_stats.json`.

---

## §4 Variant-Specific Observable Phenomena

Rag agents retrieve social-science passages from `KnowledgeStore.query()` each
round and splice them into the `{rag_context}` prompt slot. When retrieval
returns no documents the sentinel

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

is injected instead, and `analyze_rag_knowledge_effect()` classifies that
round as a retrieval failure. Analysis must therefore distinguish
context-informed rounds from fallback rounds before interpreting behavior.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Retrieval-informed action modulation | `rag_stats.json` shows `retrieval_success_rounds` dominating `retrieval_failure_rounds`; polarization curve deviates from Rule where retrieval succeeded | Rule has no retrieval; deviations here isolate the RAG effect |
| Fallback-triggered LLM regression | Rounds where `rag_context == _RAG_FALLBACK` should show behavior close to RuleLLM, not Rag | Signals a knowledge-base gap when fallback fraction is high |
| Reduced variance vs. plain LLM | `summary.json → metrics.polarization.amplification_ratio` sits within a narrower band than pure LLM | Retrieval anchors reasoning; LLM without RAG is noisier |
| Cluster-formation smoothing | `01_echochamber_dynamics.png` (Panel 2) shows fewer spurious jumps in `cluster_separation` | Retrieved cluster-formation literature stabilizes trajectory |
| Retrieval coverage audit | `compute_api_quality(actions, rag_contexts)` reports `retrieval_coverage`; `rag_stats.aggregate.mean_retrieval_failure_rate` should stay ≤ 0.30 | Rule reports coverage = 0.0; LLM/RuleLLM lack this field |

Rag is expected to sit between RuleLLM (rule-only reasoning) and LLM
(persona-only reasoning) with retrieval-driven variance compression when
`retrieval_success_rate ≥ 0.70` per agent.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | Retrieval coverage measurable; polarization arc partially resolved | Low — few retrieval hits per agent | Quick smoke test |
| 200 | Full arc; per-agent retrieval statistics stable | Medium | Standard runs |
| 500 | Precise `retrieval_failure_rate` per agent; smooth comparison against RuleLLM | High | Retrieval-quality studies |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~10) | Retrieval workload light; some agents may see zero fallbacks | Small sample — retrieval variance dominates |
| Recommended (30–50) | Stable `mean_retrieval_failure_rate`; readable per-agent Panel 4 | Balanced retrieval load |
| Large (100+) | Retrieval throughput becomes the bottleneck; RAG cost dominates | Cost-limited regime |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Retrieval top-k | +50% | Lower `retrieval_failure_rate`; longer prompts; may amplify RAG smoothing effect |
| Retrieval top-k | −50% | Higher fallback rate; Rag behavior regresses toward RuleLLM |
| Knowledge base breadth (document count) | +50% | Fewer `_RAG_FALLBACK` hits; more stable cluster separation |
| Knowledge base breadth | −50% | Fallback rate rises; interpretation of polarization changes weakens |
| Query template specificity | +50% | Higher retrieval relevance; observable reduction in Panel 3 jitter |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EchoChamber/Rag/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` | Rounds, polarization, opinion, cluster, activity, dispersion, `rag_knowledge_effect`, validation | `metrics.rag_knowledge_effect.aggregate` summarizes retrieval health |
| `rag_stats.json` | `analyze_rag_knowledge_effect()` | Per-agent `total_rag_rounds`, `retrieval_success_rounds`, `retrieval_failure_rounds`, `retrieval_failure_rate`, plus aggregate | Audit before economic/behavioral interpretation; agents above 30% failure need review |
| `00_investor_bids.png` | `create_visualizations()` (imported from Rule) | 2×2 EchoChamber panel (agent-opinion / action panel alias) | Compare Panel 4 per-agent fans against Rule to identify retrieval-driven smoothing |
| `01_echochamber_dynamics.png` | `create_visualizations()` | Same 2×2 panel under dynamics alias | Panel 2 cluster-separation curve is the primary Rag signature |
| `02_echochamber_analysis.png` | `create_visualizations()` | Same 2×2 panel under analysis alias | Cross-referenced in cross-variant reports |
| `03_summary.png` | `create_visualizations()` | Same 2×2 panel under summary alias | Compact panel for top-level summaries |

Any agent whose `rag_stats[agent_id]` records `"note": "no rag_context field in records"` was not exercising retrieval — inspect `Rag/players.py` before treating that agent's results as RAG-informed.
