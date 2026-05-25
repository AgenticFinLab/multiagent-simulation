# SorosPound Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | SorosPound |
| Decision Mechanism | Retrieved currency-crisis context plus API quantity orders |
| Theory Reference | `examples/SorosPound/simulation-bases.md` |
| Market Broadcast | `configs/SorosPound/Rag/topology.yml` |

Rag preserves the current-market quantity schema and adds retrieved knowledge to
the prompt. Investor payloads record `rag_context` so retrieval quality can be
audited.

## §2 Theory -> Implementation Mapping

### §2.1 MacroHedgeFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Speculative attack role | `RagLLMMacroHedgeFund` combines macro attacker rules with retrieved crisis context. |
| Config link | Portfolio, LLM, and RAG configs from `configs/SorosPound/Rag/players.yml`. |
| Output contract | Quantity order plus `rag_context` and parser-quality metadata. |

### §2.2 PegDefender (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Peg defense role | `RagLLMPegDefender` retrieves peg-defense and reserve-management context. |
| Config link | Defender metadata, LLM config, and RAG config. |
| Output contract | Quantity order and retrieval audit fields. |

### §2.3 ConvergenceTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Convergence belief role | `RagLLMConvergenceTrader` uses ERM/convergence context when available. |
| Config link | Convergence metadata and RAG config. |
| Output contract | Quantity order plus recorded retrieval context. |

### §2.4 OpportunisticTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Momentum/herding role | `RagLLMOpportunisticTrader` retrieves historical attack-escalation context. |
| Config link | Attack-join metadata and RAG config. |
| Output contract | Quantity order plus retrieval and fallback fields. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Noise liquidity role | `RagLLMNoiseTrader` may reference retrieved fragments only superficially. |
| Config link | Noise metadata and RAG config. |
| Output contract | Quantity order with RAG context recorded for audit. |

## §3 Market Mechanism

The Rag variant reuses the Rule market. Retrieved knowledge influences
investor reasoning only; market clearing remains current-market net-demand
aggregation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/SorosPound/Rag/players.py` |
| Prompt module | `examples/SorosPound/Rag/prompts.py` |
| Inference | Project ARK model policy plus Hunyuan/LiteLLM embedding policy |
| Retrieval | `KnowledgeStore` over configured document resources |
| Output parsing | Required-field validation after shared LLM parser |
| Error handling | Missing documents/index failures fail; parse fallback is explicit and auditable |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/SorosPound/Rag/simulation.yml` | 200-round simulation entry point |
| `configs/SorosPound/Rag/players.yml` | Class paths, portfolio, LLM, and RAG config |
| `configs/SorosPound/Rag/topology.yml` | Market update and investor order routing |
| `configs/SorosPound/Rag/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/SorosPound/Rag/run_sorospound_rag.py -c configs/SorosPound/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve valid quantity orders while recording retrieval context in
every investor decision after initialization. `rag_stats.json` must be reviewed
before accepting full samples.

## §8 References

See `examples/SorosPound/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Compare Rag with RuleLLM to isolate the effect of retrieved ERM and currency
crisis context on attack urgency, defense response, and fallback/retrieval
quality.
