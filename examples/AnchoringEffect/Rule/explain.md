# AnchoringEffect Rule — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                            |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rule (deterministic baseline)                                                                                                                          |
| **Implements**                         | `../simulation-bases.md`                                                                                                                               |
| **Decision Logic**                     | Fixed formulas — all thresholds and parameters loaded from config; no LLM calls                                                                        |
| **Key Difference from Other Variants** | Fully deterministic; every decision is a traceable formula with no stochastic LLM component                                                            |
| **Primary Research Contribution**      | Establish the deterministic baseline showing whether anchoring formulas alone reproduce empirically observed price stickiness and slow price discovery |

---

## §2 How Theoretical Design Is Implemented

### AnchoredTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — AnchoredTrader)*

| Theoretical Design Element                                                | Implementation                                                                                 |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Anchoring and Insufficient Adjustment → simulation-bases.md §2.1          | Class docstring cites Tversky & Kahneman (1974); players.py line ~141                          |
| Anchor = first price observed → sim-bases §4 (AnchoredTrader, Rule-Based) | `anchor_price` initialized to `None`; set to `market_data["price"]` on first `perceive()` call |
| Perceived target formula → sim-bases §4 (AnchoredTrader)                  | `perceived_target = anchor_price + (fundamental − anchor_price) × adjustment_factor`           |
| Adjustment factor α = 0.3 → sim-bases §6                                  | `adjustment_factor = extras["adjustment_factor"]` loaded from players.yml                      |
| Buy/sell threshold 3% → sim-bases §4 (AnchoredTrader)                     | `if abs(perceived_dev) > 0.03: ...` in `decide()`                                              |
| Position sizing → sim-bases §6                                            | `quantity = min(base_position_size, abs(perceived_dev) × 1000)` constrained by cash/position   |

### HistoricalAnchor: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — HistoricalAnchor)*

| Theoretical Design Element                                     | Implementation                                                                                    |
|----------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| Expert anchoring to historical average → sim-bases §2.2        | Class docstring cites Northcraft & Neale (1987)                                                   |
| Rolling 60-round lookback → sim-bases §6                       | `historical_prices` list; `lookback = extras["lookback"]` (= 60); trimmed each round              |
| Dampened perceived deviation → sim-bases §4 (HistoricalAnchor) | `perceived_dev = (price − hist_avg) / hist_avg × (1 − anchor_weight)` where `anchor_weight = 0.5` |
| Trade threshold 3% → sim-bases §4                              | Same threshold pattern as AnchoredTrader                                                          |
| Parameters from config → sim-bases §6                          | `anchor_weight`, `lookback`, `base_position_size` from `extras`                                   |

### RationalUpdater: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — RationalUpdater)*

| Theoretical Design Element                             | Implementation                                                                           |
|--------------------------------------------------------|------------------------------------------------------------------------------------------|
| Rational expectations benchmark → sim-bases §2.4       | Class docstring cites Muth (1961)                                                        |
| Trade directly on fundamental deviation → sim-bases §4 | Uses `market_data["deviation"]` (pre-computed by Market) — no anchoring adjustment       |
| Trade threshold 2% → sim-bases §6                      | `if abs(deviation) > 0.02:` in `decide()`                                                |
| Position sizing → sim-bases §6                         | `quantity = min(base_position_size, abs(deviation) × 1000)` constrained by cash/position |

### MomentumTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — MomentumTrader)*

| Theoretical Design Element                     | Implementation                                                                            |
|------------------------------------------------|-------------------------------------------------------------------------------------------|
| Momentum effect → sim-bases §2.5               | Class docstring cites Jegadeesh & Titman (1993)                                           |
| Signal: round-over-round return → sim-bases §4 | `return_pct = (price − prev_price) / prev_price` using `market_data["prev_price"]`        |
| Entry threshold 2% → sim-bases §6              | `entry_threshold = extras["entry_threshold"]` (= 0.02)                                    |
| Position sizing → sim-bases §6                 | `quantity = min(base_position_size, abs(return_pct) × 1000)` constrained by cash/position |

### NoiseTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — NoiseTrader)*

| Theoretical Design Element                    | Implementation                                                                                    |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------|
| Random uninformed trading → sim-bases §2.6    | Class docstring cites Black (1986)                                                                |
| Trade probability 5% per round → sim-bases §6 | `if random.random() < trade_probability:` where `trade_probability = extras["trade_probability"]` |
| Quantity uniform [min, max] → sim-bases §6    | `quantity = random.uniform(min_order, max_order)`; constrained by cash/position                   |
| Random direction → sim-bases §4 (NoiseTrader) | `if random.random() > 0.5: action = "buy" else: action = "sell"`                                  |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market.perceive()` (inline computation, no separate method)

Code translation:

| sim-bases variable     | Python variable                      | Config path                        | Value |
|------------------------|--------------------------------------|------------------------------------|-------|
| `λ` (price_impact)     | `price_impact`                       | `extras["price_impact"]`           | 0.01  |
| `γ` (mean_reversion)   | `mean_reversion`                     | `extras["mean_reversion"]`         | 0.01  |
| `F` (fundamental)      | `fundamental`                        | `extras["fundamental_value"]`      | 100.0 |
| `D(t)` (net demand)    | `net_demand = buy_qty − sell_qty`    | computed from orders               | —     |
| `ε(t)` (noise)         | `noise = random.gauss(0, noise_std)` | `extras["noise_std"]`              | 0.5   |
| `P(t)` (current price) | `current_price`                      | `self.state.custom_state["price"]` | —     |

Price floor: `new_price = max(new_price, 0.01)` — prevents numerical instability.

Deviation computation: `deviation = (new_price − fundamental) / fundamental` — broadcast to all investors each round.

Additional mechanisms: simulation-bases.md §3.2
- **Cash constraint** → `quantity = min(quantity, cash / price)` in all investor `decide()` methods
- **Position constraint** → `quantity = min(quantity, max(position, 0.0))` for sell orders

Deviations from simulation-bases.md design: None. All formula variables map directly.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rule variant entry)*

This variant establishes the deterministic ground truth for the anchoring phenomenon.

**Key constraint**: No hardcoded values anywhere. All numeric thresholds, position sizes, and parameters are loaded from `extras` in `players.yml`. See simulation-bases.md §6 for parameter source citations.

**AnchoredTrader anchor initialization**: The anchor is set to the first price received from Market in round 1 (`initial_price = 105.0`). This is the core anchoring seed — the agent's perceived target will be biased toward 105 throughout the simulation even as price converges toward fundamental 100.

**Portfolio state management**: All investor classes manage `cash` and `position` in `act()` by applying the trade. No separate execution system — the investor applies its own constraints and executes atomically.

**HistoryBuffer**: All price histories use `masim.utils.history.HistoryBuffer` with `folder` pointing to the record path and `entry_limit = custom_state_hot_limit`. This avoids unbounded memory growth.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════╗
║                         ROUND N                              ║
╠══════════════════════════════════════════════════════════════╣
║  Market.perceive()                                           ║
║    ├── Collect orders from all investors (inbounds)          ║
║    ├── Aggregate: buy_qty, sell_qty, net_demand              ║
║    ├── Apply: P(t+1) = P(t) + λ×D + γ×(F−P) + ε            ║
║    └── Compute: deviation = (P−F)/F                          ║
║                                                              ║
║  Market.decide()  →  broadcast market_data to all           ║
║    payload: {price, prev_price, fundamental, deviation, round}║
║                                                              ║
║  AnchoredTrader (×3):  perceived_target → buy/sell/hold      ║
║  HistoricalAnchor (×3): hist_avg based → buy/sell/hold       ║
║  RationalUpdater (×3):  deviation → buy/sell/hold            ║
║  MomentumTrader (×2):   return_pct → buy/sell/hold           ║
║  NoiseTrader (×2):      random → buy/sell/hold               ║
║        │                                                      ║
║        └──── send orders → Market.perceive() [next round]    ║
╚══════════════════════════════════════════════════════════════╝
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/AnchoringEffect/Rule/players.yml`):

| Parameter           | Config Path                | Value | Design Justification                                                          |
|---------------------|----------------------------|-------|-------------------------------------------------------------------------------|
| `price_impact`      | `extras.price_impact`      | 0.01  | Low λ — anchoring agents generate small demand; prevents excessive volatility |
| `mean_reversion`    | `extras.mean_reversion`    | 0.01  | Low γ — essential for sustained mispricing; see sim-bases §3.1                |
| `fundamental_value` | `extras.fundamental_value` | 100.0 | Stable benchmark; deviation attributable purely to anchoring bias             |
| `initial_price`     | `extras.initial_price`     | 105.0 | Seeds 5% initial mispricing; AnchoredTrader anchors to this value             |
| `adjustment_factor` | `extras.adjustment_factor` | 0.3   | α calibrated from Tversky & Kahneman (1974); see sim-bases §6                 |
| `anchor_weight`     | `extras.anchor_weight`     | 0.5   | Northcraft & Neale (1987) expert anchoring; see sim-bases §6                  |
| `lookback`          | `extras.lookback`          | 60    | Campbell & Sharpe (2009) quarterly window; see sim-bases §6                   |
| `entry_threshold`   | `extras.entry_threshold`   | 0.02  | Jegadeesh & Titman (1993) momentum signal; see sim-bases §6                   |
| `trade_probability` | `extras.trade_probability` | 0.05  | Black (1986) noise trader activity; see sim-bases §6                          |

---

## §7 Running Instructions

```bash
python examples/AnchoringEffect/Rule/run_anchoringeffect.py \
    -c configs/AnchoringEffect/Rule/simulation.yml
```

Required environment variables: None (Rule variant requires no API keys)

Expected runtime: ~10–30 seconds for 100 rounds (pure Python, no LLM calls)

Output location: `EXPERIMENT/AnchoringEffect/Rule/`

---

## §8 Expected Behavior Patterns

| Phase              | Rounds | Expected Agent Behavior                                                | Expected Price Dynamics                                        |
|--------------------|--------|------------------------------------------------------------------------|----------------------------------------------------------------|
| Anchor Setup       | 1–5    | AnchoredTrader sets anchor = 105; HistoricalAnchor accumulates history | Price remains near 105; minimal RationalUpdater pressure       |
| Persistent Bias    | 5–60   | AnchoredTrader resists correction (perceived_target ≈ 101.5 vs F=100)  | Price declines slowly; deviation 3–7%; RationalUpdater selling |
| Gradual Correction | 60–90  | HistoricalAnchor's hist_avg converges to ~102; bias weakens            | Price approaches 101–102; deviation shrinks                    |
| Near-Convergence   | 90–100 | All anchoring signals weaken; RationalUpdater dominates                | Price within 1–2% of fundamental                               |

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Anchoring and Insufficient Adjustment → `simulation-bases.md §2.1, §4 — AnchoredTrader`
- Expert anchoring to historical prices → `simulation-bases.md §2.2, §4 — HistoricalAnchor`
- Consensus forecast anchoring (calibration) → `simulation-bases.md §2.3, §6`
- Rational expectations benchmark → `simulation-bases.md §2.4, §4 — RationalUpdater`
- Momentum effect → `simulation-bases.md §2.5, §4 — MomentumTrader`
- Noise trader theory → `simulation-bases.md §2.6, §4 — NoiseTrader`
- Price formula → `simulation-bases.md §3.1`
- Full parameter table → `simulation-bases.md §6`
