# AssetBubble Rule — Implementation Explanation

## Overview

| Item                               | Description                                                                                                                                                               |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant                            | Rule                                                                                                                                                                      |
| Implements                         | `../simulation-bases.md`                                                                                                                                                  |
| Decision Logic                     | Deterministic mathematical formulas; all parameters loaded from `players.yml`; no LLM calls                                                                               |
| Key Difference from Other Variants | Fully reproducible — same config produces identical output every run; establishes the baseline                                                                            |
| Primary Research Contribution      | Verifies that the target phenomenon (asset bubble) emerges purely from agent interaction rules and market mechanics, without any language reasoning or external knowledge |

---

## 1. Design Motivation and Baseline Role

The Rule variant is the **deterministic foundation** of the four-variant research design (see `simulation-bases.md §9`). Its purpose is not just to produce a bubble, but to establish a reproducible quantitative baseline against which LLM, RuleLLM, and Rag variants can be directly compared.

Every design decision in this variant is traceable:
- Every agent behavior → `simulation-bases.md §4` investor specification
- Every formula parameter → `simulation-bases.md §6` parameter table with source citations
- Every market mechanism → `simulation-bases.md §3` market design principles

---

## 2. Theory → Implementation Mapping

### Market: Theory → Implementation
*(Theory defined in `simulation-bases.md §3`)*

| Theoretical Design Element                                                 | Implementation                                                                                                                                 |
|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Price formation model → `simulation-bases.md §3.1`                         | `Market.decide()` in `players.py`; formula: `new_price = current_price + price_impact×net_demand + mean_reversion×(fundamental−price) + noise` |
| Bubble-prone parameter choice (high λ, low γ) → `simulation-bases.md §3.1` | `extras["price_impact"] = 0.15`; `extras["mean_reversion"] = 0.005` in `configs/AssetBubble/Rule/players.yml`                                  |
| Short-selling constraints → `simulation-bases.md §3.2`                     | `BaseInvestor._apply_constraints()`: `max_sellable = position + 50`                                                                            |
| Margin call mechanism → `simulation-bases.md §3.2`                         | `LeveragedBuyer.decide()`: `if equity_ratio < margin_call_threshold: quantity = -position × 0.5`                                               |
| Information broadcast design → `simulation-bases.md §3.3`                  | `Market.decide()` returns `market_data` dict with all fields listed in §3.3; broadcast via `outbound_messages`                                 |
| Price floor (non-negativity) → `simulation-bases.md §3.2`                  | `new_price = max(1.0, ...)` in `Market.decide()`                                                                                               |

---

### MomentumSpeculator: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — MomentumSpeculator`)*

| Theoretical Design Element                                                             | Implementation                                                                                                                        |
|----------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Greater Fool Theory`                     | Class docstring: "Theory: Greater Fool Theory"; `players.py` line ~283                                                                |
| Buy condition (momentum > threshold) → `simulation-bases.md §4 — Rule-Based Behavior`  | `if momentum > 0.01: quantity = aggressiveness × momentum × base_position_size × leverage_multiplier`                                 |
| Sell condition (momentum < threshold) → `simulation-bases.md §4 — Rule-Based Behavior` | `elif momentum < -0.02: quantity = aggressiveness × momentum × base_position_size`                                                    |
| Momentum formula (MA5) → `simulation-bases.md §4 — Rule-Based Behavior`                | `recent_prices = list(price_history)[-lookback_short:]`; `ma_short = mean(recent_prices)`; `momentum = (price - ma_short) / ma_short` |
| Position caps → `simulation-bases.md §6`                                               | `min(quantity, 100)` for buys; `max(quantity, -80)` for sells                                                                         |
| Parameters loaded from config → `simulation-bases.md §6`                               | `extras["lookback_short"]`, `extras["aggressiveness"]`, `extras["base_position_size"]`, `extras["leverage_multiplier"]`               |
| Expected market impact → `simulation-bases.md §4 — Expected Market Impact`             | Primary driver of net_demand spike; see `analyze_bubble()` in `analysis.py`                                                           |

---

### RationalArbitrageur: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — RationalArbitrageur`)*

| Theoretical Design Element                                                  | Implementation                                                                                                                      |
|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Limits to Arbitrage`          | Class docstring: "Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)"; `players.py` line ~370                                    |
| Short trigger (overvalued) → `simulation-bases.md §4 — Rule-Based Behavior` | `if deviation > deviation_threshold and short_position < max_short_position:`                                                       |
| Cost penalty formula → `simulation-bases.md §4 — Rule-Based Behavior`       | `cost_penalty = max(0.2, 1.0 - short_cost_sensitivity × short_cost × 10)`                                                           |
| Short position cap → `simulation-bases.md §6`                               | `quantity = -min(short_size, max_short_position - short_position)`                                                                  |
| Buy trigger (undervalued) → `simulation-bases.md §4 — Rule-Based Behavior`  | `elif deviation < -deviation_threshold: quantity = min(abs(deviation) × base_size, 30)`                                             |
| Parameters loaded from config → `simulation-bases.md §6`                    | `extras["deviation_threshold"]`, `extras["max_short_position"]`, `extras["short_cost_sensitivity"]`, `extras["base_position_size"]` |

---

### NoiseTrader: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — NoiseTrader`)*

| Theoretical Design Element                                                  | Implementation                                                                               |
|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Noise Trader Risk`            | Class docstring: "Theory: De Long et al. (1990) - Noise Trader Risk"; `players.py` line ~466 |
| Random sentiment component → `simulation-bases.md §4 — Rule-Based Behavior` | `random_sentiment = random.gauss(0, sentiment_volatility)`                                   |
| Herding component → `simulation-bases.md §4 — Rule-Based Behavior`          | `herding_sentiment = herding_weight × price_return × 10`                                     |
| Combined sentiment signal → `simulation-bases.md §4`                        | `total_sentiment = random_sentiment + herding_sentiment`                                     |
| Position sizing → `simulation-bases.md §4 — Rule-Based Behavior`            | `quantity = total_sentiment × base_size`, capped at ±40                                      |
| Parameters loaded from config → `simulation-bases.md §6`                    | `extras["sentiment_volatility"]`, `extras["herding_weight"]`, `extras["base_position_size"]` |

---

### FundamentalInvestor: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — FundamentalInvestor`)*

| Theoretical Design Element                                                 | Implementation                                                                             |
|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Traditional Value Investing` | Class docstring: "Theory: Traditional value investing"; `players.py` line ~544             |
| Frequency gate → `simulation-bases.md §4 — Rule-Based Behavior`            | `if round_num % trade_frequency != 0: quantity = 0.0`                                      |
| Value deviation formula → `simulation-bases.md §4 — Rule-Based Behavior`   | `deviation = (fundamental - price) / price`                                                |
| Position sizing → `simulation-bases.md §4 — Rule-Based Behavior`           | `quantity = value_sensitivity × deviation × base_size`, clamped to `[-15, +15]`            |
| Parameters loaded from config → `simulation-bases.md §6`                   | `extras["trade_frequency"]`, `extras["value_sensitivity"]`, `extras["base_position_size"]` |

---

### LeveragedBuyer: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — LeveragedBuyer`)*

| Theoretical Design Element                                                                       | Implementation                                                                                                            |
|--------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Leverage amplification + procyclical deleveraging` | Class docstring: "Theory: Leverage amplifies both gains and losses"; `players.py` line ~616                               |
| Margin call check (highest priority) → `simulation-bases.md §4 — Rule-Based Behavior`            | First condition: `if equity_ratio < margin_call_threshold and position > 0: quantity = -position × 0.5`                   |
| Equity ratio formula → `simulation-bases.md §4`                                                  | `portfolio_value = cash + position × price`; `equity_ratio = portfolio_value / initial_equity`                            |
| Leveraged buy condition → `simulation-bases.md §4 — Rule-Based Behavior`                         | `elif price_return > 0.005: quantity = price_return × base_size × leverage_ratio`, capped at +60                          |
| Sell on downturn → `simulation-bases.md §4 — Rule-Based Behavior`                                | `elif price_return < -0.01: quantity = price_return × base_size`, floored at -40                                          |
| Parameters loaded from config → `simulation-bases.md §6`                                         | `extras["leverage_ratio"]`, `extras["margin_call_threshold"]`, `extras["base_position_size"]`, `extras["initial_equity"]` |

---

### ConservativeHolder: Theory → Implementation
*(Theory defined in `simulation-bases.md §4 — ConservativeHolder`)*

| Theoretical Design Element                                                | Implementation                                                                                 |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| Theoretical basis → `simulation-bases.md §4 — Passive investing`          | Class docstring: "Provides small stabilizing force"; `players.py` line ~700                    |
| Rebalance frequency gate → `simulation-bases.md §4 — Rule-Based Behavior` | `if round_num % rebalance_frequency != 0: quantity = 0.0`                                      |
| Slow convergence formula → `simulation-bases.md §4`                       | `gap = target_position - position`; `quantity = gap × rebalance_rate`, clamped to `[-10, +10]` |
| Parameters loaded from config → `simulation-bases.md §6`                  | `extras["target_position"]`, `extras["rebalance_frequency"]`, `extras["rebalance_rate"]`       |

---

## 3. Market Mechanism Implementation

> Formula source: `simulation-bases.md §3.1`

```
P(t+1) = P(t) + λ × D(t) + γ × [F(t) - P(t)] + ε(t)
```

**Implemented in**: `players.py → Market.decide()`

**Code translation**:

| sim-bases variable | Python variable                                                                                              | Config path in players.yml                                                                                                                |
|--------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| P(t)               | `current_price`                                                                                              | `extras["initial_price"]` (initial); updated via `self.state.custom_state["price"]`                                                       |
| D(t)               | `net_demand = total_buy_qty - total_sell_qty`                                                                | Computed from aggregated investor orders                                                                                                  |
| F(t)               | `current_fundamental`                                                                                        | `extras["fundamental_value"]` (initial); updated each round: `new_fundamental = current_fundamental × (1 + extras["fundamental_growth"])` |
| λ (lambda)         | `extras["price_impact"]` → `price_impact = extras["price_impact"] × net_demand`                              | `extras.price_impact: 0.15`                                                                                                               |
| γ (gamma)          | `extras["mean_reversion"]` → `mean_reversion = extras["mean_reversion"] × (new_fundamental - current_price)` | `extras.mean_reversion: 0.005`                                                                                                            |
| ε(t)               | `noise = random.gauss(0, extras["noise_std"])`                                                               | `extras.noise_std: 0.3`                                                                                                                   |

**Additional mechanisms** (source: `simulation-bases.md §3.2`):
- Short-selling cost → applied in `BaseInvestor._apply_constraints()` via `short_cost_sensitivity` and `short_cost_rate`
- Margin call → `LeveragedBuyer.decide()` priority check
- Price floor → `new_price = max(1.0, ...)` in `Market.decide()`

**Deviations from `simulation-bases.md` design**: None. All mechanisms implemented as specified.

---

## 4. Variant-Specific Features

The Rule variant is the **baseline** — it has no LLM, no RAG, no hybrid logic. Its distinguishing features are (per `simulation-bases.md §9`):

1. **Full Determinism**: With the same `random.gauss` seed, every run produces identical output. This enables strict reproducibility for parameter calibration and cross-variant comparison.

2. **No inference latency**: Every round completes in milliseconds; 100-round simulation runs in under 1 second.

3. **Exact formula fidelity**: MomentumSpeculator uses exactly the formula from `simulation-bases.md §4` — no approximation, no natural language interpretation.

4. **Direct parameter traceability**: Every number in every decision can be traced back to a `players.yml` `extras` key, which has a source citation comment in the config file.

5. **Six distinct investor types** (vs. 5 in LLM variants): Rule variant includes `ConservativeHolder` as a 6th type that is dropped from LLM variants for prompt economy.

---

## 5. Architecture Diagram

```
                    ┌──────────────────────────────────────────────────┐
                    │              AssetBubble Rule Architecture        │
                    └──────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────────────────┐
   │                         Market (Coordinator)                                 │
   │                                                                              │
   │   Price Formula (simulation-bases.md §3.1):                                  │
   │   P(t+1) = P(t) + 0.15×D(t) + 0.005×[F(t)−P(t)] + N(0, 0.3)               │
   │                                                                              │
   │   Broadcast → {price, fundamental, bubble_ratio, volume, net_demand, ...}   │
   └──────────────────────────┬───────────────────────────────────────────────────┘
                              │ market_data (each round)
          ┌───────────────────┼─────────────────────────────────────────────────┐
          ▼                   ▼              ▼              ▼                    ▼
   ┌─────────────┐  ┌──────────────────┐  ┌────────────┐  ┌────────────────┐  ┌───────────────────┐
   │ Momentum    │  │ Rational         │  │ Noise      │  │ Fundamental    │  │ Leveraged  │ Conserv.│
   │ Speculator  │  │ Arbitrageur      │  │ Trader     │  │ Investor       │  │ Buyer      │ Holder  │
   │ ×5          │  │ ×3               │  │ ×2         │  │ ×4             │  │ ×3         │ ×1      │
   │ (destab.)   │  │ (weak stab.)     │  │ (destab.)  │  │ (weak stab.)   │  │ (destab.)  │ (stable)│
   │             │  │                  │  │            │  │                │  │            │         │
   │ formula:    │  │ formula:         │  │ formula:   │  │ formula:       │  │ formula:   │ formula:│
   │ momentum MA │  │ deviation +      │  │ random +   │  │ value         │  │ equity     │ target  │
   │ > threshold │  │ cost penalty     │  │ herding    │  │ deviation      │  │ ratio +    │ rebal.  │
   └──────┬──────┘  └────────┬─────────┘  └─────┬──────┘  └──────┬─────────┘  └─────┬──────┘ └──┬──┘
          │                  │                   │                │                   │            │
          └──────────────────┴───────────────────┴────────────────┴───────────────────┴────────────┘
                                          │ orders: {bid_price, quantity, strategy}
                                          ▼
                               Market.perceive() collects orders
                               Market.decide() applies price formula
                               Cycle repeats each round
```

**Total Agents**: 1 Market + 18 Investors = 19 agents (per `simulation-bases.md §5`)

---

## 6. Configuration Reference

Key parameters from `configs/AssetBubble/Rule/players.yml`:

| Parameter               | Config Path                              | Value | Design Justification (source: `simulation-bases.md §6`)            |
|-------------------------|------------------------------------------|-------|--------------------------------------------------------------------|
| `price_impact`          | `market.extras.price_impact`             | 0.15  | High λ for bubble-prone dynamics; De Long et al. (1990)            |
| `mean_reversion`        | `market.extras.mean_reversion`           | 0.005 | Very low γ allows sustained deviation; Abreu & Brunnermeier (2003) |
| `fundamental_growth`    | `market.extras.fundamental_growth`       | 0.001 | 0.1%/round slow growth; ~10% annual                                |
| `noise_std`             | `market.extras.noise_std`                | 0.3   | Realistic price noise; calibrated to daily equity volatility       |
| `short_cost_rate`       | `market.extras.short_cost_rate`          | 0.02  | 2% borrowing cost; limits arbitrage (Shleifer & Vishny, 1997)      |
| `lookback_short`        | `momentum.extras.lookback_short`         | 5     | 5-round MA window; standard short-term momentum                    |
| `aggressiveness`        | `momentum.extras.aggressiveness`         | 2.0   | Aggressive trading to drive bubble formation                       |
| `leverage_multiplier`   | `momentum.extras.leverage_multiplier`    | 2.0   | 2× leverage on momentum trades                                     |
| `deviation_threshold`   | `arbitrageur.extras.deviation_threshold` | 0.05  | 5% mispricing required to trigger arbitrage                        |
| `max_short_position`    | `arbitrageur.extras.max_short_position`  | 30.0  | Hard short cap; limits corrective force                            |
| `sentiment_volatility`  | `noise.extras.sentiment_volatility`      | 0.3   | Noise trader sentiment variance                                    |
| `herding_weight`        | `noise.extras.herding_weight`            | 0.7   | 70% crowd-following component                                      |
| `trade_frequency`       | `fundamental.extras.trade_frequency`     | 5     | Acts every 5 rounds; patient value investor                        |
| `leverage_ratio`        | `leveraged.extras.leverage_ratio`        | 3.0   | 3× leverage; amplifies bubble and crash                            |
| `margin_call_threshold` | `leveraged.extras.margin_call_threshold` | 0.7   | 70% equity floor triggers forced deleveraging                      |

---

## 7. Running Instructions

```
Execution:
  python examples/AssetBubble/Rule/run_bubble.py \
      -c configs/AssetBubble/Rule/simulation.yml

Required environment variables: None (Rule variant has no LLM calls)

Expected runtime: < 5 seconds for 100 rounds (pure Python, no API calls)
Output location:  EXPERIMENT/AssetBubble/Rule/
```

---

## 8. Expected Behavior Patterns

| Phase        | Rounds | Expected Agent Behavior                                                                                                                                     | Expected Price Dynamics                                                  |
|--------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Build-up     | 1–20   | MomentumSpeculator starts buying as price drifts up; LeveragedBuyer follows; NoiseTrader occasionally buys                                                  | Price rises 5–15% above fundamental; bubble_ratio reaches ~1.1×          |
| Escalation   | 20–50  | MomentumSpeculator buys aggressively; LeveragedBuyer amplifies; RationalArbitrageur starts shorting (constrained); FundamentalInvestor begins slow selling  | Rapid price rise; bubble_ratio reaches 1.3–1.8×; volume spikes           |
| Peak & Crash | 50–70  | LeveragedBuyer equity falls below margin threshold → forced selling; MomentumSpeculator detects reversal → panic selling; RationalArbitrageur covers shorts | Rapid price decline 20–50% from peak; volatility spikes                  |
| Resolution   | 70–100 | All agents reduce activity; FundamentalInvestor may buy if undervalued; NoiseTrader quiets                                                                  | Price stabilizes near or below fundamental; volume returns to low levels |

---

## 9. References

> This variant uses only theories defined in `simulation-bases.md §2`. No variant-specific references.

- Greater Fool Theory → `simulation-bases.md §2`, `§4 — MomentumSpeculator`
- Limits to Arbitrage → `simulation-bases.md §2`, `§4 — RationalArbitrageur`
- Noise Trader Risk → `simulation-bases.md §2`, `§4 — NoiseTrader`
- Synchronization Risk / Forced Deleveraging → `simulation-bases.md §2`, `§4 — LeveragedBuyer`
- Historical calibration targets → `simulation-bases.md §8`
- Parameter source citations → `simulation-bases.md §6`
