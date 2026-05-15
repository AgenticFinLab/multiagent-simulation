# GamblerFallacy — Rag Variant Analysis

## §1 Overview

Analysis for the **Rag variant** of GamblerFallacy. Metric definitions from `../analysis-bases.md §2`. Key distinction: RAG retrieval reinforces opposite biases for §4.1 and §4.2, potentially producing SAR divergence similar to LLM but grounded in retrieved empirical evidence.

| Aspect         | Detail                 |
|----------------|------------------------|
| Variant        | Rag                    |
| Simulation     | GamblerFallacy         |
| Analysis basis | `../analysis-bases.md` |

---

## §2 Metric → Function Mapping

| Metric | Function                                                                           | analysis-bases.md ref |
|--------|------------------------------------------------------------------------------------|-----------------------|
| GFI    | `gambler_fallacy_index(price_history, fundamental)`                                | §2.1                  |
| SAR    | `streak_asymmetry_ratio(price_history, fundamental)`                               | §2.2                  |
| HHM    | `hot_hand_momentum(trade_history, price_history, fundamental, threshold=0.02)`     | §2.3                  |
| ACI    | `arbitrage_correction_index(price_history, fundamental, threshold=0.05, window=5)` | §2.4                  |
| VAF    | `volatility_amplification_factor(price_history, fundamental, threshold=0.02)`      | §2.5                  |
| WDI    | `wealth_distribution_index(agent_states, final_price)`                             | §2.6                  |

---

## §3 Rag-Specific Notes

- **RagLLMStreakReversalTrader (§4.1)**: Retrieved gambler's fallacy evidence (casino data, psychological studies) reinforces reversal expectation. If RAG corpus contains hot hand evidence, partial moderation occurs.
- **RagLLMHotHandTrader (§4.2)**: Retrieved momentum studies reinforce continuation expectation. Different retrieval corpus from §4.1 creates empirically grounded differentiation.
- **SAR divergence**: Rag expected to produce SAR furthest from 1.0 among all variants when retrieval corpora are well-differentiated.
- **Corpus quality dependency**: All metrics depend on retrieval corpus quality — poor corpus makes Rag resemble LLM.
- **ACI in Rag**: Rational agents (§4.3, §4.4) retrieve mean-reversion evidence, potentially making ACI slightly higher than Rule.

---

## §4 Expected Ranges (Rag Variant)

| Metric | Rag Expected Range | vs. Rule Baseline                    | Interpretation                                            |
|--------|--------------------|--------------------------------------|-----------------------------------------------------------|
| GFI    | 0.018–0.08         | Similar/slightly lower               | Opposing retrieval effects partially cancel net deviation |
| SAR    | 0.4–2.0            | More variable (wider range than LLM) | Retrieval corpora reinforce opposite biases empirically   |
| HHM    | 120–450 shares     | Slightly lower                       | Partial cancellation of opposing biases                   |
| ACI    | 0.35–0.70          | Similar/slightly higher              | Retrieved mean-reversion evidence aids rational agents    |
| VAF    | 1.3–3.2            | Slightly lower                       | Net bias effect reduced by opposing reinforcement         |
| WDI    | 0.08–0.30          | Slightly lower                       | Less systematic redistribution when biases oppose         |
