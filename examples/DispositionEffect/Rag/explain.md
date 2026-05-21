# DispositionEffect Rag Variant — explain.md

## §1 Overview

The Rag variant augments each LLM agent with a retrieval-augmented knowledge store containing behavioral finance literature and historical disposition effect case studies. Agents receive persona prompts plus retrieved academic context, testing whether RAG-informed disposition behavior is more calibrated to empirical benchmarks.

| Aspect             | Detail                                                                        |
|--------------------|-------------------------------------------------------------------------------|
| Variant            | Rag                                                                           |
| Simulation         | DispositionEffect                                                             |
| Decision Mechanism | LLM persona + RAG behavioral finance knowledge retrieval                      |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                               |
| Market Broadcast   | `price`, `purchase_price`, `gain_loss`, `cash`, `position`, `portfolio_value` |
| Prompt Location    | `DispositionEffect/Rag/prompts.py`                                            |
| Knowledge Store    | Per-agent `KnowledgeStore` configured in `configs/DispositionEffect/Rag/players.yml` |

## §2 Theory → Implementation Mapping

### §2.1 RagDispositionInvestor (simulation-bases.md §4.1)

| Theory Component                           | Rag Implementation                                                               |
|--------------------------------------------|----------------------------------------------------------------------------------|
| Prospect Theory (Kahneman & Tversky, 1979) | Persona + RAG: retrieves Odean (1998) PGR/PLR evidence, Shefrin & Statman (1985) |
| Reference point anchoring                  | RAG provides historical average gain_loss at which investors sell winners (3–5%) |
| Loss reluctance                            | RAG retrieves studies on average holding periods for losers                      |

### §2.2 RagRationalInvestor (simulation-bases.md §4.2)

| Theory Component        | Rag Implementation                                                                    |
|-------------------------|---------------------------------------------------------------------------------------|
| Expected Utility Theory | RAG retrieves rational portfolio theory and rebalancing strategies                    |
| No reference point bias | RAG may retrieve empirical evidence that past prices are irrelevant to future returns |

### §2.3 RagTaxAwareInvestor (simulation-bases.md §4.3)

| Theory Component                           | Rag Implementation                                                          |
|--------------------------------------------|-----------------------------------------------------------------------------|
| Tax-loss harvesting (Constantinides, 1983) | RAG retrieves tax-loss harvesting strategy literature and year-end patterns |
| December effect                            | RAG case studies on year-end tax harvesting reversals                       |

### §2.4 RagInstitutionalInvestor (simulation-bases.md §4.5)

| Theory Component                           | Rag Implementation                                                         |
|--------------------------------------------|----------------------------------------------------------------------------|
| Professional discipline                    | RAG retrieves institutional risk management and professional trading norms |
| Symmetric gain/loss treatment              | Prompt rules apply configured gain and loss thresholds symmetrically       |

### §2.5 RagLossAverse (simulation-bases.md §4.1)

| Theory Component                           | Rag Implementation                                                        |
|--------------------------------------------|---------------------------------------------------------------------------|
| Loss aversion                              | RAG retrieves Prospect Theory and loss-aversion context                   |
| Disposition-effect amplification           | Prompt rules preserve quick winner selling and reluctant loser selling    |

## §3 Prompt Variables

| Variable              | Source                   | Example Value                    |
|-----------------------|--------------------------|----------------------------------|
| `{price}`             | Market broadcast         | `105.0`                          |
| `{purchase_price}`    | Agent state              | `100.0`                          |
| `{gain_loss}`         | Computed                 | `+5.0%`                          |
| `{cash}`              | Agent state              | `75000.0`                        |
| `{position}`          | Agent state              | `500`                            |
| `{portfolio_value}`   | Computed                 | `127500.0`                       |
| `{rag_context}`       | `KnowledgeStore.query()` | Behavioral finance study excerpt |

## §4 Variant-Specific Features

- **Five active API investor types**: Rag mirrors the active LLM/RuleLLM investor set with disposition-biased, rational, tax-aware, institutional, and extreme loss-averse agents.
- **Academic calibration**: RAG context may improve PGR/PLR calibration toward Odean empirical benchmarks.
- **Self-awareness paradox**: RagDispositionInvestor retrieves Prospect Theory studies — it "knows" about its own bias; testing whether this awareness reduces the effect.
- **RAG query formulation**: `_formulate_rag_query()` constructs context-specific query based on current `gain_loss` magnitude and direction.
- **Knowledge store**: `KnowledgeStore` retrieves top-K chunks from pre-embedded behavioral finance knowledge base.

## §5 Architecture

```
Market.decide() → broadcast market_data
RagInvestor.perceive() → store market_data, purchase_price
RagInvestor.decide() → KnowledgeStore.query(gain_loss_context) → retrieved_chunks
                     → LangChainAPIInference.infer(persona + rag_context, user_prompt)
                     → parse_llm_response_with_thinking() → {action, bid_price, quantity, reasoning}
RagInvestor.act() → update cash/position, submit bid order
```

## §6 Config Reference

Rag uses `configs/DispositionEffect/Rag/players.yml`. Each investor has `llm` settings, configured decision parameters, and `rag` settings including `persist_dir`, `docs_dir`, `top_k`, `embed_type`, `embed_model`, and chunking parameters.

## §7 Running Instructions

```bash
python -m examples.DispositionEffect.Rag.run_disposition_rag
```

## §8 Expected Behavior

- PGR/PLR more calibrated toward Odean empirical values (RAG provides anchors)
- RagDispositionInvestor DC may be weaker than pure LLM (bias awareness from reading Prospect Theory)
- RagRationalInvestor may exhibit stronger rationality (retrieves empirical evidence against reference point anchoring)
- RagTaxAwareInvestor PLR highest (RAG reinforces tax-harvesting rationale)
- RagInstitutionalInvestor should remain more symmetric than retail-biased agents
- RagLossAverse may preserve or amplify quick winner selling and loser holding

## §9 References

See `simulation-bases.md §2` for full DOI citations.
