# SunkCostFallacy Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RAG-augmented LLM reasoning with canonical trading JSON |
| Key Difference from Other Variants | Each investor retrieves behavioral-finance context before deciding. |
| Primary Research Contribution | Tests whether evidence about sunk costs and escalation changes LLM trading behavior. |
| Files | `players.py`, `prompts.py`, `run_sunkcostfallacy_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Agent | Root Section | Implementation |
|---|---|---|
| `RagLLMSunkCostHolder` | `simulation-bases.md §4.1` | Retrieval can reinforce or challenge sunk-cost holding evidence. |
| `RagLLMCommitmentEscalator` | `simulation-bases.md §4.2` | Retrieval can contextualize averaging-down and escalation base rates. |
| `RagLLMRationalCutter` | `simulation-bases.md §4.3` | Retrieval can support forward-looking loss-cutting. |
| `RagLLMOpportunityCostTrader` | `simulation-bases.md §4.4` | Retrieval can support opportunity-cost reallocation. |
| `RagLLMNoiseTrader` | `simulation-bases.md §4.5` | Retrieval is available but not systematically used. |

## §3 Market Mechanism Implementation

The Rag variant reuses the Rule market. RAG only changes the information set
used by investor prompts before the LLM decision call.

## §4 Rag Variant-Specific Features

Each agent initializes a `KnowledgeStore` from `private_knowledge.rag`. Retrieval
queries include the current deviation, price, and fundamental value. When no
context is retrieved, the explicit fallback string
`(No relevant knowledge retrieved this round.)` is injected and recorded as
`rag_context`.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
RagLLMInvestor._build_prompt()
        |
        v
KnowledgeStore.query(sunk cost + current market state)
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
| `knowledge.global_resources` | top-level `knowledge` | Source document and index roots. |
| `llm.lm_name` | `*.extras.llm.lm_name` | ARK model for final decision. |

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/Rag/run_sunkcostfallacy_rag.py \
  -c configs/SunkCostFallacy/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

RAG should preserve the canonical trading schema while adding auditable context
about sunk-cost fallacy, escalation, opportunity cost, and rational loss
cutting.

## §9 References

RAG content is motivated by `../simulation-bases.md §1.1.2` and
`../simulation-bases.md §8`. Metrics and `rag_stats.json` trace to
`../analysis-bases.md §2` and `../analysis-bases.md §6`.
