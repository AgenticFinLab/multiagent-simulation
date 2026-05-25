# EuropeanDebtCrisis Rag — Analysis Documentation

## §1 Analysis Objectives

Measure how RAG-retrieved crisis literature affects the self-fulfilling spiral dynamics. Key questions:
- Does retrieved De Grauwe/Acharya literature amplify crisis severity beyond Rule baseline?
- Does retrieved Draghi "whatever it takes" content improve ECB intervention effectiveness?
- How does RAG knowledge variability (retrieval quality) affect CDI and IER across runs?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                     | analysis-bases.md ref |
|----------------------------------------|------------------------------------------------------------------------------|-----------------------|
| Crisis Depth Index (CDI)               | `crisis_depth_index(price_history, fundamental)`                             | §2.1                  |
| Crisis Duration (CD)                   | `crisis_duration(price_history, fundamental, crisis_threshold=-0.10)`        | §2.2                  |
| Amplification Ratio (AR)               | `amplification_ratio(creditor_sell_volume, periphery_sell_volume)`           | §2.3                  |
| Intervention Effectiveness Ratio (IER) | `intervention_effectiveness_ratio(ecb_buy_rounds, crisis_rounds)`            | §2.4                  |
| Spread Recovery Time (SRT)             | `spread_recovery_time(price_history, fundamental, recovery_threshold=-0.05)` | §2.5                  |
| Arbitrage Profit Rate (APR)            | `arbitrage_profit_rate(hf_terminal_wealth, hf_initial_wealth)`               | §2.6                  |
| RAG Retrieval Quality                  | `analyze_rag_knowledge_effect(rag_contexts)`                                 | §2.7                  |

## §3 Rag-Specific Notes

- **RagLLMPeripheryBondSeller (§4.1)**: Retrieved De Grauwe passages reinforce speculative selling — CDI may be slightly deeper than Rule; onset slightly earlier when crisis literature is retrieved
- **RagLLMCreditorPanicker (§4.2)**: Retrieved doom-loop literature (Acharya et al.) amplifies creditor panic — AR upper bound higher than Rule; more severe two-wave crises possible
- **RagLLMCoreBondBuyer (§4.3)**: Historical flight-to-safety examples (2010–2012 data) calibrate rotation timing; CDI floor slightly better than pure LLM
- **RagLLMECBIntervenor (§4.4)**: Retrieved Draghi OMT documents model credible commitment more authentically — IER ceiling above Rule; crisis may resolve faster when ECB literature is retrieved
- **RagLLMHedgedFund (§4.5)**: Retrieved LTCM-style limits-to-arbitrage examples make HedgedFund more cautious at crisis peaks; APR may be lower than Rule but less variance
- **vs. Rule**: CDI central tendency similar; upper tail higher due to knowledge-amplified panic; IER upper bound higher due to knowledge-modeled ECB credibility

## §4 Expected Ranges

| Metric | Rag Expected Range | vs. Rule Baseline                             | vs. LLM Baseline  |
|--------|--------------------|-----------------------------------------------|-------------------|
| CDI    | 0.12–0.38          | Slightly wider; upper tail higher             | Similar           |
| CD     | 8–35 rounds        | Similar central; wider upper                  | Narrower than LLM |
| AR     | 0.7–1.8            | Higher upper bound                            | Similar           |
| IER    | 0.65–0.98          | Higher ceiling                                | Higher ceiling    |
| SRT    | 4–22 rounds        | Similar; can be shorter when Draghi retrieved | Narrower          |
| APR    | 0.02–0.18          | Lower floor (caution at peaks)                | Similar           |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Cross-Variant Comparison

| Comparison | Interpretation |
|---|---|
| Rag vs RuleLLM | Measures the marginal effect of retrieved sovereign-debt context. |
| Rag vs LLM | Separates persona-only reasoning from knowledge-augmented reasoning. |
| Rag vs Rule | Tests whether RAG knowledge improves or weakens baseline mechanism emergence. |

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Confirm RAG assets and embedding configuration were available.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Confirm `rag_stats.json` is written and retrieval-health records are auditable.
- Audit parse failures and retry counts before acceptance; deterministic parser/provider failures must fail fast.
