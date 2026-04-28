# EchoChamber Rag Variant — analysis.md

## §1 Analysis Objectives

1. Assess whether RAG-retrieved academic literature moderates agent behavior relative to LLM and Rule baselines.
2. Evaluate whether RagLLMCriticalThinker produces stronger depolarization than LLMCriticalThinker.
3. Measure RAG effectiveness: does retrieved context change action type distribution or merely the reasoning text?
4. Compare Rag variant DE and PI to LLM and Rule variants to quantify literature-grounded moderation effect.

## §2 Metric → Function Mapping

| Metric                         | Function                                                        | analysis-bases.md ref |
|--------------------------------|-----------------------------------------------------------------|-----------------------|
| Polarization Index (PI)        | `polarization_index(polarization_history)`                      | §2.1                  |
| Cluster Separation (CS)        | `cluster_separation(opinion_list)`                              | §2.2                  |
| Mean Opinion Drift (MOD)       | `mean_opinion_drift(mean_opinion_history)`                      | §2.3                  |
| Cross-Cutting Exposure (CCE)   | `cross_cutting_exposure(opinion_list, center_threshold=0.3)`    | §2.4                  |
| Polarization Velocity (PV)     | `polarization_velocity(polarization_history)`                   | §2.5                  |
| Depolarizer Effectiveness (DE) | `depolarizer_effectiveness(depolarize_counts, polarize_counts)` | §2.6                  |
| Opinion Variance (OV)          | `opinion_variance(opinion_list)`                                | §2.7                  |

## §3 Variant-Specific Notes

- RAG retrieval quality depends entirely on the document corpus — if sources are biased, polarization dynamics may be skewed.
- RagLLMCriticalThinker is expected to show the largest improvement over LLMCriticalThinker; academic counter-polarization evidence may increase depolarization intensity.
- RagLLMIdeologue may exhibit moderate reduction in extremity compared to LLMIdeologue if retrieved literature highlights polarization harms.
- RAG context injection uses `{rag_context}` in `RAG_USER_TEMPLATE` — empty string when RAG retrieval fails, degrading to LLM-only behavior.
- Shared RAG index configurations (if used) result in all agents retrieving from the same corpus; per-agent indexes allow agent-type-specific document sources.

## §4 Expected Ranges

| Metric | Expected Range | Interpretation                                                              |
|--------|----------------|-----------------------------------------------------------------------------|
| PI     | 0.15 – 0.70    | Lower ceiling than LLM if literature moderates Ideologue/Conformist         |
| CS     | 0.3 – 1.7      | Moderate to lower than LLM; RAG depolarization research may reduce CS       |
| MOD    | 0.0 – 0.25     | Literature-grounded moderation may reduce directional drift                 |
| CCE    | 0.15 – 0.55    | Higher CCE than LLM if RAG literature emphasizes cross-cutting exposure     |
| PV     | 0.004 – 0.07   | Variable; depends on RAG corpus quality and retrieval relevance             |
| DE     | 0.25 – 0.60    | Higher DE than LLM if CriticalThinker/BridgeBuilder benefit from literature |
| OV     | 0.08 – 0.35    | Potentially lower upper bound than LLM due to RAG moderation                |

## §5 References

See `analysis-bases.md §2` for full metric derivations and simulation-bases.md §4 for agent parameter sources.
