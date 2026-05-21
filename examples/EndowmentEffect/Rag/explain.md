# EndowmentEffect Rag — Implementation Explanation

## §1 Overview

The Rag variant augments the RuleLLM prompt structure with Retrieval-Augmented Generation (RAG). Each investor class retrieves relevant domain passages before reasoning, combines that context with the same persona/rule guidance used by RuleLLM, and returns canonical trading JSON. This allows retrieved knowledge to moderate or amplify the endowment effect depending on the retrieved content.

| Aspect             | Detail                                                                    |
|--------------------|---------------------------------------------------------------------------|
| Variant            | Rag (RAG-augmented LLM)                                                   |
| Simulation         | EndowmentEffect                                                           |
| Decision Mechanism | RAG-retrieved knowledge + RuleLLM-style persona/rule guidance |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                           |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `cash`, `position`, `round`          |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMEndowedHolder (simulation-bases.md §4.1)

| Theory Component                          | Implementation                                                                                            |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Endowment premium (Kahneman et al., 1990) | System prompt: ownership attachment persona; RAG retrieves Kahneman et al. (1990) passages on WTA/WTP gap |
| Loss aversion suppresses selling          | Retrieved documents reinforce reluctance to sell below endowment premium                                  |
| Historical anchoring                      | RAG may retrieve episodes of prolonged holding during overvaluation, reinforcing inertia                  |

### §2.2 RagLLMStatusQuoSeller (simulation-bases.md §4.2)

| Theory Component                               | Implementation                                                                                           |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Status quo bias (Samuelson & Zeckhauser, 1988) | System prompt: inertia persona; RAG retrieves Samuelson & Zeckhauser (1988) passages                     |
| Knowledge-informed inertia                     | Retrieved passages may strengthen or weaken inertia depending on market context retrieved                |
| Adaptive threshold interpretation             | Retrieved passages may influence reasoning and sizing while the prompt still presents RuleLLM-style thresholds |

### §2.3 RagLLMRationalArbitrageur (simulation-bases.md §4.3)

| Theory Component                             | Implementation                                                                                      |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Rational expectations benchmark (Muth, 1961) | System prompt: arbitrageur persona; RAG retrieves Muth (1961) and Shleifer & Vishny (1997) passages |
| Retrieved evidence moderates aggressiveness  | If RAG retrieves evidence of persistent overvaluation, arbitrageur may delay entry                  |
| Symmetric arbitrage                          | Persona instructs symmetric buy/sell; RAG provides market context for sizing                        |

### §2.4 RagLLMNewBuyer (simulation-bases.md §4.4)

| Theory Component                                         | Implementation                                                                           |
|----------------------------------------------------------|------------------------------------------------------------------------------------------|
| Rational WTP equals market value (Kahneman et al., 1990) | System prompt: unbiased buyer persona; RAG retrieves WTP rationality literature          |
| Knowledge-informed entry                                 | Retrieved passages help LLM judge whether current deviation justifies buying             |
| No ownership premium                                     | Persona explicitly lacks prior ownership; RAG provides external justification for action |

### §2.5 RagLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | Implementation                                                                            |
|----------------------------------------|-------------------------------------------------------------------------------------------|
| Uninformed noise trading (Black, 1986) | System prompt: noise trader persona; RAG retrieves Black (1986) passages on noise trading |
| Retrieved noise amplification          | RAG may retrieve market news that triggers random-direction trades, simulating noise      |
| Constrained by portfolio               | LLM respects cash and position limits despite random direction                            |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class is imported from `Rule/players.py` (shared). All Rag investors submit orders to the same Market.

## §4 Variant Architecture

| Component      | Detail                                                                                  |
|----------------|-----------------------------------------------------------------------------------------|
| Base class     | `RagLLMInvestor` → `GeneralPlayer`                                                      |
| Inference      | `LangChainAPIInference` + RAG knowledge retrieval                                       |
| Context        | `price`, `fundamental`, `deviation`, `cash`, `position`, `round` + retrieved documents  |
| Output parsing | JSON response with `action`, `bid_price`, `quantity`, `reasoning`, `analysis`; payload also records `rag_context` |
| RAG retrieval  | Query built from market state; documents retrieved from endowment effect knowledge base |

## §5 Config Reference

Config file: `configs/EndowmentEffect/Rag/simulation.yml`

LLM config under each player's `extras.llm`:
- `lm_name`: model identifier
- `generation_config`: temperature, max_tokens etc.

RAG config under each player's `extras.private_knowledge.rag`:
- `from_global_index_dir`: shared index names such as `rag_index`
- `embed_type`, `embed_model`, `embed_api_key`, `embed_api_base`: embedding client configuration
- `chunk_size`, `chunk_overlap`, `top_k`: retrieval construction and query settings

## §6 Running Instructions

```bash
python -m examples.EndowmentEffect.Rag.run_endowment_effect \
    -c configs/EndowmentEffect/Rag/simulation.yml
```

## §7 Expected Behavior

- **Knowledge-moderated endowment effect**: Retrieved Kahneman et al. passages tend to reinforce the endowment premium — expect strong volume suppression
- **Higher variability**: RAG retrieval quality affects each round; MAD variance is higher than Rule
- **MAD range**: 0.03–0.14 (retrieval can moderate or amplify deviation)
- **VSR**: 0.40–0.70 (knowledge retrieval generally reinforces holding bias)

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
