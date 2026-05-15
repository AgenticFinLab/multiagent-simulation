# GameStopShortSqueeze — Rag Variant

## §1 Overview

The Rag variant implements the short squeeze with RAG-augmented LLM reasoning. Retrieved documents about the GME 2021 event, Reddit WallStreetBets posts, short squeeze mechanics, and historical squeezes (VW 2008, Silver 1979) reinforce each agent's behavioral role. Rag retrieval may amplify §4.1 retail enthusiasm (through GME historical momentum retrieval) or §4.2 fear (through retrieved squeeze postmortem data).

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | Rag                                          |
| Simulation         | GameStopShortSqueeze                         |
| Decision Mechanism | RAG-augmented LLM                            |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |

---

## §2 Theory → Implementation Mapping

### §2.1 RagLLMRetailCoordinated (`simulation-bases.md §4.1`)
| Theory Component         | Implementation                                                                                    |
|--------------------------|---------------------------------------------------------------------------------------------------|
| Social coordination      | System prompt: retail coordinator; RAG retrieves WallStreetBets posts, GME Jan 2021 momentum data |
| Historical reinforcement | Retrieved GME squeeze data may amplify buying conviction                                          |

### §2.2 RagLLMShortSellerHF (`simulation-bases.md §4.2`)
| Theory Component   | Implementation                                                                                     |
|--------------------|----------------------------------------------------------------------------------------------------|
| Forced covering    | System prompt: short-seller persona; RAG retrieves Melvin Capital postmortem, VW 2008 squeeze data |
| Fear amplification | Retrieved squeeze postmortems reinforce covering urgency                                           |

### §2.3 RagLLMMarketMakerGamma (`simulation-bases.md §4.3`)
| Theory Component | Implementation                                                                           |
|------------------|------------------------------------------------------------------------------------------|
| Gamma hedging    | System prompt: market maker; RAG retrieves options flow data and gamma squeeze mechanics |

### §2.4 RagLLMInstitutionalValue (`simulation-bases.md §4.4`)
| Theory Component        | Implementation                                                                        |
|-------------------------|---------------------------------------------------------------------------------------|
| Fundamental value       | System prompt: value investor; RAG retrieves analyst reports on GameStop fundamentals |
| Conviction strengthened | Retrieved fundamental analysis may reinforce early exit decision                      |

### §2.5 RagLLMMomentumRetail (`simulation-bases.md §4.5`)
| Theory Component | Implementation                                                      |
|------------------|---------------------------------------------------------------------|
| FOMO             | System prompt: FOMO retail; RAG retrieves social media buzz metrics |

---

## §3 Rag-Specific Notes

- **SQI amplification likely**: Retrieved GME momentum data reinforces §4.1 buying, potentially pushing SQI higher than Rule.
- **Faster covering**: Retrieved squeeze postmortems may accelerate §4.2 covering (fear), shortening SCD vs. Rule.
- **Corpus dependency**: Key — if retrieval corpus is GME-focused, all metrics skew toward historical GME values.

---

## §4 Expected Ranges (Rag Variant vs. Rule Baseline)

| Metric | Rag Expected Range | vs. Rule | Basis                                               |
|--------|--------------------|----------|-----------------------------------------------------|
| SQI    | 1.5–7.0            | Higher   | Retrieved squeeze cases reinforce §4.1 buying       |
| PAR    | 0.3–1.5            | Higher   | Larger and longer squeeze                           |
| SCD    | 1–6 rounds         | Shorter  | Faster covering due to retrieved fear evidence      |
| IEP    | Rounds 2–8         | Earlier  | Retrieved fundamental analysis prompts earlier sell |
| WTI    | 0.15–0.50          | Higher   | Larger wealth transfer in amplified squeeze         |
