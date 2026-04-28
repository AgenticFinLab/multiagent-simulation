# GamblerFallacy — RuleLLM Variant Analysis

## §1 Overview

Analysis for the **RuleLLM variant** of GamblerFallacy. Metric definitions from `../analysis-bases.md §2`. Expected near-Rule baseline due to embedded thresholds.

| Aspect         | Detail                 |
|----------------|------------------------|
| Variant        | RuleLLM                |
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

## §3 RuleLLM-Specific Notes

- **Near-Rule behavior**: Embedded rules maintain same activation logic as Rule; LLM adds quantity variation only. GFI, SAR, HHM should closely track Rule baseline.
- **SAR may deviate slightly**: LLM quantity modulation based on perceived streak length creates partial differentiation between §4.1 and §4.2 even with same direction logic.
- **Research value**: RuleLLM vs. LLM isolates rule-constraint effect. RuleLLM vs. Rule isolates LLM-reasoning effect with rules held constant.

---

## §4 Expected Ranges (RuleLLM Variant)

| Metric | RuleLLM Expected Range | vs. Rule Baseline          | Interpretation                               |
|--------|------------------------|----------------------------|----------------------------------------------|
| GFI    | 0.02–0.08              | ≈ Rule                     | Embedded threshold anchors to Rule level     |
| SAR    | 0.8–1.2                | ≈ Rule (±0.2 LLM variance) | Slight quantity asymmetry from LLM reasoning |
| HHM    | 140–480 shares         | ≈ Rule                     | Near-identical demand magnitude              |
| ACI    | 0.35–0.65              | ≈ Rule                     | Same correction efficiency                   |
| VAF    | 1.4–3.3                | ≈ Rule                     | Marginal dampening from LLM                  |
| WDI    | 0.09–0.33              | ≈ Rule                     | Near-identical wealth distribution           |
