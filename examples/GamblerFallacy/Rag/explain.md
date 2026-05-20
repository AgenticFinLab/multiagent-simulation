# GamblerFallacy Rag — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM-style prompts augmented with retrieved knowledge |
| Key Difference from Other Variants | Each investor queries a `KnowledgeStore` and injects `{rag_context}` into the user prompt. |
| Primary Research Contribution | Tests whether domain knowledge changes gambler's-fallacy, hot-hand, and arbitrage behavior. |
| Files | `players.py`, `prompts.py`, `run_gamblerfallacy_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### RagLLMStreakReversalTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `RagLLMStreakReversalTrader`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | Imports RuleLLM prompt and augments reversal reasoning with retrieved context. |
| Mathematical model → sim-bases §4.1.4.3 | Uses the same canonical trading decision schema as LLM and RuleLLM. |
| State variables → sim-bases §4.1.4.3 | Stores market, portfolio, LLM client, and RAG store state. |
| Parameters → sim-bases §6 | LLM, embedding, and portfolio values are config supplied. |
| Historical case → sim-bases §8 | Query text searches for gambler's-fallacy and streak-trading knowledge around current deviation. |

### RagLLMHotHandTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `RagLLMHotHandTrader`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | Retrieved context can reinforce or moderate continuation beliefs. |
| Mathematical model → sim-bases §4.2.4.3 | Parsed orders are capped by cash, holdings, and max order size. |
| State variables → sim-bases §4.2.4.3 | Uses market fields plus RAG state. |
| Parameters → sim-bases §6 | Embedding and model settings are in `players.yml`. |
| Historical case → sim-bases §8 | Retrieval can surface hot-hand studies and market episodes. |

### RagLLMIndependentAssessor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `RagLLMIndependentAssessor`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Retrieved evidence should support independence of sequential outcomes. |
| Mathematical model → sim-bases §4.3.4.3 | Uses canonical action JSON and portfolio caps. |
| State variables → sim-bases §4.3.4.3 | Reads price, fundamental, deviation, cash, position, and RAG state. |
| Parameters → sim-bases §6 | Config supplies lower-temperature model settings. |
| Historical case → sim-bases §8 | Retrieval can support rational correction. |

### RagLLMArbitrageur: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `RagLLMArbitrageur`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Retrieved knowledge informs exploitation of streak-driven mispricing. |
| Mathematical model → sim-bases §4.4.4.3 | Model output is parsed and capped before order emission. |
| State variables → sim-bases §4.4.4.3 | Uses current market, portfolio, and RAG fields. |
| Parameters → sim-bases §6 | Config controls LLM and embedding settings. |
| Historical case → sim-bases §8 | Retrieval can provide correction timing examples. |

### RagLLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `RagLLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt remains noisy but receives external context. |
| Mathematical model → sim-bases §4.5.4.3 | Valid decision JSON is bounded by portfolio limits. |
| State variables → sim-bases §4.5.4.3 | Same state fields as other RAG investors. |
| Parameters → sim-bases §6 | Higher temperature preserves noisy behavior. |
| Historical case → sim-bases §8 | Retrieved context may make the nominally noisy agent partially informed. |

## §3 Market Mechanism Implementation

Rag imports the Rule `Market`, preserving identical price formation and message topology. RAG changes only investor prompt construction and RAG state management.

## §4 Rag Variant-Specific Features

- Per-agent knowledge is resolved through `ResourceManager`.
- Indexes are loaded locally, copied from shared storage, or built from processed documents.
- `{rag_context}` is injected before market state.
- Empty retrieval uses `"(No relevant knowledge retrieved this round.)"`.
- Optional `extras["knowledge"]` is read through the project-allowed RAG config-resolution path.

## §5 Architecture Diagram

```text
Market broadcast -> RagLLMInvestor -> KnowledgeStore.query() -> RAG prompt -> LLM -> parser -> capped order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/GamblerFallacy/Rag/simulation.yml` | Full-run and Ray settings |
| `configs/GamblerFallacy/Rag/players.yml` | LLM model, embedding config, knowledge resources, class paths |
| `configs/GamblerFallacy/Rag/topology.yml` | Star topology |
| `configs/GamblerFallacy/Rag/persona.yml` | Shared proxy/storage settings |

## §7 Expected Runtime Outputs

Accepted RAG runs should complete 200 rounds, produce valid order records, and expose RAG context observations for retrieval-quality audit. The prior RAG row is pending and must be rerun.

## §8 Validation Checklist

- RAG embed config uses `litellm` and `openai/hunyuan-embedding`.
- Prompt contains `{rag_context}` and canonical decision JSON.
- Preflight validates class paths and config load.
- `GamblerFallacy__Rag` requires a new full sample after this repair.

## §9 Cross-Variant Comparison Notes

RAG is compared primarily against RuleLLM to isolate the effect of retrieved knowledge on streak-bias and hot-hand dynamics.
