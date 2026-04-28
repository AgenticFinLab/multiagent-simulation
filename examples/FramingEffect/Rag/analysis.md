# FramingEffect — Rag Variant Analysis

## §1 Overview

Analysis methodology for the **Rag variant** of the FramingEffect simulation. Metric definitions from `../analysis-bases.md §2`. Rag is expected to show slightly higher bias amplification than Rule due to retrieved documents reinforcing framing-consistent behavior.

| Aspect             | Detail                 |
|--------------------|------------------------|
| Variant            | Rag                    |
| Simulation         | FramingEffect          |
| Analysis basis     | `../analysis-bases.md` |
| Decision mechanism | RAG-augmented LLM      |

---

## §2 Metric → Function Mapping

| Metric                                | Function                                                                      | analysis-bases.md ref |
|---------------------------------------|-------------------------------------------------------------------------------|-----------------------|
| FDI (Framing Deviation Index)         | `framing_deviation_index(price_history, fundamental)`                         | §2.1                  |
| FPI (Framing Persistence Index)       | `framing_persistence_index(price_history, fundamental, threshold=0.02)`       | §2.2                  |
| ACC (Agent Contribution Coefficient)  | `agent_contribution_coefficient(trade_history, price_history, fundamental)`   | §2.3                  |
| VAF (Volatility Amplification Factor) | `volatility_amplification_factor(price_history, fundamental, threshold=0.02)` | §2.4                  |
| OWP (Overconfidence Wealth Penalty)   | `overconfidence_wealth_penalty(agent_states, final_price)`                    | §2.5                  |
| WDI (Wealth Distribution Index)       | `wealth_distribution_index(agent_states, final_price)`                        | §2.6                  |

---

## §3 Rag-Specific Notes

- **RagLLMGainFrameFollower (§4.1)**: Retrieved framing studies typically confirm bias; FDI contribution from this agent expected to be higher than LLM variant. Retrieval of crash evidence can produce sudden position reversal.
- **RagLLMLossFrameReactor (§4.2)**: Different retrieval corpus (loss-framing studies, panic-selling episodes) creates empirically grounded differentiation from §4.1 — a key Rag advantage over Rule/LLM variants.
- **RagLLMFrameInvariantTrader (§4.3)**: Retrieval of mean-reversion evidence strengthens contrarian conviction; ACC for rational agents may be slightly higher than Rule baseline.
- **RagLLMArbitrageFramer (§4.4)**: Historical arbitrage correction timelines from retrieval may lead to earlier or more precise contrarian entries.
- **RagLLMNoiseTrader (§4.5)**: Partial information from retrieved news may introduce slight systematic bias in nominally random trading.
- **Corpus quality**: All Rag metrics depend on retrieval corpus quality; run retrieval audit before interpreting cross-variant comparisons.

---

## §4 Expected Ranges (Rag Variant)

| Metric          | Rag Expected Range | vs. Rule Baseline                 | Interpretation                                                     |
|-----------------|--------------------|-----------------------------------|--------------------------------------------------------------------|
| FDI             | 0.02–0.09          | Slightly higher (+5 to +15%)      | Retrieved framing evidence reinforces biased agent deviations      |
| FPI             | 3–13 rounds        | Slightly longer (+0 to +2 rounds) | Retrieval reinforces cascade persistence                           |
| ACC (§4.1+§4.2) | 50–72%             | Slightly higher (+0 to +5%)       | Retrieval amplifies biased agent volume                            |
| VAF             | 1.5–3.8            | Slightly higher                   | Retrieval-reinforced biases create slightly more excess volatility |
| OWP             | 0.05–0.22          | Slightly higher                   | Biased agents lose slightly more due to reinforced errors          |
| WDI             | 0.10–0.32          | Slightly higher                   | Slightly more inequality due to stronger retrieval-driven bias     |
