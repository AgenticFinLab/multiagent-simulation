# CarryTradeUnwind Rule Variant — Design Specification

## §1 Overview

| Item               | Detail                                                                                                                                                                                      |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Carry trade unwind: sudden risk-off events trigger rapid appreciation of low-yield funding currencies (JPY/CHF), forcing leveraged carry traders to close positions and amplifying the move |
| **Variant**        | Rule — fully deterministic algorithmic agents, no LLM calls                                                                                                                                 |
| **Rounds**         | 200 (configurable)                                                                                                                                                                          |
| **Market**         | FX exchange rate with net-demand + mean-reversion dynamics                                                                                                                                  |
| **Key Feature**    | Leveraged forced-exit cascade → crash → partial stabilization                                                                                                                               |
| **Academic Basis** | Brunnermeier, Nagel & Pedersen (2009); Plantin & Shin (2018); Menkhoff et al. (2012)                                                                                                        |

---

## §2 Theory → Implementation Mapping

### §2.1 CarryTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Carry-premium accumulation from simulation-bases.md §4.1.4 | `CarryTrader.decide()` buys when deviation > +0.02 and sells when deviation < -0.02. |
| Quantity model from simulation-bases.md §4.1.4.3 | Uses `min(int(800 * leverage), int(abs(deviation) * 5000))`; `leverage` is loaded from `extras["leverage"]`. |

### §2.2 LeveragedCarryFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Stop-loss liquidation from simulation-bases.md §4.2.4 | `LeveragedCarryFund.decide()` sells when deviation < -`stop_loss` or the negative-deviation margin-call branch fires. |
| Forced-sell capacity from simulation-bases.md §4.2.4.3 | Quantity is `min(int(800 * leverage), position)`, making this the dominant cascade amplifier. |

### §2.3 FundingCurrencyBuyer (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Safe-haven counterflow from simulation-bases.md §4.3.4 | `FundingCurrencyBuyer.decide()` buys when deviation < -`risk_threshold` and sells when deviation > +`risk_threshold`. |
| Stabilizer capacity from simulation-bases.md §6 | `position_size` is loaded from config and bounds each stabilizing order. |

### §2.4 HedgedCarryTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Volatility-managed carry from simulation-bases.md §4.4.4 | `HedgedCarryTrader.decide()` computes rolling volatility from `price_history` and trades only when the deviation/volatility branch is active. |
| Hedge-ratio sizing from simulation-bases.md §4.4.4.3 | Uses `adj_qty = int(500 * (1 - hedge_ratio))`, with `hedge_ratio` loaded from config. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background FX order flow from simulation-bases.md §4.5.4 | `NoiseTrader.decide()` trades with `trade_probability` and random side/size to provide non-carry liquidity. |
| Bounded liquidity order from simulation-bases.md §6 | Order size is drawn from 100-500 and then constrained by cash or current position. |

---

## §3 Market Mechanism

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

## §4 Variant-Specific Features

The **Rule** variant is the algorithmic baseline. All agent decisions are
deterministic given the same `deviation` value:

| Agent | Role | Trigger | Quantity |
|---|---|---|---|
| `CarryTrader` | Destabilizing | `abs(deviation) > 0.02` | `min(800 * leverage, abs(deviation) * 5000)` |
| `LeveragedCarryFund` | Destabilizing | `deviation < -stop_loss` or negative margin-call branch | `min(800 * leverage, position)` |
| `FundingCurrencyBuyer` | Stabilizing | `abs(deviation) > risk_threshold` | `position_size` |
| `HedgedCarryTrader` | Stabilizing | deviation and rolling-volatility condition | `500 * (1 - hedge_ratio)` |
| `NoiseTrader` | Neutral | random participation at `trade_probability` | random 100-500, constrained by cash/position |

---

## §5 Architecture Diagram

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

## §6 Configuration Reference

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

## §7 Running Instructions

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

## §8 Expected Behavior

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

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Carry trade borrowing / crash dynamics → `simulation-bases.md §2.1, §4 — CarryTrader, LeveragedCarryFund`
- Speculative dynamics / forced unwind → `simulation-bases.md §2.2, §4 — LeveragedCarryFund`
- Volatility-managed carry → `simulation-bases.md §2.3, §4 — HedgedCarryTrader`
- Safe-haven demand → `simulation-bases.md §2.4, §4 — FundingCurrencyBuyer`
- Noise trader theory → `simulation-bases.md §2.5, §4 — NoiseTrader`
- Price formula (FX rate) → `simulation-bases.md §3.1`
- Full parameter table with source citations → `simulation-bases.md §6`
