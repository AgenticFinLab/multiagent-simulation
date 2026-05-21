# StatusQuoBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RAG-augmented LLM reasoning with canonical trading JSON |
| Key Difference from Other Variants | Each investor retrieves behavioral-finance context before deciding. |
| Primary Research Contribution | Tests whether domain evidence changes inertia, default adherence, and explanation quality. |
| Files | `players.py`, `prompts.py`, `run_statusquobias_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### RagLLMInertialHolder

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.1`; class docstring cites `simulation-bases.md §4.1`. |
| Persona | `RAGLLM_INERTIAL_HOLDER_SYS` describes reluctance to change current holdings. |
| Retrieval | Query includes status quo bias, inertia, price, fundamental, and deviation. |
| Output contract | `_validate_decision()` enforces canonical order JSON and records `rag_context`. |

### RagLLMDefaultFollower

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.2`; class docstring cites `simulation-bases.md §4.2`. |
| Persona | `RAGLLM_DEFAULT_FOLLOWER_SYS` describes default-seeking allocation behavior. |
| Retrieval | Context may include default enrollment and allocation-inertia evidence. |
| Output contract | Same canonical schema and `rag_context` recording. |

### RagLLMActiveRebalancer

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.3`; class docstring cites `simulation-bases.md §4.3`. |
| Persona | `RAGLLM_ACTIVE_REBALANCER_SYS` describes active valuation response. |
| Retrieval | Context can contrast rational rebalancing with behavioral inertia. |
| Output contract | Same canonical schema and `rag_context` recording. |

### RagLLMMomentumTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.4`; class docstring cites `simulation-bases.md §4.4`. |
| Persona | `RAGLLM_MOMENTUM_TRADER_SYS` describes trend-following behavior. |
| Retrieval | Context can connect momentum pressure to delayed adjustment. |
| Output contract | Same canonical schema and `rag_context` recording. |

### RagLLMNoiseTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.5`; class docstring cites `simulation-bases.md §4.5`. |
| Persona | `RAGLLM_NOISE_TRADER_SYS` describes low-information liquidity behavior. |
| Retrieval | Context is available but low-information behavior should remain modest. |
| Output contract | Same canonical schema and `rag_context` recording. |

## §3 Market Mechanism Implementation

The market is re-exported from `StatusQuoBias.Rule.players`, so price formation
and order aggregation remain identical to `simulation-bases.md §3.1`. RAG only
changes the investor information set before the LLM call.

## §4 Rag Variant-Specific Features

Each agent initializes a `KnowledgeStore` using the current
`private_knowledge.rag` configuration shape. When retrieval returns no context,
the prompt receives the explicit string
`(No relevant knowledge retrieved this round.)`; this is recorded as
`rag_context` and later summarized in `rag_stats.json`.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
RagLLMInvestor._build_prompt()
        |
        v
KnowledgeStore.query(status quo + current market state)
        |
        v
rag_context injected into prompt
        |
        v
LLM response -> parser -> _validate_decision() -> order + rag_context -> Market
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `private_knowledge.rag.embed_type` | `*.extras.private_knowledge.rag.embed_type` | Embedding provider type. |
| `private_knowledge.rag.embed_model` | `*.extras.private_knowledge.rag.embed_model` | Hunyuan embedding model through LiteLLM convention. |
| `private_knowledge.rag.top_k` | `*.extras.private_knowledge.rag.top_k` | Number of chunks retrieved per decision. |
| `knowledge.global_uri` | top-level `knowledge.global_uri` | Document source root. |
| `llm.lm_name` | `*.extras.llm.lm_name` | ARK model for final decision. |

## §7 Running Instructions

```bash
python examples/StatusQuoBias/Rag/run_statusquobias_rag.py \
  -c configs/StatusQuoBias/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

RAG should preserve canonical trading behavior while adding auditable domain
context. Retrieval fallback context is acceptable only as an explicit recorded
diagnostic, not as hidden error recovery.

## §9 References

RAG content is motivated by `../simulation-bases.md §1.1.2` and
`../simulation-bases.md §8`. Metrics and `rag_stats.json` trace to
`../analysis-bases.md §2.7` and `../analysis-bases.md §6`.
