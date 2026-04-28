# HerdingInformation Rag — Analysis Guide

## §1 Analysis Objectives

The Rag variant analysis measures the **amplification effect** of retrieval-augmented generation on information cascade dynamics. The core research question is whether historical cascade evidence retrieved from the knowledge base strengthens herding behavior, producing higher CCI and longer CPD than the Rule or LLM baselines.

1. Quantify the cascade amplification effect: does RAG increase CCI above the Rule baseline?
2. Measure CPD change: does historical precedent lengthen cascade persistence?
3. Assess ICE increase: does retrieved cascade evidence suppress private signal use?
4. Verify RHI elevation: do retrieved reputation-herding cases make ReputationHerder more aggressive?

Analysis objectives:
- CCI target 0.55–0.75: RAG cascade examples should produce higher concentration than Rule (0.40–0.70)
- CPD target 4–12 rounds: historical precedent extends cascade persistence
- RHI target 0.60–1.50: retrieved institutional herding cases elevate reputation concern
- ICE target 0.20–0.45: cascade evidence suppresses private signals more than Rule
- VAF in 1.5–3.5: similar to Rule (cascade reinforcement amplifies price deviation similarly)
- WDI in 0.12–0.30: similar to Rule (wealth transfer pattern preserved)

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md | Python Function                     | Primary Input                             |
|--------|---------------------------------|-------------------|-------------------------------------|-------------------------------------------|
| CCI    | Cascade Concentration Index     | §2.1              | `cascade_concentration_index()`     | trade_history, price_history, fundamental |
| CPD    | Cascade Persistence Duration    | §2.2              | `cascade_persistence_duration()`    | price_history, fundamental                |
| RHI    | Reputation Herding Index        | §2.3              | `reputation_herding_index()`        | trade_history, price_history, fundamental |
| ICE    | Information Cascade Efficiency  | §2.4              | `information_cascade_efficiency()`  | trade_history, price_history, fundamental |
| VAF    | Volatility Amplification Factor | §2.5              | `volatility_amplification_factor()` | price_history, fundamental                |
| WDI    | Wealth Distribution Index       | §2.6              | `wealth_distribution_index()`       | agent_states, final_price                 |

All functions defined in `Rag/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 Rag-Specific Notes

- **Knowledge base composition matters**: If the knowledge base contains predominantly cascade-forming events (1929, 1987, 2000, 2008), retrieved context will amplify herding. If it includes contrarian correction events, CascadeFollower may be dampened. Document the knowledge base composition when reporting results.
- **Retrieval trigger tracking**: Log which rounds trigger RAG retrieval (|deviation| > 0.02). High retrieval frequency (> 30% of rounds) indicates the cascade is very active — expect high CCI and ICE.
- **Multi-seed averaging**: Like LLM variant, run ≥5 seeds. Rag variance may be lower than LLM if knowledge base is deterministic, but retrieval matching introduces its own variability.
- **IndependentThinker suppression**: Monitor whether IndependentThinker trade frequency decreases in Rag vs. Rule — if RAG retrieves cascade loss examples for IndependentThinker, the agent may trade less frequently, reducing correction capacity and inflating CPD.
- **CCI > 0.75 interpretation**: In the Rag variant, CCI > 0.75 is not automatically a calibration failure (unlike Rule where > 0.75 is a red flag). RAG cascade reinforcement can legitimately push CCI to 0.80 without representing miscalibration.

---

## §4 Expected Ranges

| Metric | Rag Expected | vs. Rule             | vs. LLM         | Notes                                      |
|--------|--------------|----------------------|-----------------|--------------------------------------------|
| CCI    | 0.55–0.75    | Higher (+10 to +15%) | Higher          | RAG cascade examples amplify herding       |
| CPD    | 4–12 rounds  | Longer (+1 to +3)    | Longer          | Historical persistence reinforced          |
| RHI    | 0.60–1.50    | Higher               | Higher          | Institutional herding cases retrieved      |
| ICE    | 0.20–0.45    | Higher (+5 to +10%)  | Higher          | Social evidence suppresses private signals |
| VAF    | 1.5–3.5      | ≈ Rule               | Higher than LLM | Similar cascade amplitude                  |
| WDI    | 0.12–0.30    | ≈ Rule               | ≈ Rule          | Wealth transfer preserved                  |

---

## §5 References

- `analysis-bases.md §2.1` — CCI definition, formula, interpretation
- `analysis-bases.md §2.2` — CPD definition, formula, interpretation
- `analysis-bases.md §2.3` — RHI definition, formula, interpretation
- `analysis-bases.md §2.4` — ICE definition, formula, interpretation
- `analysis-bases.md §2.5` — VAF definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- `analysis-bases.md §5` — Cross-variant comparison table
- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — Cascade amplification baseline
- Scharfstein & Stein (1990) JSTOR:2006678 — Reputation herding reinforcement
