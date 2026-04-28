# EquityPremium Rag — Implementation Explanation

## §1 Overview

The Rag variant augments LLM investor personas with Retrieval-Augmented Generation. Before deciding on allocation, each investor retrieves relevant passages from behavioral economics literature. Retrieved knowledge grounds allocation decisions in academic evidence, potentially amplifying or moderating the simulated equity premium based on what is retrieved.

| Aspect             | Detail                                                                    |
|--------------------|---------------------------------------------------------------------------|
| Variant            | Rag (RAG-augmented LLM)                                                   |
| Simulation         | EquityPremium                                                             |
| Decision Mechanism | RAG-retrieved knowledge + LLM persona reasoning — no hardcoded rules      |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                           |
| Market Broadcast   | `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMMyopicLossAverse (simulation-bases.md §4.1)

| Theory Component                               | Implementation                                                                                           |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Myopic loss aversion (Benartzi & Thaler, 1995) | System prompt: loss-averse persona; RAG retrieves Benartzi & Thaler (1995) passages on myopic evaluation |
| Retrieved evidence reinforces myopia           | Passages on high loss probability under short horizons amplify the investor's risk aversion              |
| Knowledge-calibrated threshold                 | LLM uses retrieved λ ≈ 2.25 to calibrate perceived risk — may be more precise than hardcoded value       |

### §2.2 RagLLMLongTermInvestor (simulation-bases.md §4.2)

| Theory Component                          | Implementation                                                                               |
|-------------------------------------------|----------------------------------------------------------------------------------------------|
| Long evaluation horizon (Samuelson, 1969) | System prompt: long-horizon persona; RAG retrieves Samuelson (1969) on horizon insensitivity |
| Retrieved evidence stabilizes allocation  | Long-horizon literature passages prevent panic selling even during bad runs                  |
| Historical grounding                      | RAG may retrieve historical equity premium data, reinforcing long-term equity holding        |

### §2.3 RagLLMInstitutionalInvestor (simulation-bases.md §4.3)

| Theory Component                                | Implementation                                                                                  |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Risk-neutral benchmark (Mehra & Prescott, 1985) | System prompt: institutional persona; RAG retrieves Mehra & Prescott (1985) on rational pricing |
| Excess return computation                       | Retrieved passages calibrate excess return expectations; LLM applies proportional rule          |
| Market efficiency knowledge                     | RAG may retrieve EMH literature, moderating over-reaction                                       |

### §2.4 RagLLMRiskAverseSaver (simulation-bases.md §4.4)

| Theory Component                                           | Implementation                                                                                |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Prospect theory bond preference (Kahneman & Tversky, 1979) | System prompt: preservation persona; RAG retrieves Kahneman & Tversky (1979) on loss aversion |
| Retrieved loss aversion evidence                           | Passages on λ ≈ 2.25 reinforce bond preference; investor may demand even higher premium       |
| Historical crash evidence                                  | RAG may retrieve crash histories, further reinforcing extreme bond preference                 |

### §2.5 RagLLMRationalOptimizer (simulation-bases.md §4.5)

| Theory Component                          | Implementation                                                                                           |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Adaptive optimization (rational baseline) | System prompt: optimizer persona; RAG retrieves arbitrage and efficiency literature                      |
| Context-aware trading                     | Retrieved market microstructure knowledge allows more informed directional trades                        |
| Noise moderation                          | Knowledge retrieval reduces pure noise; this investor becomes more signal-driven than Rule's NoiseTrader |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) × (1 + μ_stock + demand_impact + ε(t))
```

Market is shared with Rule variant. All Rag investors send `stock_qty` orders with `provides_liquidity` field.

## §4 Variant Architecture

| Component      | Detail                                                                                       |
|----------------|----------------------------------------------------------------------------------------------|
| Base class     | `RagLLMInvestor` → `GeneralPlayer`                                                           |
| Inference      | `LangChainAPIInference` + RAG knowledge retrieval                                            |
| Context        | `stock_price`, `stock_return`, `bond_return`, `cash`, `stock`, `round` + retrieved documents |
| Output parsing | JSON response with `stock_qty`, `strategy`, `reasoning`, `provides_liquidity`                |
| RAG retrieval  | Query built from market state; documents from equity premium knowledge base                  |

## §5 Config Reference

Config file: `configs/EquityPremium/Rag/simulation.yml`

LLM config under `extras.llm`:
- `lm_name`, `generation_config`

RAG config (if present):
- `knowledge_base`: path to equity premium / behavioral finance documents
- `top_k`: retrieved document count

## §6 Running Instructions

```bash
python -m examples.EquityPremium.Rag.run_equity_premium_ragllm \
    -c configs/EquityPremium/Rag/simulation.yml
```

## §7 Expected Behavior

- **Retrieved theory reinforcement**: Benartzi & Thaler passages amplify loss aversion — SEP may be slightly higher than Rule
- **Better calibrated allocation**: Knowledge-grounded decisions reduce extreme deviations seen in pure LLM
- **SEP range**: 0.03–0.08 (knowledge anchors central tendency)
- **PWE**: 0.83–0.97 (retrieval quality variance introduces outliers)

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
