# DotComBubble Rag Variant — analysis.md

## §1 Analysis Objectives

Assess whether RAG-retrieved historical bubble knowledge moderates bubble amplitude, shortens duration, and improves stabilising-agent wealth outcomes relative to pure LLM. All metrics defined in `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric                              | Function                                                                   | analysis-bases.md ref |
|-------------------------------------|----------------------------------------------------------------------------|-----------------------|
| BAI (Bubble Amplitude Index)        | `bubble_amplitude_index(price_history, fundamental)`                       | §2.1                  |
| BD (Bubble Duration)                | `bubble_duration(price_history, fundamental, bubble_threshold=0.10)`       | §2.2                  |
| CS (Crash Severity)                 | `crash_severity(price_history)`                                            | §2.3                  |
| MAF (Momentum Amplification Factor) | `momentum_amplification_factor(agent_volume_by_type, bubble_rounds)`       | §2.4                  |
| SSR (Short Squeeze Resistance)      | `short_squeeze_resistance(short_seller_orders, momentum_sign_history)`     | §2.5                  |
| RT (Recovery Time)                  | `recovery_time(price_history, fundamental, recovery_threshold=0.10)`       | §2.6                  |
| WDI (Wealth Divergence Index)       | `wealth_divergence_index(agent_final_states, final_price, initial_wealth)` | §2.7                  |

## §3 Rag-Variant-Specific Notes

- **RAG moderation on BAI**: If `RagLLMNewEconomyEvangelist` retrieves 2000–2001 crash evidence, BAI may be lower than LLM baseline; measure mean BAI across 3 runs to confirm moderation effect.
- **BD shortening**: Historical crash case retrieval typically triggers earlier selling; BD should be ≤ LLM BD. Compare using `bubble_duration()` with same threshold=0.10.
- **SSR improvement**: `RagLLMShortSeller` SSR expected higher than LLM — synchronisation-risk literature reinforces cover delay. Report SSR difference vs. LLM/analysis.md §4.
- **MAF variance**: `RagLLMMomentumFollower` may show lower MAF if momentum crash studies are retrieved — document retrieval frequency and correlation with MAF suppression.
- **Knowledge coverage check**: If retrieved context is empty (`"No relevant knowledge retrieved this round"`), Rag variant degrades to LLM variant for that round; log retrieval rate and annotate rounds with no retrieval.

## §4 Expected Ranges

| Metric | Rag-Variant Expected Range | vs. LLM Baseline                                           |
|--------|----------------------------|------------------------------------------------------------|
| BAI    | 0.35 – 1.5                 | Lower mean; moderation effect if crash docs retrieved      |
| BD     | 15 – 48 rounds             | Shorter; historical evidence triggers earlier exits        |
| CS     | 0.35 – 0.70                | Similar; crash may be gentler if exit is earlier           |
| MAF    | 0.25 – 0.60                | Lower when momentum-crash docs retrieved                   |
| SSR    | 0.30 – 0.60                | Higher than LLM; knowledge reinforces short persistence    |
| RT     | 8 – 30 rounds              | Shorter; historical recovery patterns inform quicker reset |
| WDI    | −0.2 – +0.4                | Better stabilising-agent outcomes vs. LLM                  |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.

## §6 Cross-Variant Comparison

| Comparison | Interpretation |
|---|---|
| Rag vs RuleLLM | Measures the marginal effect of retrieved bubble/crash context. |
| Rag vs LLM | Separates persona-only narrative behavior from knowledge-augmented behavior. |
| Rag vs Rule | Tests whether RAG knowledge improves or weakens baseline mechanism emergence. |

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Confirm RAG assets and embedding configuration were available.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Audit parse failures, retry counts, fallback holds, and retrieval-health records before acceptance.
