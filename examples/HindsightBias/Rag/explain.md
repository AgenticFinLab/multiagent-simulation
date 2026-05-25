# HindsightBias Rag — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                               |
|--------------------|----------------------------------------------------------------------|
| Variant            | Rag (Retrieval-Augmented Generation)                                 |
| Simulation         | HindsightBias                                                        |
| Decision Mechanism | LLM reasoning augmented with retrieved behavioral finance literature |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                      |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                         |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`                 |

The Rag variant augments each investor's LLM reasoning with retrieved behavioral finance literature. When the `deviation` signal triggers retrieval, relevant papers (Fischhoff 1975, Daniel et al. 1998, Roese & Vohs 2012) are fetched and injected into the prompt. This produces the most moderate behavior: biased agents see their own bias documented and may partially resist it; rational agents access the limits-to-arbitrage literature and trade more confidently.

## §2 Theory → Implementation Mapping

### §2.1 HindsightOverconfident (simulation-bases.md §4.1)

| Theory Component                  | Implementation                                                                                        |
|-----------------------------------|-------------------------------------------------------------------------------------------------------|
| Fischhoff (1975) hindsight effect | RAG retrieves Fischhoff (1975), Roese & Vohs (2012) — bias agent may partially recognize its own bias |
| Momentum amplification            | Retrieved hindsight bias studies may moderate momentum by exposing the "obvious" narrative trap       |
| Self-correction potential         | Most unique to Rag: HindsightOverconfident may resist bias after retrieving literature documenting it |

### §2.2 OutcomeLearner (simulation-bases.md §4.2)

| Theory Component       | Implementation                                                                                         |
|------------------------|--------------------------------------------------------------------------------------------------------|
| Selective attribution  | RAG retrieves Barber & Odean (2000, 2002) documenting outcome attribution costs                        |
| Attribution moderation | Retrieved evidence of overtrading losses may moderate OutcomeLearner's position sizing                 |
| Bull-phase dominance   | RAG may reinforce or reduce OBI depending on whether bull-phase vs. bear-phase literature is retrieved |

### §2.3 ProcessEvaluator (simulation-bases.md §4.3)

| Theory Component     | Implementation                                                                                                  |
|----------------------|-----------------------------------------------------------------------------------------------------------------|
| Process rationality  | RAG retrieves Shleifer & Vishny (1997), Pontiff (2006) — rational agent accesses limits-to-arbitrage literature |
| Correction timing    | Retrieved empirical correction evidence allows earlier, more confident corrective trades                        |
| Highest NCE expected | RAG-retrieved correction cases help ProcessEvaluator time entries more accurately                               |

### §2.4 ContrarianSkeptic (simulation-bases.md §4.4)

| Theory Component              | Implementation                                                                                  |
|-------------------------------|-------------------------------------------------------------------------------------------------|
| Narrative skepticism          | RAG retrieves Kahneman (2011) narrative fallacy, De Bondt & Thaler (1985) contrarian literature |
| Evidence-backed skepticism    | Retrieved contrarian success cases reinforce skepticism with historical precedent               |
| Most differentiated from Rule | Rag §4.4 has access to narrative skepticism literature that Rule §4.4 lacks                     |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component   | Implementation                                                          |
|--------------------|-------------------------------------------------------------------------|
| Black (1986) noise | RAG provides minimal context to NoiseTrader (uninformed by design)      |
| Neutral retrieval  | NoiseTrader RAG retrieval is neutral — no directional bias from history |
| Baseline preserved | Noise trading frequency and magnitude preserved                         |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  λ = price_impact      [default: 0.03]
  γ = mean_reversion    [default: 0.01]
  ε ~ N(0, noise_std)   [default: 0.015]
  NetDemand = Σ signed_quantities
```

Market broadcasts `{price, fundamental, deviation, round}`. RAG retrieval is triggered when |deviation| > 0.02. Retrieved behavioral finance literature is prepended to the LLM prompt as "Research Context."

## §4 Variant Architecture

| Component  | Detail                                                          |
|------------|-----------------------------------------------------------------|
| Base class | `RagPlayer`                                                     |
| Retrieval  | Vector similarity search on behavioral finance paper embeddings |
| Inference  | LLM API call with retrieved research context prepended          |
| Context    | `market_data` + `agent_extras` + retrieved research papers      |
| Output     | Canonical parser JSON plus order records with `rag_context`     |

### RAG Architecture

| Component          | Description                                                                                                                                   |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| Knowledge Base     | Behavioral finance papers: Fischhoff (1975), Daniel et al. (1998), Barber & Odean (2000, 2002), Roese & Vohs (2012), Shleifer & Vishny (1997) |
| Embedding Model    | Text embedding of paper abstracts and key findings                                                                                            |
| Retrieval Strategy | Top-3 most relevant papers by deviation magnitude and agent type                                                                              |
| Injection Format   | Prepended as "Research Context" section in system prompt                                                                                      |
| Trigger Condition  | Retrieve when                                                                                                                                 |

## §5 Config Reference

Config file: `configs/HindsightBias/Rag/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `hindsight_inflation`, `prediction_overweight` (HindsightOverconfident)
- `success_attribution`, `failure_discount` (OutcomeLearner)
- `process_weight`, `outcome_weight` (ProcessEvaluator)
- `skepticism_level`, `max_order` (ContrarianSkeptic)
- `trade_probability`, `max_order` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`
- RAG: shared `examples/document-sources` resources, Hunyuan embedding config, `top_k`, and persisted `rag_index`

## §6 Running Instructions

```bash
python -m examples.HindsightBias.Rag.run_hindsight_bias \
    -c configs/HindsightBias/Rag/simulation.yml
```

Or via Streamlit UI: select "HindsightBias" → "Rag" variant.

## §7 Expected Behavior

- **Lowest HBI**: Biased agents retrieve their own bias documentation — most likely to partially self-correct → HBI target 0.015–0.05
- **Highest NCE**: ProcessEvaluator and ContrarianSkeptic retrieve correction literature → most efficient rational correction → NCE target 0.45–0.75
- **OBI moderated**: Retrieved Barber & Odean losses documentation moderates OutcomeLearner's bull-phase confidence
- **VAF similar to LLM**: Rag variability similar in magnitude to LLM variability
- **Research signature**: Rag is the only variant where biased agents may explicitly acknowledge bias in their reasoning — this is the key research finding

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — HindsightOverconfident self-correction
- Daniel et al. (1998) `doi:10.1111/0022-1082.00077` — overconfidence momentum
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — rational correction context

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
