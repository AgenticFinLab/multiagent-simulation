# HerdingInformation Rag — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                             |
|--------------------|--------------------------------------------------------------------|
| Variant            | Rag (Retrieval-Augmented Generation)                               |
| Simulation         | HerdingInformation                                                 |
| Decision Mechanism | LLM reasoning augmented with retrieved historical cascade examples |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                       |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε`               |

The Rag variant augments each investor's LLM reasoning with retrieved historical cascade episodes from a knowledge base. When the `deviation` signal crosses a threshold, relevant historical cascade examples are retrieved and injected into the prompt. This reinforces herding behavior — agents who see historical evidence of successful cascades are more likely to follow the crowd — producing higher CCI and longer CPD than the Rule or LLM variants.

## §2 Theory → Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component                             | Implementation                                                                                   |
|----------------------------------------------|--------------------------------------------------------------------------------------------------|
| Bikhchandani et al. (1992) cascade formation | RAG retrieves historical cascade activation examples; reinforces herding decision                |
| Social signal weighting                      | Retrieved examples include social_weight ranges from past cascades; LLM scales order accordingly |
| Cascade direction                            | RAG confirms historical precedent for cascade direction based on deviation sign                  |
| Pre-cascade                                  | RAG may retrieve pre-cascade buildup examples, enabling earlier cascade activation               |

### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component                              | Implementation                                                                            |
|-----------------------------------------------|-------------------------------------------------------------------------------------------|
| Scharfstein & Stein (1990) reputation herding | RAG retrieves institutional herding cases (mutual fund manager mimicry)                   |
| Lower activation threshold                    | Retrieved career-risk scenarios reinforce early activation below 0.02                     |
| Career concern amplification                  | RAG provides historical reputation cost examples — increases reputation_concern weighting |

### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component        | Implementation                                                                        |
|-------------------------|---------------------------------------------------------------------------------------|
| Rational Bayesian agent | RAG retrieves failed contrarian examples; may reduce independent thinking confidence  |
| Contrarian signal       | LLM faces retrieved evidence of cascades overrunning private signals — may reduce ICE |
| Activation threshold    | RAG may discourage independent action when historical examples show contrarian losses |

### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component                               | Implementation                                                                                   |
|------------------------------------------------|--------------------------------------------------------------------------------------------------|
| De Bondt & Thaler (1985) deliberate contrarian | RAG retrieves reversal examples; may support contrarian conviction                               |
| Higher threshold than IndependentThinker       | Retrieved evidence may trigger contrarian below normal threshold in clear overvaluation episodes |
| Cascade resistance                             | RAG provides historical cascade-break examples — reinforces contrarian decision                  |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                                           |
|---------------------------------|--------------------------------------------------------------------------|
| Black (1986) uninformed trading | RAG provides minimal context to NoiseTrader (uninformed by design)       |
| Random direction                | NoiseTrader RAG retrieval is neutral — no directional bias from history  |
| Accidental cascade initiator    | Noise trades preserved; cascade_count increments as in Rule/LLM variants |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  λ = price_impact      [default: 0.001]
  γ = mean_reversion    [default: 0.05]
  ε ~ N(0, noise_std)   [default: 0.5]
  NetDemand = Σ signed_quantities
```

Market broadcasts `{price, fundamental, deviation, round}`. When |deviation| exceeds the RAG retrieval threshold, the knowledge base is queried for similar historical episodes. Retrieved context is prepended to the LLM prompt.

## §4 Variant Architecture

| Component     | Detail                                                            |
|---------------|-------------------------------------------------------------------|
| Base class    | `RagPlayer`                                                       |
| Retrieval     | Vector similarity search on historical cascade episode embeddings |
| Inference     | LLM API call with retrieved context prepended                     |
| Context       | `market_data` + `agent_extras` + retrieved historical examples    |
| Output        | `{"action": "buy"/"sell"/"hold", "quantity": int}`                |
| Cascade state | `cascade_count` passed via prompt; retrieval threshold:           |

### RAG Architecture

| Component          | Description                                                                     |
|--------------------|---------------------------------------------------------------------------------|
| Knowledge Base     | Historical cascade episodes from 1929, 1987, 2000, 2007–08, 2020                |
| Embedding Model    | Text embedding of cascade context (deviation level, round, agent types)         |
| Retrieval Strategy | Top-3 most similar historical episodes by deviation magnitude and cascade_count |
| Injection Format   | Prepended as "Historical Precedent" section in system prompt                    |
| Trigger Condition  | Retrieve when                                                                   |

## §5 Config Reference

Config file: `configs/HerdingInformation/Rag/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `social_weight`, `cascade_trigger` (CascadeFollower)
- `reputation_concern` (ReputationHerder)
- `signal_precision` (IndependentThinker)
- `contrarian_threshold` (Contrarian)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`
- LLM: `model`, `temperature`, `max_tokens`
- RAG: `knowledge_base_path`, `top_k`, `retrieval_threshold`

## §6 Running Instructions

```bash
python -m examples.HerdingInformation.Rag.run_herding_information \
    -c configs/HerdingInformation/Rag/simulation.yml
```

Or via Streamlit UI: select "HerdingInformation" → "Rag" variant.

## §7 Expected Behavior

- **Higher CCI**: RAG retrieves historical cascade examples reinforcing herding → CCI target 0.55–0.75 (vs. Rule 0.40–0.70)
- **Longer CPD**: Historical precedent reinforces cascade persistence — CPD target 4–12 rounds (vs. Rule 3–10)
- **Higher RHI**: RAG retrieves institutional herding cases → ReputationHerder more aggressive → RHI may exceed 1.20
- **Higher ICE**: Retrieved cascade evidence suppresses private signal use → ICE target 0.20–0.45
- **Similar VAF**: Cascade reinforcement produces similar volatility amplification to Rule — VAF 1.5–3.5
- **IndependentThinker dampened**: Historical contrarian loss examples retrieved by RAG may reduce independent correction, making cascades harder to break

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — CascadeFollower cascade theory
- Scharfstein & Stein (1990) — ReputationHerder reputation herding
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — limits to arbitrage and cascade persistence

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
