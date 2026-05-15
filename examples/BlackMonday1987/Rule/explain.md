# BlackMonday1987 Rule — Implementation Explanation

## Overview

| Item                                   | Description                                                                                                                    |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rule (deterministic baseline)                                                                                                  |
| **Implements**                         | `../simulation-bases.md`                                                                                                       |
| **Decision Logic**                     | Fixed thresholds and formulas — all parameters loaded from config; no LLM calls                                                |
| **Key Difference from Other Variants** | Fully deterministic; portfolio insurance and program trading feedback are exact algebraic formulas                             |
| **Primary Research Contribution**      | Establish the deterministic baseline: do mechanical trading rules alone reproduce the self-reinforcing feedback crash of 1987? |

---

## 1. How Theoretical Design Is Implemented

### PortfolioInsurer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — PortfolioInsurer)*

| Theoretical Design Element                                               | Implementation                                                                   |
|--------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Dynamic hedging sell rule → simulation-bases.md §2 (Portfolio Insurance) | Class docstring cites Leland & Rubinstein (1980); `players.py PortfolioInsurer`  |
| Sell when deviation < -rebalance_threshold → sim-bases §4                | `if deviation < 0: sell_qty = int(abs(deviation) * hedge_ratio * abs(position))` |
| Buy when deviation > +rebalance_threshold → sim-bases §4                 | `if deviation > 0: buy_qty = int(deviation * hedge_ratio * cash / price)`        |
| rebalance_threshold = ±0.02 → sim-bases §6                               | `rebalance_threshold = float(extras["rebalance_threshold"])` from `players.yml`  |
| hedge_ratio ≈ 0.5 → sim-bases §6                                         | `hedge_ratio = float(extras["hedge_ratio"])` from `players.yml`                  |
| Cap buy at 500 → sim-bases §4                                            | `buy_qty = min(buy_qty, 500)` enforced in `decide()`                             |

### IndexArbitrageur: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — IndexArbitrageur)*

| Theoretical Design Element                                             | Implementation                                                                                         |
|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Futures-spot arbitrage → simulation-bases.md §2 (Index Arbitrage)      | Class docstring cites Stoll & Whaley (1990)                                                            |
| Sell when spot overpriced: `deviation > +arb_threshold` → sim-bases §4 | `if deviation > 0: sell_qty = min(position_size, max(position, 0))`                                    |
| Buy when spot underpriced: `deviation < -arb_threshold` → sim-bases §4 | `if deviation < 0: buy_qty = min(position_size, int(cash / price))`                                    |
| arb_threshold = 0.005, position_size = 500 → sim-bases §6              | `arb_threshold = float(extras["arbitrage_threshold"])`; `position_size = int(extras["position_size"])` |

### ProgramTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ProgramTrader)*

| Theoretical Design Element                                                 | Implementation                                                               |
|----------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Feedback loop amplification → simulation-bases.md §2 (Program Trading)     | Class docstring cites Brady Commission (1988)                                |
| Sell when deviation < -trigger_threshold with amplification → sim-bases §4 | `amplified = int(sell_size * (1 + feedback_strength * abs(deviation) * 10))` |
| trigger_threshold = 0.01, feedback_strength = 0.3 → sim-bases §6           | Both loaded from `extras`                                                    |
| Buy when deviation > +trigger_threshold (trend-following) → sim-bases §4   | `buy_qty = min(sell_size, int(cash / price))`                                |

### ValueInvestor: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ValueInvestor)*

| Theoretical Design Element                                           | Implementation                                                                 |
|----------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Margin of safety buy rule → simulation-bases.md §2 (Value Investing) | Class docstring cites Graham (1949)                                            |
| Buy when deviation < -value_discount → sim-bases §4                  | `if deviation < -value_discount: buy_qty = min(order_size, int(cash / price))` |
| value_discount = 0.15, order_size = 800 → sim-bases §6               | Both loaded from `extras`                                                      |

### NoiseTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — NoiseTrader)*

| Theoretical Design Element                             | Implementation                                                                        |
|--------------------------------------------------------|---------------------------------------------------------------------------------------|
| Random uninformed trading → simulation-bases.md §4     | Class docstring cites Black (1986)                                                    |
| Trade probability 5% per round → sim-bases §6          | `if random.random() < prob:` where `prob = float(extras["trade_probability"])` = 0.05 |
| Quantity uniform [min_order, max_order] → sim-bases §6 | `qty = random.randint(min_order, max_order)`; `[100, 500]`                            |

---

## 2. Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market.perceive()` (inline computation after order collection)

Code translation:

| sim-bases variable   | Python variable                      | Config path                   | Value |
|----------------------|--------------------------------------|-------------------------------|-------|
| `λ` (price_impact)   | `price_impact`                       | `extras["price_impact"]`      | 0.002 |
| `γ` (mean_reversion) | `mean_reversion`                     | `extras["mean_reversion"]`    | 0.02  |
| `F` (fundamental)    | `fundamental`                        | `extras["fundamental_value"]` | 100.0 |
| `D(t)` (net demand)  | `net_demand = buy_vol − sell_vol`    | computed from incoming orders | —     |
| `ε(t)` (noise)       | `noise = random.gauss(0, noise_std)` | `extras["noise_std"]`         | 1.0   |

Price floor: `new_price = max(price + price_change + reversion + noise, 0.01)`

Note: Market broadcasts `{price, fundamental, deviation, round}` — does NOT include `prev_price` (use current round's price history).

Deviations from simulation-bases.md design: None.

---

## 3. Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rule variant entry)*

**Feedback amplification in code**: ProgramTrader's `amplified = int(sell_size × (1 + feedback_strength × |deviation| × 10))` is the core feedback formula. As deviation deepens, sell orders grow exponentially, creating the self-reinforcing crash.

**Simultaneous triggers**: Multiple agents trigger simultaneously when thresholds are breached — PortfolioInsurer at 2%, ProgramTrader at 1%, IndexArbitrageur at 0.5%. This sequential activation creates wave structure.

**ValueInvestor activation delay**: ValueInvestor only activates at 15% deviation — much deeper than the cascade triggers. This means the crash must reach −15% before any stabilizing force activates. Models the delayed deployment of long-term capital.

**NoiseTrader as background signal**: With 5% trade probability and 100–500 share range, NoiseTrader provides realistic background activity that slightly perturbs cascade timing.

---

## 4. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market.perceive()                                                    ║
║    ├── Collect orders from all investors (inbounds)                   ║
║    ├── buy_vol = Σ buy orders; sell_vol = Σ sell orders              ║
║    ├── net_demand = buy_vol − sell_vol                                ║
║    ├── P(t+1) = P(t) + 0.002×D + 0.02×(100−P) + N(0, 1²)          ║
║    └── deviation = (P(t+1) − 100) / 100                              ║
║                                                                       ║
║  Market.decide() → broadcast {price, fundamental, deviation, round}  ║
║                                                                       ║
║  PortfolioInsurer: |deviation| > 0.02?                               ║
║    → SELL: hedge_ratio × |deviation| × position (cascade creator)    ║
║    → BUY: hedge_ratio × deviation × cash / price (cap 500)          ║
║  IndexArbitrageur: |deviation| > 0.005? → SELL/BUY ≈500 shares       ║
║  ProgramTrader: deviation < -0.01?                                    ║
║    → SELL: amplified = sell_size × (1 + 0.3 × |deviation| × 10)    ║
║  ValueInvestor: deviation < -0.15? → BUY ≈800                       ║
║  NoiseTrader: 5% chance → random 100–500 buy/sell                   ║
║         │                                                             ║
║         └──── send orders → Market.perceive() [next round]           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration Reference

Key Configuration Parameters (`configs/BlackMonday1987/Rule/players.yml`):

| Parameter             | Config Path                  | Value | Design Justification                                                       |
|-----------------------|------------------------------|-------|----------------------------------------------------------------------------|
| `price_impact`        | `extras.price_impact`        | 0.002 | Moderate λ — large lot sizes (hundreds of shares) create significant moves |
| `mean_reversion`      | `extras.mean_reversion`      | 0.02  | Moderate γ — allows crash persistence but not permanent                    |
| `fundamental_value`   | `extras.fundamental_value`   | 100.0 | Stable benchmark; no fundamental deterioration (crash is mechanical)       |
| `rebalance_threshold` | `extras.rebalance_threshold` | 0.02  | Portfolio insurance triggers at 2% deviation; see sim-bases §6             |
| `hedge_ratio`         | `extras.hedge_ratio`         | 0.5   | Brady Commission (1988) hedge fraction calibration                         |
| `trigger_threshold`   | `extras.trigger_threshold`   | 0.01  | Program trading activates at 1% deviation; see sim-bases §6                |
| `feedback_strength`   | `extras.feedback_strength`   | 0.3   | Amplification factor from Brady Commission analysis; see sim-bases §6      |
| `value_discount`      | `extras.value_discount`      | 0.15  | Graham margin of safety threshold; see sim-bases §6                        |

---

## 6. Running Instructions

```bash
python examples/BlackMonday1987/Rule/run_blackmonday1987.py \
    -c configs/BlackMonday1987/Rule/simulation.yml
```

Required environment variables: None (Rule variant requires no API keys)

Expected runtime: ~10–30 seconds for 100 rounds (pure Python, no LLM calls)

Output location: `EXPERIMENT/BlackMonday1987/Rule/`

---

## 7. Expected Behavior Patterns

| Phase            | Rounds | Expected Agent Behavior                                                        | Expected Price Dynamics                                    |
|------------------|--------|--------------------------------------------------------------------------------|------------------------------------------------------------|
| Pre-Crash        | 1–10   | All agents hold; IndexArbitrageur may make small trades on noise deviations    | Price near 100; small fluctuations from noise              |
| Feedback Onset   | 5–15   | PortfolioInsurer triggers at −2%; IndexArbitrageur at −0.5%; selling begins    | First wave of selling; deviation crosses −5%               |
| Crash Escalation | 10–25  | ProgramTrader amplified selling; PortfolioInsurer selling grows with deviation | Sharp price drop; deviation −10% to −20%; feedback visible |
| Crash Peak       | 20–35  | All destabilizers active; ValueInvestor activates at −15%                      | Maximum drawdown; deviation −20% to −30%; volume peaks     |
| Recovery         | 35–100 | ValueInvestor absorbs; mean reversion; destabilizers reduce position           | Gradual recovery toward fundamental; volatility subsides   |

---

## 8. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Portfolio insurance dynamic hedging → `simulation-bases.md §2, §4 — PortfolioInsurer`
- Index arbitrage futures-spot transmission → `simulation-bases.md §2, §4 — IndexArbitrageur`
- Program trading feedback amplification → `simulation-bases.md §2, §4 — ProgramTrader`
- Value investing margin of safety → `simulation-bases.md §2, §4 — ValueInvestor`
- Noise trading background → `simulation-bases.md §2, §4 — NoiseTrader`
- Price formula → `simulation-bases.md §3.1`
- Full parameter table with source citations → `simulation-bases.md §6`
