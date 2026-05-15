# AvailabilityBias Rule — Implementation Explanation

## Overview

| Item                                   | Description                                                                                                                                                |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rule (deterministic baseline)                                                                                                                              |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                   |
| **Decision Logic**                     | Fixed formulas — all thresholds and parameters loaded from config; no LLM calls                                                                            |
| **Key Difference from Other Variants** | Fully deterministic; recency and media channels are exact algebraic formulas with no stochastic LLM component                                              |
| **Primary Research Contribution**      | Establish the deterministic baseline: do mechanical availability bias formulas alone reproduce the recency/media-driven overreaction and partial recovery? |

---

## 1. How Theoretical Design Is Implemented

### RecentEventOverweighter: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — RecentEventOverweighter)*

| Theoretical Design Element                                                  | Implementation                                                                                                                       |
|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Availability heuristic recency channel → simulation-bases.md §2.1           | Class docstring cites Tversky & Kahneman (1973); `players.py RecentEventOverweighter`                                                |
| Uses `return_pct` from broadcast → sim-bases §3.3                           | `return_pct = market_data["return_pct"]` — unique to AvailabilityBias broadcast                                                      |
| perceived_signal = recency_weight × return_pct + (1 − recency_weight) × dev | `perceived_signal = recency_weight * return_pct + (1 - recency_weight) * deviation`                                                  |
| recency_weight = 3.0, salience_threshold = 0.05 → sim-bases §6              | `recency_weight = float(extras["recency_weight"])` and `salience_threshold = float(extras["salience_threshold"])` from `players.yml` |
| Buy when perceived_signal > threshold → sim-bases §4                        | `if perceived_signal > salience_threshold: buy order_size`                                                                           |
| Sell when perceived_signal < −threshold → sim-bases §4                      | `elif perceived_signal < -salience_threshold: sell order_size`                                                                       |

### MediaInfluencedTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — MediaInfluencedTrader)*

| Theoretical Design Element                                              | Implementation                                                                                   |
|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Media-driven availability channel → simulation-bases.md §2.2            | Class docstring cites Schwarz et al. (1991); Tetlock (2007); `players.py MediaInfluencedTrader`  |
| amplified_signal = media_weight × deviation × social_amplification → §4 | `amplified_signal = media_weight * deviation * social_amplification`                             |
| media_weight = 2.0, social_amplification = 1.5 → sim-bases §6           | Both loaded via `extras["media_weight"]` and `extras["social_amplification"]` from `players.yml` |
| Trade when                                                              | amplified_signal                                                                                 |

### SystematicAnalyst: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — SystematicAnalyst)*

| Theoretical Design Element                                         | Implementation                                                                                 |
|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Bayesian rational processing → simulation-bases.md §2.3            | Class docstring cites Mullainathan (2002); `players.py SystematicAnalyst`                      |
| Uses only deviation (no recency or media weighting) → sim-bases §4 | `deviation = market_data["deviation"]` — does NOT use `return_pct`                             |
| evidence_threshold = 0.03 → sim-bases §6                           | `evidence_threshold = float(extras["evidence_threshold"])` from `players.yml`                  |
| Stabilizing counter-trade → sim-bases §4                           | `if deviation > evidence_threshold: sell order_size` (fades overvaluation); buy if undervalued |

### ValueTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ValueTrader)*

| Theoretical Design Element                                     | Implementation                                                                           |
|----------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Value investing discipline → simulation-bases.md §2.4          | Class docstring cites Graham (1949); Baker & Wurgler (2007); `players.py ValueTrader`    |
| Trade at significant deviation threshold = 0.10 → sim-bases §6 | `deviation_threshold = float(extras["deviation_threshold"])` (= 0.10) from `players.yml` |
| Buy when deeply undervalued → sim-bases §4                     | `if deviation < -deviation_threshold: buy min(position_size, cash / price)`              |
| Sell when significantly overvalued → sim-bases §4              | `elif deviation > deviation_threshold: sell min(position_size, position)`                |

### NoiseTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — NoiseTrader)*

| Theoretical Design Element                             | Implementation                                                                                                    |
|--------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Random uninformed trading → simulation-bases.md §4     | Class docstring cites Black (1986); `players.py NoiseTrader`                                                      |
| Trade probability = 0.30 → sim-bases §6                | `if random.random() < trade_probability:` where `trade_probability = float(extras["trade_probability"])` (= 0.30) |
| Quantity uniform [min_order, max_order] → sim-bases §6 | `qty = random.randint(100, 500)`; constrained by cash/position                                                    |
| Random direction → sim-bases §4                        | `if random.random() > 0.5: action = "buy" else: action = "sell"`                                                  |

---

## 2. Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market.perceive()` (inline computation after order collection)

Code translation:

| sim-bases variable   | Python variable                      | Config path                        | Value |
|----------------------|--------------------------------------|------------------------------------|-------|
| `λ` (price_impact)   | `price_impact`                       | `extras["price_impact"]`           | 0.01  |
| `γ` (mean_reversion) | `mean_reversion`                     | `extras["mean_reversion"]`         | 0.02  |
| `F` (fundamental)    | `fundamental`                        | `extras["fundamental_value"]`      | 100.0 |
| `D(t)` (net demand)  | `net_demand = buy_qty − sell_qty`    | computed from orders               | —     |
| `ε(t)` (noise)       | `noise = random.gauss(0, noise_std)` | `extras["noise_std"]`              | 0.5   |
| `P(t)` (current)     | `current_price`                      | `self.state.custom_state["price"]` | —     |

Price floor: `new_price = max(new_price, 0.01)` — prevents negative prices.

**Unique broadcast**: Unlike all other simulations, Market broadcasts both `return_pct` and `prev_price` in addition to `price`, `fundamental`, `deviation`, and `round`. This enables RecentEventOverweighter to use the recency channel.

Deviations from simulation-bases.md design: None.

---

## 3. Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rule variant entry)*

**Two availability channels**: The Rule variant encodes both availability channels as exact algebraic formulas:
1. **Recency channel** (RecentEventOverweighter): `perceived_signal = 3.0 × return_pct − 2.0 × deviation`
2. **Media channel** (MediaInfluencedTrader): `amplified_signal = 2.0 × deviation × 1.5 = 3.0 × deviation`

**Fully deterministic channels**: Given the same noise seed, both availability distortions are exactly reproducible, establishing the baseline for how much distortion the LLM and Rag variants reproduce.

**SystematicAnalyst independence from recency**: SystematicAnalyst is the only agent that deliberately ignores `return_pct`, using only `deviation`. This is the baseline stabilizer that corrects availability-biased pricing through pure fundamental analysis.

---

## 4. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market.perceive()                                                    ║
║    ├── buy_qty = Σ buy orders; sell_qty = Σ sell orders              ║
║    ├── P(t+1) = P(t) + 0.01×D + 0.02×(100−P) + N(0, 0.5²)         ║
║    ├── return_pct = (P(t+1) − P(t)) / P(t)                          ║
║    └── deviation = (P(t+1) − 100) / 100                              ║
║                                                                       ║
║  Market.decide() → broadcast {price, prev_price, fundamental,        ║
║                               deviation, return_pct, round}          ║
║                                                                       ║
║  RecentEventOverweighter: perceived_signal = 3.0×return_pct − 2.0×dev║
║    → buy if perceived_signal > 0.05; sell if < −0.05                 ║
║  MediaInfluencedTrader:   amplified_signal = 3.0 × deviation          ║
║    → buy if amplified_signal > threshold; sell if < −threshold       ║
║  SystematicAnalyst:       evidence = deviation (no recency)           ║
║    → sell if deviation > 0.03; buy if deviation < −0.03              ║
║  ValueTrader:             trade if |deviation| > 0.10                 ║
║  NoiseTrader:             p=0.30 → random 100–500 buy/sell           ║
║         │                                                             ║
║         └──── send orders → Market.perceive() [next round]           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration Reference

Key Configuration Parameters (`configs/AvailabilityBias/Rule/players.yml`):

| Parameter              | Config Path                   | Value | Design Justification                                                        |
|------------------------|-------------------------------|-------|-----------------------------------------------------------------------------|
| `price_impact`         | `extras.price_impact`         | 0.01  | Moderate λ — availability bias creates overreaction, not leverage cascade   |
| `mean_reversion`       | `extras.mean_reversion`       | 0.02  | Moderate γ — allows bias to persist briefly but not permanently             |
| `noise_std`            | `extras.noise_std`            | 0.5   | Higher σ — availability events are stochastic surprises; see sim-bases §3.1 |
| `recency_weight`       | `extras.recency_weight`       | 3.0   | Tversky & Kahneman (1973) recency amplification; see sim-bases §6           |
| `salience_threshold`   | `extras.salience_threshold`   | 0.05  | Salient event threshold; see sim-bases §6                                   |
| `media_weight`         | `extras.media_weight`         | 2.0   | Tetlock (2007) media amplification; see sim-bases §6                        |
| `social_amplification` | `extras.social_amplification` | 1.5   | Kasperson et al. (1988) social amplification; see sim-bases §6              |
| `evidence_threshold`   | `extras.evidence_threshold`   | 0.03  | Mullainathan (2002) systematic processing threshold; see sim-bases §6       |
| `deviation_threshold`  | `extras.deviation_threshold`  | 0.10  | Graham (1949) value investing threshold; see sim-bases §6                   |

---

## 6. Running Instructions

```bash
python examples/AvailabilityBias/Rule/run_availabilitybias.py \
    -c configs/AvailabilityBias/Rule/simulation.yml
```

Required environment variables: None (Rule variant requires no API keys)

Expected runtime: ~10–30 seconds for 100 rounds (pure Python, no LLM calls)

Output location: `EXPERIMENT/AvailabilityBias/Rule/`

---

## 7. Expected Behavior Patterns

| Phase              | Rounds | Expected Agent Behavior                                                                                         | Expected Price Dynamics                                              |
|--------------------|--------|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| Pre-Event          | 1–20   | NoiseTrader provides background; small returns keep `return_pct` near 0                                         | Price near 100; deviation < 2%                                       |
| Availability Event | 20–30  | Large noise shock →                                                                                             | return_pct                                                           |
| Bias Amplification | 30–50  | Continued availability signal → both biased agents trading in same direction; SystematicAnalyst counter-trading | Peak bias; bias_amplitude_pct = 3–10%                                |
| Partial Correction | 50–80  | Recency signal decays as `return_pct` normalizes; SystematicAnalyst + ValueTrader stabilize                     | Price returns toward fundamental; correction_ratio accumulating      |
| Stabilization      | 80–100 | All biased signals below threshold; ValueTrader absorbs remaining mispricing                                    | Price within 1–3% of fundamental; bias_persistence accumulation ends |

---

## 8. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Availability heuristic recency → `simulation-bases.md §2.1, §4 — RecentEventOverweighter`
- Media-driven availability → `simulation-bases.md §2.2, §4 — MediaInfluencedTrader`
- Bounded rationality memory model → `simulation-bases.md §2.3, §4 — SystematicAnalyst`
- Value investing discipline → `simulation-bases.md §2.4, §4 — ValueTrader`
- Noise trader theory → `simulation-bases.md §2.5, §4 — NoiseTrader`
- Price formula + unique broadcast → `simulation-bases.md §3.1, §3.3`
- Full parameter table with source citations → `simulation-bases.md §6`
