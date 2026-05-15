# CarryTradeUnwind Rule Variant — Design Specification

## 1. Overview

| Item               | Detail                                                                                                                                                                                      |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Carry trade unwind: sudden risk-off events trigger rapid appreciation of low-yield funding currencies (JPY/CHF), forcing leveraged carry traders to close positions and amplifying the move |
| **Variant**        | Rule — fully deterministic algorithmic agents, no LLM calls                                                                                                                                 |
| **Rounds**         | 200 (configurable)                                                                                                                                                                          |
| **Market**         | FX exchange rate with net-demand + mean-reversion dynamics                                                                                                                                  |
| **Key Feature**    | Leveraged forced-exit cascade → crash → partial stabilization                                                                                                                               |
| **Academic Basis** | Brunnermeier, Nagel & Pedersen (2009); Plantin & Shin (2018); Menkhoff et al. (2012)                                                                                                        |

---

## 2. Theory → Implementation Mapping

| Theoretical Concept                               | Agent / Mechanism                                              | Code Location                                    |
|---------------------------------------------------|----------------------------------------------------------------|--------------------------------------------------|
| Carry trade borrowing (Brunnermeier et al., 2009) | `CarryTrader` — buys high-yield when deviation > 0.02          | `Rule/players.py: CarryTrader.decide()`          |
| Forced unwinding under leverage                   | `LeveragedCarryFund` — forced sell when deviation < −stop_loss | `Rule/players.py: LeveragedCarryFund.decide()`   |
| Safe-haven demand (Menkhoff et al., 2012)         | `FundingCurrencyBuyer` — buys when deviation < −risk_threshold | `Rule/players.py: FundingCurrencyBuyer.decide()` |
| Volatility-managed carry (Plantin & Shin, 2018)   | `HedgedCarryTrader` — reduces qty when vol > vol_threshold     | `Rule/players.py: HedgedCarryTrader.decide()`    |
| Noise trader liquidity (Black, 1986)              | `NoiseTrader` — random Uniform[100, 500]                       | `Rule/players.py: NoiseTrader.decide()`          |
| Price impact + mean reversion                     | Market clearing formula                                        | `Rule/players.py: Market.perceive()`             |

---

## 3. Market Mechanism

### 3.1 Price Update Formula

```
P(t+1) = P(t) + λ·D(t) + γ·(F − P(t)) + ε(t)
```

| Symbol | Parameter                       | Value               |
|--------|---------------------------------|---------------------|
| λ      | `price_impact`                  | 0.02                |
| D(t)   | net_demand = buy_vol − sell_vol | computed each round |
| γ      | `mean_reversion`                | 0.02                |
| F      | `fundamental_value`             | 1.20 (USDJPY)       |
| ε(t)   | noise ~ N(0, noise_std)         | noise_std = 0.02    |

### 3.2 Market Broadcast

Each round the Market agent broadcasts to all traders:

```python
{
    "price":       float,   # current FX rate
    "fundamental": float,   # PPP fundamental (constant)
    "deviation":   float,   # (price - fundamental) / fundamental
    "round":       int,
}
```

> Note: `return_pct` is **NOT** broadcast. All agent rules use only `deviation`.

### 3.3 Deviation Definition

```
deviation = (price − fundamental) / fundamental
```

- Positive: funding currency undervalued → carry trade profitable
- Negative: funding currency appreciated → carry trade losing

---

## 4. Variant-Specific Features

The **Rule** variant is the algorithmic baseline. All agent decisions are
deterministic given the same `deviation` value:

| Agent                  | Role          | Trigger                  | Quantity               |
|------------------------|---------------|--------------------------|------------------------|
| `CarryTrader`          | Destabilizing | `                        | deviation              |
| `LeveragedCarryFund`   | Destabilizing | `dev < −0.03 OR (        | dev                    |
| `FundingCurrencyBuyer` | Stabilizing   | `dev < −0.05`            | 500                    |
| `HedgedCarryTrader`    | Stabilizing   | `dev > 0 AND vol < 0.05` | 350 (hedge_ratio=0.30) |
| `NoiseTrader`          | Neutral       | p=0.30                   | Uniform[100, 500]      |

---

## 5. Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   Market (FX)                        │
│  price = P(t) + λ·D + γ·(F−P) + ε                  │
│  broadcasts: {price, fundamental, deviation, round}  │
└──────────────────────┬──────────────────────────────┘
                       │  market_update (star topology)
          ┌────────────┼────────────────┐
          │            │                │
    ┌─────▼──────┐ ┌──▼─────────┐ ┌───▼──────────────┐
    │CarryTrader │ │Leveraged   │ │FundingCurrency   │
    │(dest.)×2   │ │CarryFund×2 │ │Buyer×2 (stab.)   │
    │lev=5.0     │ │forced exit │ │risk_thr=0.05     │
    └────────────┘ └────────────┘ └──────────────────┘
          │            │                │
    ┌─────▼──────┐ ┌──▼─────────┐
    │Hedged      │ │NoiseTrader │
    │CarryTrader │ │×2 (neutral)│
    │(stab.)×1   │ │p=0.30      │
    └────────────┘ └────────────┘
          │   all agents send order → Market
```

---

## 6. Configuration Reference

From `configs/CarryTradeUnwind/Rule/players.yml`:

### Market

| Parameter           | Value | Description        |
|---------------------|-------|--------------------|
| `initial_price`     | 1.20  | Starting FX rate   |
| `fundamental_value` | 1.20  | PPP fundamental    |
| `price_impact`      | 0.02  | λ in price formula |
| `mean_reversion`    | 0.02  | γ in price formula |
| `noise_std`         | 0.02  | ε std deviation    |

### CarryTrader

| Parameter          | Value  | Description         |
|--------------------|--------|---------------------|
| `leverage`         | 5.0    | Position multiplier |
| `initial_cash`     | 100000 | Starting cash       |
| `initial_position` | 0      | Starting holdings   |

### LeveragedCarryFund

| Parameter   | Value | Description                |
|-------------|-------|----------------------------|
| `leverage`  | 5.0   | Forced-exit multiplier     |
| `stop_loss` | 0.03  | Crisis deviation threshold |

### FundingCurrencyBuyer

| Parameter        | Value | Description      |
|------------------|-------|------------------|
| `risk_threshold` | 0.05  | Buy trigger      |
| `position_size`  | 500   | Fixed order size |

### HedgedCarryTrader

| Parameter       | Value | Description        |
|-----------------|-------|--------------------|
| `hedge_ratio`   | 0.30  | Fraction hedged    |
| `vol_threshold` | 0.05  | High-vol cutoff    |
| `adj_qty`       | 350   | = 500 × (1 − 0.30) |

### NoiseTrader

| Parameter           | Value | Description      |
|---------------------|-------|------------------|
| `trade_probability` | 0.30  | Trade each round |

---

## 7. Running Instructions

```bash
# Run simulation
python examples/CarryTradeUnwind/Rule/run_carrytradeunwind_rule.py \
    -c configs/CarryTradeUnwind/Rule/simulation.yml

# Analyze results
python examples/CarryTradeUnwind/Rule/analysis.py \
    -c configs/CarryTradeUnwind/Rule/simulation.yml
```

Output: `EXPERIMENT/CarryTradeUnwind/Rule/records/`

---

## 8. Expected Behavior

### Phase 1: Carry Accumulation (rounds 1–N)

- Prices drift above fundamental (positive deviation)
- CarryTrader and HedgedCarryTrader buy — reinforce above-fundamental price
- LeveragedCarryFund builds long positions

### Phase 2: Trigger and Cascade (sharp onset)

- Noise or reversion pushes deviation below −0.03
- LeveragedCarryFund forced-exit triggers → large sell pressure
- Price drops further → more forced exits (cascade mechanism)
- Deviation reaches −5% to −15% range

### Phase 3: Stabilization

- FundingCurrencyBuyer activates at deviation < −0.05
- Mean-reversion force γ·(F−P) pulls price back
- HedgedCarryTrader reduces exposure (vol > 0.05)
- recovery_ratio > 0.5 indicates partial stabilization

---

## 9. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Carry trade borrowing / crash dynamics → `simulation-bases.md §2.1, §4 — CarryTrader, LeveragedCarryFund`
- Speculative dynamics / forced unwind → `simulation-bases.md §2.2, §4 — LeveragedCarryFund`
- Volatility-managed carry → `simulation-bases.md §2.3, §4 — HedgedCarryTrader`
- Safe-haven demand → `simulation-bases.md §2.4, §4 — FundingCurrencyBuyer`
- Noise trader theory → `simulation-bases.md §2.5, §4 — NoiseTrader`
- Price formula (FX rate) → `simulation-bases.md §3.1`
- Full parameter table with source citations → `simulation-bases.md §6`
