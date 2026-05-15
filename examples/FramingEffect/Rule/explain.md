# FramingEffect — Rule Variant

## §1 Overview

The Rule variant implements the Framing Effect simulation using deterministic threshold-based rules derived directly from `simulation-bases.md §4`. Each investor class applies fixed mathematical conditions — activation thresholds, quantity formulas, and direction logic — compiled from `Rule/players.py`. The framing effect emerges from the interaction between momentum-following biased agents (§4.1, §4.2) and contrarian rational agents (§4.3, §4.4), mediated by the standard Walrasian price formation mechanism.

| Aspect             | Detail                                             |
|--------------------|----------------------------------------------------|
| Variant            | Rule                                               |
| Simulation         | FramingEffect                                      |
| Decision Mechanism | Threshold rules on deviation δ(t) = (P(t) − F) / F |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`       |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)   |

---

## §2 Theory → Implementation Mapping

### §2.1 GainFrameFollower (`simulation-bases.md §4.1`)

| Theory Component                                        | Implementation                                                                         |
|---------------------------------------------------------|----------------------------------------------------------------------------------------|
| Prospect theory gain framing (Tversky & Kahneman, 1981) | `if abs(deviation) > 0.02: qty = min(800, int(abs(deviation) * 5000))`                 |
| Momentum following on gain frame                        | `if deviation > 0: buy qty shares` (treats positive deviation as "gain frame" signal)  |
| Panic-sell on perceived loss                            | `if deviation < 0: sell qty shares` (treats negative deviation as "loss frame" threat) |
| Position cap (limits to arbitrage)                      | `max(position, 0)` sell constraint; `int(cash / price)` buy constraint                 |

### §2.2 LossFrameReactor (`simulation-bases.md §4.2`)

| Theory Component                                        | Implementation                                                                                              |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Prospect theory loss framing (Tversky & Kahneman, 1981) | `if abs(deviation) > 0.02: qty = min(800, int(abs(deviation) * 5000))`                                      |
| Risk-seeking on loss frame                              | Same direction logic as §4.1 at default extras; differentiation via `loss_weight`/`gain_weight` calibration |
| Deviation-proportional sizing                           | `qty = min(800, int(abs(deviation) * 5000))` — larger deviations → larger trades                            |

**Note**: At default extras, §4.1 and §4.2 have identical code logic. Differentiation is achieved through non-default `gain_weight`/`loss_weight` extras calibration that affects perceived deviation magnitude.

### §2.3 FrameInvariantTrader (`simulation-bases.md §4.3`)

| Theory Component                                 | Implementation                                                                          |
|--------------------------------------------------|-----------------------------------------------------------------------------------------|
| Frame-invariant rationality (Levin et al., 1998) | `if abs(deviation) > 0.05: qty = min(500, int(abs(deviation) * 3000))`                  |
| Contrarian mean reversion                        | `if deviation < 0: buy` (buys undervalued), `if deviation > 0: sell` (sells overvalued) |
| Stronger activation threshold                    | Threshold 0.05 > 0.02 (§4.1); rational agent waits for larger mispricing signal         |
| Smaller max position                             | 500 shares cap vs. 800 for biased agents (Limits to Arbitrage, Shleifer & Vishny, 1997) |

### §2.4 ArbitrageFramer (`simulation-bases.md §4.4`)

| Theory Component                      | Implementation                                                                           |
|---------------------------------------|------------------------------------------------------------------------------------------|
| Framing arbitrage (Kuhberger, 1998)   | `if abs(deviation) > 0.05: qty = min(500, int(abs(deviation) * 3000))`                   |
| Exploit framing-induced mispricing    | `if deviation < 0: buy`; `if deviation > 0: sell` (identical contrarian logic to §4.3)   |
| Position cap matching rational agents | 500 shares cap; same as FrameInvariantTrader (both represent rational correction forces) |

**Note**: §4.3 and §4.4 have identical logic at default extras, representing two independent rational agents providing double the correction pressure against framing-biased agents.

### §2.5 NoiseTrader (`simulation-bases.md §4.5`)

| Theory Component                 | Implementation                                                               |
|----------------------------------|------------------------------------------------------------------------------|
| Noise trader model (Black, 1986) | `if random.random() < trade_probability (0.3): trade`                        |
| Random direction and size        | `action = "buy" if random.random() > 0.5 else "sell"`                        |
| Random quantity                  | `qty = random.randint(100, 500)` — uniform draw regardless of market state   |
| Position constraints             | `min(qty, int(cash/price))` for buys; `min(qty, max(position, 0))` for sells |

---

## §3 Rule-Specific Notes

- **Activation asymmetry**: Biased agents (§4.1, §4.2) activate at |δ| > 0.02; rational agents (§4.3, §4.4) activate at |δ| > 0.05. This 2.5× threshold gap means biased agents always move first, creating the deviation that rational agents later correct.
- **Sizing formula**: All active agents use `qty = min(cap, int(|δ| × scale))` where biased agents have (cap=800, scale=5000) and rational agents have (cap=500, scale=3000). At δ = 0.10: biased trade 500 shares, rational trade 300 shares — net demand ≈ +200 per biased agent.
- **Market broadcast**: All agents receive `price`, `fundamental`, `deviation`, `round` per round. Investors use `deviation` directly from broadcast (not recomputed).
- **No memory**: All 5 investor classes are memoryless (no persistent state beyond cash/position). Decision depends only on current-round deviation.

---

## §4 Expected Ranges (Rule Variant)

| Metric                                | Rule Expected Range                  | Interpretation                                                              |
|---------------------------------------|--------------------------------------|-----------------------------------------------------------------------------|
| FDI (Framing Deviation Index)         | 0.02–0.08                            | Mean absolute deviation; framing amplifies deviation 2–8% above fundamental |
| FPI (Framing Persistence Index)       | 3–12 rounds                          | Consecutive rounds of                                                       |
| ACC (Agent Contribution Coefficient)  | §4.1+§4.2: 50–70%; §4.3+§4.4: 20–40% | Biased agents dominate cascade volume                                       |
| VAF (Volatility Amplification Factor) | 1.5–3.5                              | Framing-active rounds 1.5–3.5× more volatile than quiet rounds              |
| OWP (Overconfidence Wealth Penalty)   | 0.05–0.20                            | Biased agents lose 5–20% of initial wealth vs. rational agents              |
| WDI (Wealth Distribution Index)       | 0.10–0.30                            | Moderate inequality; rational agents outperform biased agents               |
