# FramingEffect Rag — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM-style prompts augmented with per-agent retrieved knowledge |
| Key Difference from Other Variants | Each investor builds or loads a local `KnowledgeStore` and injects retrieved context into the user prompt. |
| Primary Research Contribution | Tests whether external behavioral-finance knowledge changes framing susceptibility. |
| Files | `players.py`, `prompts.py`, `run_framingeffect_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory → Implementation Mapping

### RagLLMGainFrameFollower: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.1`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.1.2 | Class: `RagLLMGainFrameFollower`; docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism → sim-bases §4.1.4.2 | Imports RuleLLM persona/rule prompt and augments it with retrieved framing knowledge. |
| Mathematical model → sim-bases §4.1.4.3 | Decision JSON is parsed through the same trading schema as LLM/RuleLLM. |
| State variables → sim-bases §4.1.4.3 | `RagLLMInvestor` stores market, portfolio, LLM client, and RAG store state. |
| Parameters → sim-bases §6 | LLM, embedding, and portfolio values are supplied through `players.yml`. |
| Historical case → sim-bases §8 | Query text searches for framing-effect trading knowledge around current deviation. |

### RagLLMLossFrameReactor: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.2`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.2.2 | Class: `RagLLMLossFrameReactor`; docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism → sim-bases §4.2.4.2 | Retrieved loss-aversion and framing context is injected before the market state. |
| Mathematical model → sim-bases §4.2.4.3 | Parsed actions are bounded by cash, holdings, and max order size. |
| State variables → sim-bases §4.2.4.3 | Uses current price, fundamental, deviation, cash, position, and RAG state. |
| Parameters → sim-bases §6 | Embedding and model parameters are configured per agent. |
| Historical case → sim-bases §8 | Retrieval can surface historical loss-frame episodes that affect reasoning. |

### RagLLMFrameInvariantTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.3`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.3.2 | Class: `RagLLMFrameInvariantTrader`; docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism → sim-bases §4.3.4.2 | Retrieval should support frame-invariant valuation and correction. |
| Mathematical model → sim-bases §4.3.4.3 | Uses the same market state and parser contract as other RAG investors. |
| State variables → sim-bases §4.3.4.3 | Market and RAG state are kept in `custom_state`. |
| Parameters → sim-bases §6 | Config uses a lower temperature for more stable reasoning. |
| Historical case → sim-bases §8 | Retrieved evidence may strengthen rational correction behavior. |

### RagLLMArbitrageFramer: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.4`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.4.2 | Class: `RagLLMArbitrageFramer`; docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism → sim-bases §4.4.4.2 | Retrieved historical correction evidence informs framing-arbitrage decisions. |
| Mathematical model → sim-bases §4.4.4.3 | Prompt and parser use the canonical trading action schema. |
| State variables → sim-bases §4.4.4.3 | Reads price deviation and portfolio state before querying knowledge. |
| Parameters → sim-bases §6 | Config controls model, embedding, chunking, and top-k retrieval. |
| Historical case → sim-bases §8 | Knowledge query references current deviation and price/fundamental gap. |

### RagLLMNoiseTrader: Theory → Implementation Mapping

> Theory defined in `simulation-bases.md §4.5`.

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis → sim-bases §4.5.2 | Class: `RagLLMNoiseTrader`; docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism → sim-bases §4.5.4.2 | Prompt remains an uninformed liquidity-provider persona but receives retrieved context. |
| Mathematical model → sim-bases §4.5.4.3 | Valid decision JSON is capped by portfolio constraints. |
| State variables → sim-bases §4.5.4.3 | Same market and RAG state as other RAG investors. |
| Parameters → sim-bases §6 | Config uses higher LLM temperature for noisier behavior. |
| Historical case → sim-bases §8 | Retrieved context may partially inform the nominally noisy agent. |

## §3 Market Mechanism Implementation

Rag imports `Market` from the Rule implementation. Market clearing is therefore unchanged from Rule; only investor prompt construction changes through retrieval.

## §4 Rag Variant-Specific Features

- Each agent resolves private knowledge through `ResourceManager`.
- The RAG store loads local index files, copies shared index files, or builds from processed documents.
- `RAG_USER_TEMPLATE` injects `{rag_context}` before market state.
- If retrieval returns no text, the prompt receives `"(No relevant knowledge retrieved this round.)"`.
- The RAG config read in `players.py` accepts optional `extras["knowledge"]` because top-level knowledge can be resolved by the simulation setup.

## §5 Architecture Diagram

```text
Market broadcast -> RagLLMInvestor
        |
        v
KnowledgeQuery(price, fundamental, deviation, round)
        |
        v
KnowledgeStore.query(top_k) -> rag_context
        |
        v
RAG prompt -> LLM -> parser -> capped order -> Market
```

## §6 Configuration Reference

| Config File | Runtime Role |
|---|---|
| `configs/FramingEffect/Rag/simulation.yml` | Full-run and Ray settings |
| `configs/FramingEffect/Rag/players.yml` | LLM model, embedding config, knowledge resources, class paths |
| `configs/FramingEffect/Rag/topology.yml` | Market/investor star topology |
| `configs/FramingEffect/Rag/persona.yml` | Shared storage and proxy settings |

## §7 Expected Runtime Outputs

Accepted RAG runs should complete 200 rounds, produce valid order records, and expose retrievable RAG context observations for quality audit. Missing processed documents or bad embedding credentials should fail before a sample is accepted.

## §8 Validation Checklist

- RAG config resolves `embed_type=litellm` and `embed_model=openai/hunyuan-embedding`.
- `RAG_USER_TEMPLATE` contains `{rag_context}` and the canonical decision schema.
- Dry-run discovers `FramingEffect__Rag`.
- Previous failed RAG sample must not be inherited; RAG requires a new full 200-round run.

## §9 Cross-Variant Comparison Notes

RAG is compared primarily against RuleLLM to isolate the effect of retrieved domain knowledge. Differences from RuleLLM should be interpreted together with retrieval success rate and fallback rate.
