# GameStopShortSqueeze — Rag Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | Rag                          |
| Metrics   | SQI, PAR, SCD, IEP, ACC, WTI |
| Reference | `../analysis-bases.md`       |
| Baseline  | Rule variant                 |

---

## §2 Metric → Function Mapping

| Metric | Function                                                                  | analysis-bases.md ref |
|--------|---------------------------------------------------------------------------|-----------------------|
| SQI    | `squeeze_intensity_index(price_history, fundamental)`                     | §2.1                  |
| PAR    | `price_area_ratio(price_history, fundamental)`                            | §2.2                  |
| ACC    | `agent_coalition_contribution(trade_history, price_history, fundamental)` | §2.3                  |
| SCD    | `squeeze_collapse_duration(price_history, fundamental)`                   | §2.4                  |
| IEP    | `institutional_exhaustion_point(agent_states_history)`                    | §2.5                  |
| WTI    | `wealth_transfer_index(agent_states, final_price)`                        | §2.6                  |
| AQR    | `analyze_rag_knowledge_effect(rag_contexts)`                              | §2.7                  |

---

## §3 Rag-Specific Notes

### §3.1 RagLLMRetailCoordinated
- Retrieved GME squeeze cases reinforce buying conviction → SQI likely higher than Rule.
- Excess enthusiasm: if retrieval corpus is GME-focused, PAR may reach upper range (> 1.0).

### §3.2 RagLLMShortSellerHF
- Retrieved squeeze postmortems (Melvin Capital, VW 2008) amplify covering urgency.
- SCD may shorten (faster panic covering) vs. Rule baseline (3–8 rounds → 1–6 rounds).

### §3.3 RagLLMMarketMakerGamma
- Retrieved options flow data anchors gamma hedge behavior; less drift than pure LLM variant.

### §3.4 RagLLMInstitutionalValue
- Retrieved analyst reports reinforce fundamental anchoring → IEP may be earlier (rounds 2–8).

### §3.5 RagLLMMomentumRetail
- Retrieved social media buzz metrics amplify FOMO buying; WTI rises with greater retail participation.

---

## §4 Expected Ranges (Rag vs. Rule Baseline)

| Metric | Rag Expected Range | vs. Rule | Basis                                             |
|--------|--------------------|----------|---------------------------------------------------|
| SQI    | 1.5–7.0            | Higher   | Retrieved squeeze cases reinforce §4.1 buying     |
| PAR    | 0.3–1.5            | Higher   | Larger and longer squeeze amplitude               |
| SCD    | 1–6 rounds         | Shorter  | Faster covering driven by retrieved fear evidence |
| IEP    | Rounds 2–8         | Earlier  | Fundamental reports prompt earlier §4.4 exit      |
| ACC    | 0.45–0.70          | Similar  | RAG improves contextual accuracy                  |
| WTI    | 0.15–0.50          | Higher   | Greater wealth transfer in amplified squeeze      |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; RAG investor roles
trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare RAG against RuleLLM to isolate the marginal effect of retrieved squeeze
context, against LLM to separate persona-only behavior from knowledge-augmented
behavior, and against Rule to assess whether retrieval amplifies or dampens the
baseline mechanism.

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Confirm RAG assets and embedding configuration were available.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Audit parse failures, retry counts, and retrieval-health records; deterministic parser/provider failures fail fast.
- Confirm `rag_stats.json` was written with per-agent and aggregate retrieval-health statistics.
