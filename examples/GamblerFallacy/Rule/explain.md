# GamblerFallacy — Rule Variant

## §1 Overview

The Rule variant implements the Gambler's Fallacy simulation using deterministic threshold-based rules from `simulation-bases.md §4`. Each investor applies fixed conditions on price deviation to generate the two competing biases: the Gambler's Fallacy (StreakReversalTrader §4.1 — expects reversal) and the Hot Hand Fallacy (HotHandTrader §4.2 — expects continuation). Both are implemented as momentum-following at default extras; differentiation requires non-default `streak_threshold`/`hot_streak_threshold` calibration.

| Aspect             | Detail                                             |
|--------------------|----------------------------------------------------|
| Variant            | Rule                                               |
| Simulation         | GamblerFallacy                                     |
| Decision Mechanism | Threshold rules on deviation δ(t) = (P(t) − F) / F |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`       |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)   |

---

## §2 Theory → Implementation Mapping

### §2.1 StreakReversalTrader (`simulation-bases.md §4.1`)

| Theory Component                                 | Implementation                                                                                                                         |
|--------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Law of small numbers (Tversky & Kahneman, 1971)  | `if abs(deviation) > 0.02: qty = min(800, int(abs(deviation) * 5000))`                                                                 |
| Gambler's fallacy: expects reversal after streak | At default extras: `if deviation > 0: buy` (paradoxically buys on upward deviation, expecting this streak to continue before reversal) |
| Streak continuation bias                         | `if deviation < 0: sell` — sells into downward streaks expecting further reversal                                                      |
| Position cap                                     | 800 shares max; `int(cash/price)` buy constraint; `max(position, 0)` sell constraint                                                   |

**Note**: At default extras, StreakReversalTrader and HotHandTrader have identical logic — both buy when deviation > 0. The gambler's fallacy (betting on reversal) requires non-default `reversal_bias`/`continuation_bias` extras to activate the opposing direction logic. At default, both are destabilizing momentum followers.

### §2.2 HotHandTrader (`simulation-bases.md §4.2`)

| Theory Component                         | Implementation                                                                                                      |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Hot hand fallacy (Gilovich et al., 1985) | `if abs(deviation) > 0.02: qty = min(800, int(abs(deviation) * 5000))`                                              |
| Streak continuation: buys winners        | `if deviation > 0: buy` — buys on positive deviation expecting hot streak to continue                               |
| Streak abandonment                       | `if deviation < 0: sell` — sells on negative deviation                                                              |
| Identical to §4.1 at default             | Both biases produce the same momentum-following behavior at default extras; GFI captures this as expected SAR = 1.0 |

### §2.3 IndependentAssessor (`simulation-bases.md §4.3`)

| Theory Component                                | Implementation                                                                          |
|-------------------------------------------------|-----------------------------------------------------------------------------------------|
| Independence of sequential events (Rabin, 2002) | `if abs(deviation) > 0.05: qty = min(500, int(abs(deviation) * 3000))`                  |
| Contrarian mean reversion                       | `if deviation < 0: buy` (buys undervalued); `if deviation > 0: sell` (sells overvalued) |
| Higher activation threshold                     | 0.05 > 0.02; rational agent waits for statistically meaningful deviation signal         |
| Smaller position cap                            | 500 shares (vs. 800 for biased agents); Shleifer & Vishny (1997) limits to arbitrage    |

### §2.4 Arbitrageur (`simulation-bases.md §4.4`)

| Theory Component                              | Implementation                                                                         |
|-----------------------------------------------|----------------------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | `if abs(deviation) > 0.05: qty = min(500, int(abs(deviation) * 3000))`                 |
| Exploit streak-based mispricing               | `if deviation < 0: buy`; `if deviation > 0: sell` — identical contrarian logic to §4.3 |
| Combined correction force                     | §4.3 + §4.4 together provide 2× rational correction pressure at same threshold         |

### §2.5 NoiseTrader (`simulation-bases.md §4.5`)

| Theory Component                 | Implementation                                        |
|----------------------------------|-------------------------------------------------------|
| Noise trader model (Black, 1986) | `if random.random() < trade_probability (0.3): trade` |
| Random direction                 | `action = "buy" if random.random() > 0.5 else "sell"` |
| Random quantity                  | `qty = random.randint(100, 500)`                      |

---

## §3 Rule-Specific Notes

- **Default extras SAR = 1.0**: At default calibration, StreakReversalTrader and HotHandTrader have exactly identical logic — Streak Asymmetry Ratio = 1.0 is expected, not a bug. Differentiation requires non-default `reversal_bias`/`continuation_bias` parameters.
- **Activation gap**: Biased agents at |δ| > 0.02; rational agents at |δ| > 0.05 — same asymmetric structure as FramingEffect.
- **Hot Hand Momentum**: Even with identical direction logic, combined biased agents produce strong demand at |δ| > 0.02, captured by HHM metric.

---

## §4 Expected Ranges (Rule Variant)

| Metric                                | Rule Expected Range     | Interpretation                                                       |
|---------------------------------------|-------------------------|----------------------------------------------------------------------|
| GFI (Gambler's Fallacy Index)         | 0.02–0.08               | Mean absolute deviation; both biased agents amplify deviation        |
| SAR (Streak Asymmetry Ratio)          | ≈ 1.0 at default extras | Equal positive/negative deviation mean; both biased agents symmetric |
| HHM (Hot Hand Momentum)               | 150–500 shares/round    | Mean demand magnitude during                                         |
| ACI (Arbitrage Correction Index)      | 0.35–0.65               | Fraction of large deviations corrected 50% within 5 rounds           |
| VAF (Volatility Amplification Factor) | 1.5–3.5                 | Biased-active rounds 1.5–3.5× more volatile than quiet rounds        |
| WDI (Wealth Distribution Index)       | 0.10–0.35               | Moderate inequality; rational agents outperform biased agents        |
