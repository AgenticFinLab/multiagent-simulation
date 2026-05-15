# FramingEffect — LLM Variant Analysis

## §1 Overview

Analysis methodology for the **LLM variant** of the FramingEffect simulation. Metric definitions from `../analysis-bases.md §2`. This file documents LLM-specific behavioral expectations and expected metric ranges relative to the Rule baseline.

| Aspect             | Detail                 |
|--------------------|------------------------|
| Variant            | LLM                    |
| Simulation         | FramingEffect          |
| Analysis basis     | `../analysis-bases.md` |
| Decision mechanism | LLM persona reasoning  |

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

## §3 LLM-Specific Notes

- **LLMGainFrameFollower (§4.1)**: LLM may express bias more contextually — e.g., buy on gain framing only when prior trend is established, not mechanically at every |δ| > 0.02. FDI may be lower as a result.
- **LLMLossFrameReactor (§4.2)**: Unlike Rule, LLM can produce distinct gain vs. loss response asymmetry. Expect ACC split to differ from 50/50 Rule baseline.
- **LLMFrameInvariantTrader (§4.3)**: May reason about framing explicitly in `<analysis>` tag; qualitative analysis of reasoning available in output. VAF dampened by more sophisticated contrarian reasoning.
- **LLMArbitrageFramer (§4.4)**: Can contextualise arbitrage opportunity in narrative terms; may identify more complex mispricing patterns than Rule threshold.
- **LLMNoiseTrader (§4.5)**: LLM noise traders may exhibit mood-consistent sequences (e.g., several buys then several sells) rather than pure random alternation, slightly affecting FPI.
- **Run averaging**: Run 10+ seeds and average all metrics; LLM stochasticity makes single-run results unreliable.

---

## §4 Expected Ranges (LLM Variant)

| Metric          | LLM Expected Range | vs. Rule Baseline         | Interpretation                                                                 |
|-----------------|--------------------|---------------------------|--------------------------------------------------------------------------------|
| FDI             | 0.015–0.07         | Lower (−15 to −25%)       | LLM moderation of extreme bias; persona reasoning softens systematic deviation |
| FPI             | 2–10 rounds        | Shorter (−1 to −3 rounds) | LLM occasionally breaks cascade through reasoning                              |
| ACC (§4.1+§4.2) | 40–65%             | Lower (−5 to −15%)        | LLM biased agents less mechanically consistent                                 |
| VAF             | 1.2–3.0            | Lower (−0.5 range)        | LLM variability reduces systematic volatility amplification                    |
| OWP             | 0.03–0.18          | Lower                     | LLM sometimes avoids losing trades through contextual reasoning                |
| WDI             | 0.08–0.25          | Lower                     | Less systematic wealth redistribution than deterministic Rule                  |
