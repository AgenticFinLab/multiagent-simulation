# SouthSeaBubble Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | SouthSeaBubble |
| Decision Mechanism | Retrieved historical bubble context plus API quantity orders |
| Theory Reference | `examples/SouthSeaBubble/simulation-bases.md` |
| Market Broadcast | `configs/SouthSeaBubble/Rag/topology.yml` |

Rag preserves the current-market quantity schema and records `rag_context` for
retrieval-quality audit.

## §2 Theory -> Implementation Mapping

### §2.1 InsiderAdvantaged (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Insider advantage | `RagLLMInsiderAdvantaged` combines insider persona with retrieved bubble history. |
| Config link | Portfolio, LLM, and RAG configs from `configs/SouthSeaBubble/Rag/players.yml`. |
| Output contract | Quantity order plus `rag_context` and parser-quality fields. |

### §2.2 NarrativeBeliever (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Narrative demand | `RagLLMNarrativeBeliever` retrieves bubble narratives and mania context. |
| Config link | Narrative metadata and RAG config. |
| Output contract | Quantity order with retrieval context. |

### §2.3 SkepticalAnalyst (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Fundamental skepticism | `RagLLMSkepticalAnalyst` retrieves cash-flow and bubble-collapse context. |
| Config link | Cash-flow metadata and RAG config. |
| Output contract | Quantity order plus retrieval/fallback artifacts. |

### §2.4 Arbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Mispricing correction | `RagLLMArbitrageur` retrieves limits-to-arbitrage context. |
| Config link | Spread metadata and RAG config. |
| Output contract | Quantity order plus `rag_context`. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | `RagLLMNoiseTrader` uses retrieved context only superficially. |
| Config link | Noise metadata and RAG config. |
| Output contract | Quantity order and retrieval audit fields. |

## §3 Market Mechanism

The Rag variant reuses the Rule market. Retrieval affects reasoning only; market
clearing remains current-market quantity aggregation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SouthSeaBubble/Rag/players.py` |
| Prompt module | `examples/SouthSeaBubble/Rag/prompts.py` |
| Inference | Project ARK model policy plus Hunyuan/LiteLLM embedding policy |
| Retrieval | `KnowledgeStore` over configured document resources |
| Output parsing | Shared parser plus required-field validation |
| Error handling | Missing document/index failures fail; parse fallback is explicit |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SouthSeaBubble/Rag/simulation.yml` | 200-round simulation entry point |
| `configs/SouthSeaBubble/Rag/players.yml` | Class paths, portfolio, LLM, and RAG config |
| `configs/SouthSeaBubble/Rag/topology.yml` | Message routing |
| `configs/SouthSeaBubble/Rag/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SouthSeaBubble/Rag/run_southseabubble_rag.py -c configs/SouthSeaBubble/Rag/simulation.yml
```

## §7 Expected Behavior

Rag must record `rag_context`, preserve valid quantity orders, and write
`rag_stats.json` for retrieval-quality review.

## §8 References

See `examples/SouthSeaBubble/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare Rag with RuleLLM to isolate how retrieved bubble history affects
narrative demand, skepticism, and correction timing.
