# EuropeanDebtCrisis Rag — Implementation Explanation

## §1 Overview

The Rag variant augments LLM crisis reasoning with RAG-retrieved documents from crisis literature, historical episodes, and ECB policy records. Each investor retrieves relevant passages before deciding, enabling knowledge-grounded crisis assessment that can amplify or moderate the self-fulfilling spiral based on what is retrieved.

| Aspect             | Detail                                                  |
|--------------------|---------------------------------------------------------|
| Variant            | Rag (RAG-augmented LLM)                                 |
| Simulation         | EuropeanDebtCrisis                                      |
| Decision Mechanism | RAG-retrieved crisis literature + LLM persona reasoning |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                         |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`            |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMPeripheryBondSeller (simulation-bases.md §4.1)

| Theory Component                              | Implementation                                                                                       |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------|
| Self-fulfilling speculation (De Grauwe, 2011) | System prompt: sell-side persona; RAG retrieves De Grauwe (2011) on self-fulfilling crisis mechanics |
| Retrieved evidence amplifies panic            | Passages on Greek/Spanish crisis escalation may accelerate LLM sell decision                         |
| Historical calibration                        | RAG retrieves historical threshold data; LLM may calibrate quantity to crisis severity               |

### §2.2 RagLLMCreditorPanicker (simulation-bases.md §4.2)

| Theory Component                            | Implementation                                                                          |
|---------------------------------------------|-----------------------------------------------------------------------------------------|
| Sovereign-bank nexus (Acharya et al., 2014) | System prompt: creditor persona; RAG retrieves Acharya et al. (2014) on doom loop       |
| Knowledge-informed panic                    | Retrieved evidence of bank failures (Lehman, Irish banks) may trigger more severe panic |
| Contagion literature                        | RAG retrieves contagion models; LLM applies doom loop reasoning from academic evidence  |

### §2.3 RagLLMCoreBondBuyer (simulation-bases.md §4.3)

| Theory Component                         | Implementation                                                                                |
|------------------------------------------|-----------------------------------------------------------------------------------------------|
| Flight-to-quality (De Grauwe & Ji, 2012) | System prompt: safety-seeker persona; RAG retrieves De Grauwe & Ji (2012) on capital rotation |
| Retrieved crisis history                 | Historical flight-to-safety episodes inform LLM's rotation timing and size                    |
| Recovery signal                          | RAG may retrieve ECB intervention histories, helping LLM identify when to reverse rotation    |

### §2.4 RagLLMECBIntervenor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                                              |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Central bank backstop (Draghi, 2012) | System prompt: ECB persona; RAG retrieves Draghi (2012) speech and OMT program documents                    |
| Retrieved policy documents           | Draghi "whatever it takes" transcript grounds LLM's intervention commitment                                 |
| Credible commitment signal           | Retrieved OMT documents allow LLM to model the confidence effect — may activate earlier and more decisively |

### §2.5 RagLLMHedgedFund (simulation-bases.md §4.5)

| Theory Component                              | Implementation                                                                                                |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt: hedged fund persona; RAG retrieves Shleifer & Vishny (1997) and Brunnermeier & Pedersen (2009) |
| Capital constraint awareness                  | Retrieved limits-to-arbitrage literature informs more cautious position sizing at extreme deviations          |
| Historical arbitrage performance              | RAG may retrieve LTCM-style crisis examples, moderating position size                                         |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class shared with Rule variant. All Rag investors send orders with `provides_liquidity` field.

## §4 Variant Architecture

| Component      | Detail                                                                                        |
|----------------|-----------------------------------------------------------------------------------------------|
| Base class     | `RagLLMInvestor` → `GeneralPlayer`                                                            |
| Inference      | `LangChainAPIInference` + RAG knowledge retrieval                                             |
| Context        | `price`, `fundamental`, `deviation`, `cash`, `position`, `round` + retrieved documents        |
| Output parsing | JSON response with `action`, `quantity`, `reasoning`, `analysis`, `provides_liquidity`        |
| RAG retrieval  | Query built from market state; documents from EDC knowledge base (De Grauwe, Draghi, Acharya) |

## §5 Config Reference

Config file: `configs/EuropeanDebtCrisis/Rag/simulation.yml`

LLM config under `extras.llm`:
- `lm_name`, `generation_config`

RAG config:
- `knowledge_base`: path to crisis documents
- `top_k`: retrieved document count

## §6 Running Instructions

```bash
python -m examples.EuropeanDebtCrisis.Rag.run_edc_ragllm \
    -c configs/EuropeanDebtCrisis/Rag/simulation.yml
```

## §7 Expected Behavior

- **Knowledge-amplified crisis**: Retrieved De Grauwe passages reinforce panic — CDI may exceed Rule in some runs
- **Draghi credibility**: Retrieved OMT documents make ECB more decisive — IER ceiling higher than Rule
- **Variable AR**: Retrieved doom loop literature can produce more or less severe creditor panic — AR range 0.7–1.8
- **SRT**: 4–22 rounds; retrieved crisis resolution histories inform ECB commitment timing

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
