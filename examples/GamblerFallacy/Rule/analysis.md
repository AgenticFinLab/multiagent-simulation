# GamblerFallacy — Rule Variant Analysis

## §1 Overview

Analysis methodology for the **Rule variant** of the GamblerFallacy simulation. All metric definitions sourced from `../analysis-bases.md §2`.

| Aspect             | Detail                  |
|--------------------|-------------------------|
| Variant            | Rule                    |
| Simulation         | GamblerFallacy          |
| Analysis basis     | `../analysis-bases.md`  |
| Decision mechanism | Threshold rules on δ(t) |

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

## §3 Rule-Specific Notes

- **StreakReversalTrader (§4.1)**: At default extras, buys on positive deviation — momentum follower despite the gambler's fallacy label. GFI reflects this amplifying behavior. SAR = 1.0 at default.
- **HotHandTrader (§4.2)**: Identical logic to §4.1 at default. Combined, §4.1+§4.2 provide 2× amplification at |δ| > 0.02. HHM captures this combined demand.
- **IndependentAssessor (§4.3)**: Contrarian at |δ| > 0.05; deterministically corrects deviations. ACI measures its correction efficiency combined with §4.4.
- **Arbitrageur (§4.4)**: Identical contrarian logic to §4.3; combined they produce ACI correction in 35–65% of large deviation episodes.
- **NoiseTrader (§4.5)**: Contributes ≈15–20% of background volume; random direction does not systematically affect GFI or SAR.
- **SAR interpretation**: SAR = 1.0 at default means positive and negative deviation means are equal — confirming symmetric biased agent behavior. SAR ≠ 1.0 at non-default calibration isolates gambler's fallacy from hot hand effects.

---

## §4 Expected Ranges (Rule Variant)

| Metric | Rule Expected Range | vs. Calibration Target        | Interpretation                                                  |
|--------|---------------------|-------------------------------|-----------------------------------------------------------------|
| GFI    | 0.02–0.08           | Target: 0.02–0.08             | Mean deviation; biased agents amplify price deviations          |
| SAR    | ≈ 1.0 (default)     | Target: 0.7–1.5 (non-default) | Symmetric at default; asymmetric after extras calibration       |
| HHM    | 150–500 shares      | Target: 150–500               | Biased agent demand during streak episodes                      |
| ACI    | 0.35–0.65           | Target: 0.35–0.65             | 35–65% of large deviations corrected by rational agents         |
| VAF    | 1.5–3.5             | Target: 1.5–3.5               | Streak episodes amplify volatility                              |
| WDI    | 0.10–0.35           | Target: 0.10–0.35             | Rational agents accumulate wealth advantage over biased traders |
