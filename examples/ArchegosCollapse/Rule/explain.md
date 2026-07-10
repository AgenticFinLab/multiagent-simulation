# ArchegosCollapse Rule — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                   |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rule (deterministic baseline)                                                                                                                 |
| **Implements**                         | `../simulation-bases.md`                                                                                                                      |
| **Decision Logic**                     | Fixed thresholds and formulas — all parameters loaded from config; no LLM calls                                                               |
| **Key Difference from Other Variants** | Fully deterministic; every decision is a traceable formula with no stochastic LLM component                                                   |
| **Primary Research Contribution**      | Establish the deterministic baseline: do liquidation cascade rules alone reproduce the self-reinforcing prime broker race and price collapse? |

---

## §2 Theory → Implementation Mapping

### ConcentratedFund: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.1 — ConcentratedFund)*

| Theory Component                                                      | Implementation                                                                                    |
|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| TRS Leverage → simulation-bases.md §2 (TRS Leverage Theory)           | Class docstring cites Becketti (2021); `players.py` `ConcentratedFund` class                      |
| Margin call trigger: `deviation < -leverage_trigger` → sim-bases §4   | `if deviation < margin_threshold:` in `decide()`; `margin_threshold = extras["margin_threshold"]` |
| Leverage trigger = −0.15 → sim-bases §6                               | `margin_threshold = extras["margin_threshold"]` loaded from `players.yml`                         |
| Sell `liquidation_fraction × position` → sim-bases §4 (Rule Behavior) | `quantity = position * trs_sell_ratio`; `trs_sell_ratio = extras["trs_sell_ratio"]`               |
| Position constraint → sim-bases §6                                    | `quantity = min(quantity, max(position, 0.0))` in `decide()`                                      |
| Cash update on execution → sim-bases §4                               | `self.state.custom_state["cash"] += quantity * price` in `act()`                                  |

### PrimeBrokerFirstMover: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.2 — PrimeBrokerFirstMover)*

| Theory Component                                                         | Implementation                                                                                          |
|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| First-mover liquidation race → simulation-bases.md §2 (Liquidation Race) | Class docstring cites Gorton & Metrick (2012)                                                           |
| Lower threshold (acts first): `deviation < -0.10` → sim-bases §4         | `if deviation < liquidation_threshold:` where `liquidation_threshold = extras["liquidation_threshold"]` |
| Sell `liquidation_sell_ratio × position` → sim-bases §4                  | `quantity = position * liquidation_sell_ratio`; ratio loaded from `extras`                              |
| Receives full market price (first-mover advantage) → sim-bases §4        | No `price_penalty` applied; `cash += quantity * price` directly in `act()`                              |

### PrimeBrokerDelayedLiquidator: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.3 — PrimeBrokerDelayedLiquidator)*

| Theory Component                                                             | Implementation                                                                              |
|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Second-mover disadvantage → simulation-bases.md §2 (Liquidation Race)        | Class docstring; higher `liquidation_threshold` = 0.15 vs PrimeBrokerFirstMover's 0.10      |
| Price penalty: effective_price = market_price × price_penalty → sim-bases §4 | `effective_price = price * price_penalty`; `price_penalty = extras["price_penalty"]`        |
| Cash update at effective price → sim-bases §4                                | `cash += quantity * effective_price` in `act()` (vs PrimeBrokerFirstMover using full price) |

### BlockTradeBuyer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.4 — BlockTradeBuyer)*

| Theory Component                                                          | Implementation                                                                                 |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Opportunistic buying at discount → simulation-bases.md §2 (Block Trading) | Class docstring cites Grossman & Miller (1988)                                                 |
| Buy condition: `deviation < -discount_threshold` → sim-bases §4           | `if deviation < discount_threshold:` where `discount_threshold = extras["discount_threshold"]` |
| Deploy `buy_ratio × cash` → sim-bases §4                                  | `quantity = (cash * buy_ratio) / price`; `buy_ratio = extras["buy_ratio"]`                     |
| Cash constraint → sim-bases §6                                            | Quantity naturally bounded by cash; `cash -= quantity * price` in `act()`                      |

### InformationTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.5 — InformationTrader)*

| Theory Component                                                                 | Implementation                                                                                    |
|----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| Information-based front-running → simulation-bases.md §2 (Kyle, 1985)            | Class docstring; probabilistic detection simulates partial information advantage                  |
| Detection: `deviation < -detection_threshold` AND `random() < detection_ability` | `if deviation < detection_threshold and random.random() < detection_ability:` in `decide()`       |
| Front-run size = min(front_run_size, position) → sim-bases §4                    | `sell_qty = min(front_run_size, max(position, 0.0))`; `front_run_size = extras["front_run_size"]` |
| Short-cover ledger → sim-bases §4                                                | `short_position` increments after front-run sells and decrements when recovery-cover buys execute |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market.perceive()` (inline computation after order collection)

Code translation:

| sim-bases variable   | Python variable                      | Config path                        | Value |
|----------------------|--------------------------------------|------------------------------------|-------|
| `λ` (price_impact)   | `price_impact`                       | `extras["price_impact"]`           | 0.03  |
| `γ` (mean_reversion) | `mean_reversion`                     | `extras["mean_reversion"]`         | 0.01  |
| `F` (fundamental)    | `fundamental`                        | `extras["fundamental_value"]`      | 100.0 |
| `D(t)` (net demand)  | `net_demand = buy_qty − sell_qty`    | computed from incoming orders      | —     |
| `ε(t)` (noise)       | `noise = random.gauss(0, noise_std)` | `extras["noise_std"]`              | 0.015 |
| `P(t)` (current)     | `current_price`                      | `self.state.custom_state["price"]` | —     |

Price floor: `new_price = max(new_price, 0.01)` — prevents negative prices during extreme cascades.

Deviation broadcast: `deviation = (new_price − fundamental) / fundamental` — key distress signal.

Additional mechanisms (simulation-bases.md §3.2):
- Short selling allowed: `InformationTrader` can hold negative `position` and short `front_run_size` shares
- PrimeBrokerDelayedLiquidator price penalty: `effective_price = price * price_penalty` — models second-mover worse execution

Deviations from simulation-bases.md design: None — all formula variables map directly.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rule variant entry)*

**Fully deterministic**: All thresholds are loaded from `extras` in `players.yml`. Given the same config and random seed, the same cascade triggers at the same round every time. This makes the Rule variant the calibration baseline for cross-variant comparison.

**Threshold asymmetry implementation**: The key first-mover advantage is encoded as `liquidation_threshold` difference:
- PrimeBrokerFirstMover: `extras["liquidation_threshold"]` = −0.10 (acts first)
- PrimeBrokerDelayedLiquidator: `extras["liquidation_threshold"]` = −0.15 (acts after price has already fallen further)

**No LLM delay**: ConcentratedFund sells immediately when `deviation < margin_threshold` — no hesitation or denial psychology. This creates the fastest, deepest cascade of any variant.

**Detection probability**: `InformationTrader` uses `random.random() < detection_ability` (0.50) — the only stochastic element. This makes the cascade onset round slightly variable even in Rule variant (front-running timing uncertainty).

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market.perceive()                                                    ║
║    ├── Collect orders from all investors (inbounds)                   ║
║    ├── buy_qty = Σ buy orders; sell_qty = Σ sell orders              ║
║    ├── net_demand = buy_qty − sell_qty                                ║
║    ├── P(t+1) = P(t) + 0.03×D + 0.01×(100−P) + N(0, 0.015²)       ║
║    └── deviation = (P(t+1) − 100) / 100                              ║
║                                                                       ║
║  Market.decide() → broadcast {price, prev_price, fundamental,        ║
║                               deviation, round} to all investors      ║
║                                                                       ║
║  ConcentratedFund:  deviation < −0.15? → SELL 50% position           ║
║  PrimeBrokerFirstMover:      deviation < −0.10? → SELL 40% position           ║
║  PrimeBrokerDelayedLiquidator:      deviation < −0.15? → SELL 35% position @ −3%    ║
║  BlockTradeBuyer:   deviation < −0.10? → BUY 30% of cash / price    ║
║  InformationTrader: deviation < −0.05 AND rand<0.5? → SELL 1000      ║
║         │                                                             ║
║         └──── send orders → Market.perceive() [next round]           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/ArchegosCollapse/Rule/players.yml`):

| Parameter               | Config Path                    | Value         | Design Justification                                                          |
|-------------------------|--------------------------------|---------------|-------------------------------------------------------------------------------|
| `price_impact`          | `extras.price_impact`          | 0.03          | High λ — large liquidation blocks cause significant price impact              |
| `mean_reversion`        | `extras.mean_reversion`        | 0.01          | Low γ — ensures cascade persists; not immediately corrected                   |
| `fundamental_value`     | `extras.fundamental_value`     | 100.0         | Stable benchmark; all deviations relative to this                             |
| `initial_price`         | `extras.initial_price`         | 100.0         | Starts at fair value; cascade driven by liquidation, not initial mispricing   |
| `margin_threshold`      | `extras.margin_threshold`      | −0.15         | Becketti (2021) TRS margin call level; see sim-bases §6                       |
| `trs_sell_ratio`        | `extras.trs_sell_ratio`        | 0.50          | Archegos post-mortem: 50% position forced liquidation                         |
| `liquidation_threshold` | `extras.liquidation_threshold` | −0.10 / −0.15 | PrimeBrokerFirstMover/2 asymmetry captures first-mover timing                 |
| `price_penalty`         | `extras.price_penalty`         | 0.97          | PrimeBrokerDelayedLiquidator sells at 3% discount — second-mover disadvantage |
| `discount_threshold`    | `extras.discount_threshold`    | −0.10         | Grossman & Miller (1988) block buyer entry level; see sim-bases §6            |
| `detection_threshold`   | `extras.detection_threshold`   | −0.05         | Kyle (1985) information signal threshold; see sim-bases §6                    |

---

## §7 Running Instructions

```bash
python examples/ArchegosCollapse/Rule/run_archegsoscollapse.py \
    -c configs/ArchegosCollapse/Rule/simulation.yml
```

Required environment variables: None (Rule variant requires no API keys)

Expected runtime: ~10–30 seconds for 200 rounds (pure Python, no LLM calls)

Output location: `EXPERIMENT/ArchegosCollapse/Rule/`

---

## §8 Expected Behavior Patterns

| Phase         | Rounds | Expected Agent Behavior                                                                        | Expected Price Dynamics                            |
|---------------|--------|------------------------------------------------------------------------------------------------|----------------------------------------------------|
| Pre-Cascade   | 1–10   | All agents hold; InformationTrader may detect early signal at ~5% deviation                    | Price near 100; small fluctuations from noise      |
| Cascade Onset | 10–20  | PrimeBrokerFirstMover triggers at −10%; ConcentratedFund at −15%; InformationTrader front-runs | Sharp price drop; deviation crosses −10% then −15% |
| Peak Cascade  | 20–35  | PrimeBrokerDelayedLiquidator forced to sell at discounted prices; BlockTradeBuyer activates    | Price trough; max drawdown; deviation −20% to −40% |
| Recovery      | 35–100 | BlockTradeBuyer absorbs supply; InformationTrader covers short; mean reversion                 | Price gradually recovers toward fundamental (100)  |

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- TRS leverage / ConcentratedFund behavior → `simulation-bases.md §2, §4 — ConcentratedFund`
- Creditor run / prime broker liquidation race → `simulation-bases.md §2, §4 — PrimeBrokerFirstMover, PrimeBrokerDelayedLiquidator`
- Opportunistic block trading / price floor → `simulation-bases.md §2, §4 — BlockTradeBuyer`
- Information-based front-running → `simulation-bases.md §2, §4 — InformationTrader`
- Price formula implementation → `simulation-bases.md §3.1`
- Full parameter table with source citations → `simulation-bases.md §6`
