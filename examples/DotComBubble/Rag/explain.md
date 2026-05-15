# DotComBubble Rag Variant — explain.md

## §1 Overview

The Rag variant augments each LLM investor with RAG retrieval of historical dot-com bubble cases and relevant finance research. Before each decision, a `KnowledgeStore` query retrieves documents about NASDAQ 1995–2001 dynamics, IPO lock-up expiry patterns, momentum crashes, and short-squeeze events. Retrieved context is injected into the LLM prompt, grounding persona reasoning in empirical historical evidence.

| Aspect             | Detail                                                                                                         |
|--------------------|----------------------------------------------------------------------------------------------------------------|
| Variant            | Rag                                                                                                            |
| Simulation         | DotComBubble                                                                                                   |
| Decision Mechanism | RAG-augmented LLM — historical knowledge retrieval + persona reasoning                                         |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                                                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                                                                   |
| Knowledge Sources  | NASDAQ bubble history, IPO flipping research, momentum/crash analysis, Abreu-Brunnermeier synchronisation risk |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                                                      |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt: narrative-driven buyer persona; RAG retrieves Shiller (2000) passages and NASDAQ run-up case studies |
| Historical anchoring                | Retrieved documents on late-1990s tech narrative moderate or reinforce buying decisions                             |
| Crash capitulation                  | RAG may retrieve 2000–2001 crash evidence and prompt earlier sell signals vs. Rule                                  |

### §2.2 RagLLMIPOFlipper (simulation-bases.md §4.2)

| Theory Component                           | Implementation                                                                                        |
|--------------------------------------------|-------------------------------------------------------------------------------------------------------|
| IPO underpricing (Ofek & Richardson, 2003) | System prompt: IPO flip persona; RAG retrieves historical IPO lock-up data and flip return statistics |
| Short-hold decision                        | Retrieved evidence on typical flip windows (3–6 days) calibrates sell timing in LLM reasoning         |

### §2.3 RagLLMMomentumFollower (simulation-bases.md §4.3)

| Theory Component                    | Implementation                                                                                                |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Momentum (Jegadeesh & Titman, 1993) | System prompt: trend-follower persona; RAG retrieves momentum factor research and historical momentum crashes |
| Crash risk awareness                | Retrieved momentum crash case studies may cause LLM to reduce position size at high deviation                 |

### §2.4 RagLLMSkepticalValueInvestor (simulation-bases.md §4.4)

| Theory Component               | Implementation                                                                                                 |
|--------------------------------|----------------------------------------------------------------------------------------------------------------|
| Value anchoring (Graham, 1949) | System prompt: fundamental-anchored persona; RAG retrieves Graham principles and post-bubble recovery analysis |
| Historical patience            | Retrieval of 2000–2003 recovery timeline provides concrete basis for LLM patience decisions                    |

### §2.5 RagLLMShortSeller (simulation-bases.md §4.5)

| Theory Component                                  | Implementation                                                                                                    |
|---------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Synchronisation risk (Abreu & Brunnermeier, 2003) | System prompt: short-seller persona; RAG retrieves limits-to-arbitrage literature and NASDAQ short-squeeze events |
| Squeeze timing                                    | Retrieved evidence on squeeze duration helps LLM calibrate cover decisions                                        |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.005 (weak mean-reversion)
```

RAG query: `f"dot-com bubble trading: price={price:.2f}, fundamental={fundamental:.2f}, deviation={deviation:+.2%}"`

## §4 RAG Architecture

| Component       | Detail                                                         |
|-----------------|----------------------------------------------------------------|
| Base class      | `RagLLMInvestor` (extends `GeneralPlayer`)                     |
| Knowledge store | `KnowledgeStore` with `embed_model = openai/hunyuan-embedding` |
| Retrieval       | `KnowledgeQuery(text=query, top_k=3, round_num=round)`         |
| Inference       | `LangChainAPIInference`                                        |
| Context         | `HistoryBuffer` (last 200 entries)                             |
| Output parsing  | `parse_llm_response_with_thinking()` → `{action, quantity}`    |
| Retry logic     | 3 attempts; fall back to hold on failure                       |

## §5 Config Reference

Config file: `DotComBubble/Rag/config.yaml`

Key extras: `llm.lm_name`, `llm.generation_config`, `initial_cash`, `initial_position`; `rag.docs_dir`, `rag.top_k`, `rag.embed_model`, `rag.shared_rag_index_dir`.

## §6 Running Instructions

```bash
python -m examples.DotComBubble.Rag.run_dotcombubble_rag
```

## §7 Expected Behavior

- RAG moderation effect: `RagLLMNewEconomyEvangelist` may exit earlier than Rule if crash case studies are retrieved; BAI slightly lower.
- `RagLLMShortSeller` shows improved SSR vs. LLM — retrieved synchronisation-risk literature reinforces persistence against squeeze.
- `RagLLMMomentumFollower` displays variable MAF — retrieved momentum crash evidence occasionally suppresses momentum buying.
- BD is typically shorter than pure LLM because historical crash evidence triggers earlier selling decisions.

## §8 References

See `simulation-bases.md §2` for full DOI citations. Historical case documents should reside in `rag.docs_dir`.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
