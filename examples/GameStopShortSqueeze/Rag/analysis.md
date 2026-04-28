# GameStopShortSqueeze — Rag Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | Rag                          |
| Metrics   | SQI, PAR, SCD, IEP, ACC, WTI |
| Reference | `analysis-bases.md`          |
| Baseline  | Rule variant                 |

---

## §2 Metric → Function Mapping

| Metric | Function Signature                                          | Key Args                                        |
|--------|-------------------------------------------------------------|-------------------------------------------------|
| SQI    | `squeeze_intensity_index(price_history, fundamental)`       | `price_history: list`, `fundamental: float`     |
| PAR    | `price_acceleration_ratio(price_history)`                   | `price_history: list`                           |
| SCD    | `short_covering_duration(position_history)`                 | `position_history: list`                        |
| IEP    | `institutional_exit_point(position_history, price_history)` | `position_history: list`, `price_history: list` |
| ACC    | `accuracy_metric(agent_decisions, outcomes)`                | `agent_decisions: list`, `outcomes: list`       |
| WTI    | `wealth_transfer_index(final_wealth, initial_wealth)`       | `final_wealth: dict`, `initial_wealth: dict`    |

---

## §3 Rag-Specific Notes

### §3.1 RagLLMRetailCoordinated
- Retrieved GME squeeze cases reinforce buying conviction → SQI likely higher than Rule.
- Excess enthusiasm: if retrieval corpus is GME-focused, PAR may reach upper range (> 1.0).

### §3.2 RagLLMShortSellerHF
- Retrieved squeeze postmortems (Melvin Capital, VW 2008) amplify covering urgency.
- SCD may shorten (faster panic covering) vs. Rule baseline (3–8 rounds → 1–6 rounds).

### §3.3 RagLLMMarketMakerGamma
- Retrieved options flow data anchors gamma hedge behavior; less drift than pure LLM variant.

### §3.4 RagLLMInstitutionalValue
- Retrieved analyst reports reinforce fundamental anchoring → IEP may be earlier (rounds 2–8).

### §3.5 RagLLMMomentumRetail
- Retrieved social media buzz metrics amplify FOMO buying; WTI rises with greater retail participation.

---

## §4 Expected Ranges (Rag vs. Rule Baseline)

| Metric | Rag Expected Range | vs. Rule | Basis                                             |
|--------|--------------------|----------|---------------------------------------------------|
| SQI    | 1.5–7.0            | Higher   | Retrieved squeeze cases reinforce §4.1 buying     |
| PAR    | 0.3–1.5            | Higher   | Larger and longer squeeze amplitude               |
| SCD    | 1–6 rounds         | Shorter  | Faster covering driven by retrieved fear evidence |
| IEP    | Rounds 2–8         | Earlier  | Fundamental reports prompt earlier §4.4 exit      |
| ACC    | 0.45–0.70          | Similar  | RAG improves contextual accuracy                  |
| WTI    | 0.15–0.50          | Higher   | Greater wealth transfer in amplified squeeze      |
