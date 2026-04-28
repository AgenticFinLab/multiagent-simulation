# CurrencyCrisis Rag Variant — explain.md

## §1 Overview

The Rag variant augments each LLM agent with a retrieval-augmented knowledge store. Agents receive persona prompts plus retrieved historical currency crisis case summaries and academic knowledge. This tests whether RAG-informed agents exhibit more historically grounded crisis behavior than pure LLM persona agents.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | Rag                                          |
| Simulation         | CurrencyCrisis                               |
| Decision Mechanism | LLM persona + RAG knowledge retrieval        |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |
| Prompt Location    | `CurrencyCrisis/Rag/prompts.py`              |
| Knowledge Store    | `CurrencyCrisis/Rag/knowledge/`              |

## §2 Theory → Implementation Mapping

### §2.1 RagSpeculativeAttacker (simulation-bases.md §4.1)

| Theory Component                         | Rag Implementation                                                      |
|------------------------------------------|-------------------------------------------------------------------------|
| Reserve depletion attack (Krugman, 1979) | Persona + RAG: retrieves ERM 1992, Baht 1997 case attack patterns       |
| Reserve threshold signal                 | RAG retrieves "typical reserve exhaustion timing" from historical cases |
| Short-cover on recovery                  | RAG may provide historical precedents for cover timing                  |

### §2.2 RagSelfFulfillingTrader (simulation-bases.md §4.2)

| Theory Component                          | Rag Implementation                                        |
|-------------------------------------------|-----------------------------------------------------------|
| Expectation coordination (Obstfeld, 1996) | RAG retrieves coordination failure case studies           |
| Momentum signal                           | Historical momentum data from retrieved crisis narratives |
| Self-fulfilling dynamics                  | RAG provides multiple-equilibria crisis case summaries    |

### §2.3 RagCentralBankDefender (simulation-bases.md §4.3)

| Theory Component     | Rag Implementation                                                         |
|----------------------|----------------------------------------------------------------------------|
| Reserve intervention | RAG retrieves successful and failed peg defense cases (HKD 1998, GBP 1992) |
| Two-tier defense     | Historical defense escalation patterns inform threshold reasoning          |
| Reserve constraint   | RAG may surface cases where reserve exhaustion led to collapse             |

### §2.4 RagFundamentalHedger (simulation-bases.md §4.4)

| Theory Component                             | Rag Implementation                                                     |
|----------------------------------------------|------------------------------------------------------------------------|
| Global games anchoring (Morris & Shin, 1998) | RAG retrieves PPP and equilibrium exchange rate studies                |
| 8% threshold reasoning                       | Historical cases of fundamental-anchored FX recovery inform buy timing |
| Counter-speculation                          | RAG case studies on fundamental-driven currency stabilization          |

### §2.5 RagNoiseTrader (simulation-bases.md §4.5)

| Theory Component                        | Rag Implementation                                                   |
|-----------------------------------------|----------------------------------------------------------------------|
| Random uninformed trading (Black, 1986) | Persona + RAG (minimal retrieval; noise trader ignores fundamentals) |

## §3 Prompt Variables

| Variable              | Source                   | Example Value                  |
|-----------------------|--------------------------|--------------------------------|
| `{price}`             | Market broadcast         | `0.92`                         |
| `{fundamental}`       | Market broadcast         | `1.00`                         |
| `{deviation}`         | Market broadcast         | `-0.08`                        |
| `{round}`             | Market broadcast         | `22`                           |
| `{cash}`              | Agent state              | `60000.0`                      |
| `{position}`          | Agent state              | `2000`                         |
| `{retrieved_context}` | `KnowledgeStore.query()` | Historical crisis case summary |
| `{history}`           | `HistoryBuffer`          | Last 5 rounds summary          |

## §4 Variant-Specific Features

- **Historical grounding**: RAG context may moderate speculative attacks (attacker "knows" failed attacks from history) or amplify them (attacker retrieves successful attacks).
- **Defense informed by precedent**: RagCentralBankDefender may reference successful HKD or failed UK defense to calibrate response.
- **SFAF moderation**: RAG awareness of coordination failure cases may reduce SFAF relative to pure LLM.
- **FAS improvement**: RAG fundamental knowledge (PPP studies) expected to improve FundamentalHedger precision.
- **Knowledge store**: `KnowledgeStore` (`masim.player.knowledge`) retrieves top-K chunks from pre-embedded currency crisis knowledge base.

## §5 Architecture

```
Market.decide() → broadcast market_data
RagInvestor.perceive() → store market_data
RagInvestor.decide() → KnowledgeStore.query(market_context) → retrieved_chunks
                     → LangChainAPIInference.infer(persona + retrieved_context, user_prompt)
                     → parse_llm_response_with_thinking() → {action, quantity}
RagInvestor.act() → update cash/position, submit order
```

## §6 Config Reference

Same `config.yaml` as Rule variant; additional Rag extras: `model_name`, `temperature`, `max_tokens`, `knowledge_store_path`, `top_k`.

## §7 Running Instructions

```bash
python -m examples.CurrencyCrisis.Rag.run
```

## §8 Expected Behavior

- AII may be lower than LLM variant (RAG moderates attack via historical failure cases)
- SFAF may be reduced (RAG coordination failure cases discourage blindly following others)
- FAS likely highest of all variants (RAG PPP knowledge reinforces fundamental-anchored hedging)
- DER may exhibit historically-informed defense patterns (gradual vs. sudden exhaustion)

## §9 References

See `simulation-bases.md §2` for full DOI citations.
