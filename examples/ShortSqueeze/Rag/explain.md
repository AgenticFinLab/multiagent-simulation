# Short Squeeze Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | ShortSqueeze |
| Decision Mechanism | RuleLLM-style API orders augmented by retrieved squeeze context |
| Theory Reference | `examples/ShortSqueeze/simulation-bases.md` |
| Market Broadcast | `configs/ShortSqueeze/Rag/topology.yml` |

Rag keeps the RuleLLM liquidity-aware market and injects retrieved knowledge
into each decision prompt. It must record `rag_context` for retrieval-quality
analysis.

## §2 Theory -> Implementation Mapping

### §2.1 ShortSeller (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Forced covering | `RagLLMShortSeller` uses short-seller rules plus retrieved context. |
| RAG contract | Records `rag_context` and emits liquidity-aware canonical trading JSON. |

### §2.2 MomentumBuyer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Positive-feedback demand | `RagLLMMomentumBuyer` uses momentum rules plus retrieved context. |
| RAG contract | Retrieved context may affect timing and urgency but not schema. |

### §2.3 RetailTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Attention-driven bullish flow | `RagLLMRetailCoordinator` uses retail rules plus retrieved context. |
| RAG contract | Retrieval text is available for Level-2 quality audit. |

### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental resistance | `RagLLMValueInvestor` uses valuation rules plus retrieved context. |
| RAG contract | Structured JSON remains aligned with the RuleLLM parser. |

### §2.5 InstitutionalHolder (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Float scarcity | `RagLLMInstitutionalHolder` uses holding/profit-taking rules plus retrieved context. |
| RAG contract | `rag_stats.json` reports retrieval success and fallback context rate. |

## §3 Market Mechanism

`Market` in `examples/ShortSqueeze/Rag/players.py` consumes
`provides_liquidity` to calculate effective depth. Investors retrieve top-k
context, store the resolved `rag_context`, and submit canonical liquidity-aware
orders.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ShortSqueeze/Rag/players.py` |
| Prompt module | `examples/ShortSqueeze/Rag/prompts.py` |
| Retrieval | `masim.knowledge.*` local knowledge stack |
| Inference | ARK API model plus Hunyuan/LiteLLM embedding config |
| Error handling | Deterministic RAG/config/parser errors fail fast; retrieval fallback context is recorded |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ShortSqueeze/Rag/simulation.yml` | Full simulation entry point |
| `configs/ShortSqueeze/Rag/players.yml` | RAG settings, prompts, models |
| `configs/ShortSqueeze/Rag/topology.yml` | Message routing |
| `configs/ShortSqueeze/Rag/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/ShortSqueeze/Rag/run_short_squeeze_ragllm.py -c configs/ShortSqueeze/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM's squeeze mechanism while retrieved GameStop,
Volkswagen, or short-sale-constraint context may change decision urgency or
liquidity provision.

## §8 References

See `examples/ShortSqueeze/simulation-bases.md §2` and
`examples/ShortSqueeze/analysis-bases.md §2`.

## §9 Variant Comparison

Use Rag to test whether retrieved squeeze context changes amplification,
covering urgency, or value resistance relative to RuleLLM.
