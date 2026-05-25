# AvailabilityBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Simulation | AvailabilityBias |
| Decision Mechanism | RuleLLM prompt structure plus retrieved behavioral-finance context |
| Theory Reference | `simulation-bases.md §2` and investor designs in `simulation-bases.md §4` |
| Market Broadcast | `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMRecentEventOverweighter (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Recency salience overweighting | Uses the RuleLLM recency rules and queries RAG with current return/deviation. |
| Historical overreaction context | Retrieved passages may reinforce or moderate event-salience reasoning. |
| Auditable knowledge use | Order payload records `rag_context` for post-run analysis. |

### §2.2 RagLLMMediaInfluencedTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Media salience amplification | Uses the RuleLLM media formula and retrieved media/sentiment literature. |
| Social narrative grounding | Query text includes current deviation and return context. |
| Auditable knowledge use | `Rag/analysis.py` reports retrieval failure rate. |

### §2.3 RagLLMSystematicAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Objective evidence weighting | Uses RuleLLM systematic rules while retrieving debiasing or rational-processing context. |
| Stabilizing role | Retrieved research may strengthen correction rather than change the order schema. |
| Parser contract | Same canonical action JSON as LLM and RuleLLM. |

### §2.4 RagLLMValueTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental value discipline | Uses RuleLLM value rules with retrieved value/overreaction context. |
| Correction after salient events | RAG can surface historical reversal examples. |
| Auditable knowledge use | `rag_context` is persisted with the order. |

### §2.5 RagLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | Uses RuleLLM noise rules while retaining random weak motivation. |
| Knowledge has limited decision role | Retrieved context is available but should not create systematic strategy. |
| Auditability | Retrieval quality is still recorded for the variant-level RAG check. |

## §3 Market Mechanism

The Rag variant reuses the Rule market implementation. RAG affects investor reasoning only; market clearing and broadcast schema are unchanged.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Knowledge Source | Shared `knowledge` block in `configs/AvailabilityBias/Rag/players.yml`. |
| Retrieval | `KnowledgeStore.query()` using price, return, and deviation context. |
| Prompt Injection | `{rag_context}` is inserted into `RAG_USER_TEMPLATE`. |
| Parser | Same `<analysis>` and `<decision>` contract as RuleLLM. |
| Failure Policy | Missing processed documents, invalid keys, or invalid decision output raises instead of silently substituting a hold. |

## §5 Config Reference

Primary config: `configs/AvailabilityBias/Rag/simulation.yml`.
Knowledge config uses `examples/document-sources`, `MinerU_processed`, `rag_index`, and `openai/hunyuan-embedding` through LiteLLM-compatible Hunyuan settings.

## §6 Running Instructions

```bash
python examples/AvailabilityBias/Rag/run_availabilitybias_rag.py \
  -c configs/AvailabilityBias/Rag/simulation.yml
```

## §7 Expected Behavior

- RAG should preserve the same trading action schema as RuleLLM.
- `rag_context` should be recorded in every RAG order payload.
- `Rag/analysis.py` should write `rag_stats.json` alongside the standard analysis outputs.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
