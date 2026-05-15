# GamblerFallacy — LLM Variant Analysis

## §1 Overview

Analysis methodology for the **LLM variant** of the GamblerFallacy simulation. Metric definitions from `../analysis-bases.md §2`. The key LLM-specific finding: SAR should diverge from 1.0 as LLM agents express genuinely opposing gambler's fallacy vs. hot hand biases.

| Aspect             | Detail                 |
|--------------------|------------------------|
| Variant            | LLM                    |
| Simulation         | GamblerFallacy         |
| Analysis basis     | `../analysis-bases.md` |
| Decision mechanism | LLM persona reasoning  |

---

## §2 Metric → Function Mapping

| Metric                                | Function                                                                           | analysis-bases.md ref |
|---------------------------------------|------------------------------------------------------------------------------------|-----------------------|
| GFI (Gambler's Fallacy Index)         | `gambler_fallacy_index(price_history, fundamental)`                                | §2.1                  |
| SAR (Streak Asymmetry Ratio)          | `streak_asymmetry_ratio(price_history, fundamental)`                               | §2.2                  |
| HHM (Hot Hand Momentum)               | `hot_hand_momentum(trade_history, price_history, fundamental, threshold=0.02)`     | §2.3                  |
| ACI (Arbitrage Correction Index)      | `arbitrage_correction_index(price_history, fundamental, threshold=0.05, window=5)` | §2.4                  |
| VAF (Volatility Amplification Factor) | `volatility_amplification_factor(price_history, fundamental, threshold=0.02)`      | §2.5                  |
| WDI (Wealth Distribution Index)       | `wealth_distribution_index(agent_states, final_price)`                             | §2.6                  |

---

## §3 LLM-Specific Notes

- **LLMStreakReversalTrader (§4.1)**: Prompt-encoded reversal bias may produce SAR < 1.0 (positive deviations smaller than negative) when the reversal belief is strong enough to dampen upward momentum.
- **LLMHotHandTrader (§4.2)**: Momentum-continuation persona may produce SAR > 1.0 (positive deviations larger). The interplay between §4.1 (SAR↓) and §4.2 (SAR↑) is the core LLM research finding.
- **SAR diagnostic**: If SAR ≈ 1.0 in LLM variant, the LLM personas are not successfully differentiating the two biases — examine system prompts for sufficient asymmetry.
- **HHM in LLM**: When §4.1 and §4.2 trade in opposite directions, net demand (HHM numerator) is reduced vs. Rule baseline where both agents trade in the same direction.
- **Multi-run**: Run ≥10 seeds; SAR is highly variable across runs due to LLM stochasticity.

---

## §4 Expected Ranges (LLM Variant)

| Metric | LLM Expected Range | vs. Rule Baseline            | Interpretation                                                         |
|--------|--------------------|------------------------------|------------------------------------------------------------------------|
| GFI    | 0.015–0.07         | Lower                        | Opposing biases partially cancel net deviation                         |
| SAR    | 0.5–1.8            | More variable than Rule ≈1.0 | Key LLM differentiation: §4.1 reversal vs. §4.2 continuation expressed |
| HHM    | 100–400 shares     | Lower                        | Partial cancellation of biased agent demands                           |
| ACI    | 0.35–0.70          | Similar/slightly higher      | LLM rational agents reason explicitly about correction                 |
| VAF    | 1.2–3.0            | Lower                        | Dampened by opposing bias cancellation                                 |
| WDI    | 0.08–0.28          | Lower                        | Less systematic exploitation when biases oppose each other             |
